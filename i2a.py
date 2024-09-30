import numpy as np
from PIL import Image
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from scipy.io.wavfile import write
import threading

# 多語言支持
LANGUAGES = {
    "English": {
        "title": "Image-Audio Encoder/Decoder",
        "encode_button": "Select Image to Encode",
        "decode_button": "Select Audio to Decode",
        "success_encode": "Image encoded to audio.",
        "success_decode": "Audio decoded back to image.",
        "error_length": "Decoded data length does not match expected length.",
    },
    "中文": {
        "title": "圖片-音頻編碼/解碼器",
        "encode_button": "選擇要編碼的圖片",
        "decode_button": "選擇要解碼的音頻",
        "success_encode": "圖片已編碼為音頻。",
        "success_decode": "音頻已解碼為圖片。",
        "error_length": "解碼數據長度與預期長度不匹配。",
    }
}

current_language = "English"  # 預設語言

def update_text():
    """根據當前語言更新 UI 文本。"""
    title_label.config(text=LANGUAGES[current_language]["title"])
    encode_button.config(text=LANGUAGES[current_language]["encode_button"])
    decode_button.config(text=LANGUAGES[current_language]["decode_button"])

def encode_image_to_audio(image_path, audio_path, progress_var):
    img = Image.open(image_path)
    data = np.array(img)
    height, width, _ = data.shape
    audio_data = data / 255.0 * 2 - 1
    audio_data_flattened = audio_data.flatten()
    size_info = np.array([height, width], dtype=np.int32)
    audio_data_with_size = np.concatenate([size_info, audio_data_flattened])
    
    # 模擬編碼過程並更新進度條
    for i in range(0, len(audio_data_with_size), 1000):
        progress_var.set(min(i / len(audio_data_with_size), 1.0))  # 更新進度
    write(audio_path, 44100, audio_data_with_size.astype(np.float32))
    progress_var.set(1.0)  # 完成

    messagebox.showinfo("Success", LANGUAGES[current_language]["success_encode"])

def decode_audio_to_image(audio_path, image_path, progress_var):
    audio_data, sample_rate = sf.read(audio_path)
    height = int(audio_data[0])
    width = int(audio_data[1])
    data = audio_data[2:]
    expected_length = height * width * 3

    if len(data) != expected_length:
        messagebox.showerror("Error", LANGUAGES[current_language]["error_length"])
        return

    img_data = ((data + 1) / 2 * 255).astype(np.uint8)
    img_data = img_data.reshape((height, width, 3))
    
    # 模擬解碼過程並更新進度條
    for i in range(0, len(img_data.flatten()), 1000):
        progress_var.set(min(i / len(img_data.flatten()), 1.0))  # 更新進度

    img = Image.fromarray(img_data)
    img.save(image_path)
    progress_var.set(1.0)  # 完成
    messagebox.showinfo("Success", LANGUAGES[current_language]["success_decode"])

def select_image(progress_var):
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if image_path:
        threading.Thread(target=encode_image_to_audio, args=(image_path, 'encoded_audio.wav', progress_var)).start()

def select_audio(progress_var):
    audio_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
    if audio_path:
        threading.Thread(target=decode_audio_to_image, args=(audio_path, 'decoded_image.png', progress_var)).start()

# UI 設計
root = tk.Tk()
root.title("Image-Audio Encoder/Decoder")
root.geometry("400x350")
root.configure(bg="#f0f0f0")

# 標題標籤
title_label = ttk.Label(root, text=LANGUAGES[current_language]["title"], font=("Helvetica", 16), background="#f0f0f0")
title_label.pack(pady=10)

# 進度條
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=1.0, length=300)
progress_bar.pack(pady=20)

# 編碼按鈕
encode_button = ttk.Button(root, text=LANGUAGES[current_language]["encode_button"], command=lambda: select_image(progress_var))
encode_button.pack(pady=10, padx=20, fill='x')

# 解碼按鈕
decode_button = ttk.Button(root, text=LANGUAGES[current_language]["decode_button"], command=lambda: select_audio(progress_var))
decode_button.pack(pady=10, padx=20, fill='x')

# 語言選擇下拉選單
language_var = tk.StringVar(value=current_language)
language_menu = ttk.Combobox(root, textvariable=language_var, values=list(LANGUAGES.keys()), state='readonly')
language_menu.pack(pady=10)
language_menu.bind("<<ComboboxSelected>>", lambda event: change_language(language_var.get()))

def change_language(language):
    global current_language
    current_language = language
    update_text()

# 主循環
root.mainloop()

