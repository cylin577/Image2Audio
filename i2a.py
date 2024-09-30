import numpy as np
from PIL import Image
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

def encode_image_to_audio(image_path, audio_path, progress_var):
    img = Image.open(image_path)
    data = np.array(img)
    height, width, _ = data.shape
    audio_data = data / 255.0 * 2 - 1
    audio_data_flattened = audio_data.flatten()
    size_info = np.array([height, width], dtype=np.int32)
    audio_data_with_size = np.concatenate([size_info, audio_data_flattened])
    
    for i in range(0, len(audio_data_with_size), 1000):
        progress_var.set(min(i / len(audio_data_with_size), 1.0))
    sf.write(audio_path, audio_data_with_size.astype(np.float32), 44100)
    progress_var.set(1.0)
    messagebox.showinfo("成功", "圖片已編碼為音頻。")

def decode_audio_to_image(audio_path, image_path, progress_var):
    audio_data, sample_rate = sf.read(audio_path)
    height = int(audio_data[0])
    width = int(audio_data[1])
    data = audio_data[2:]
    expected_length = height * width * 3

    if len(data) != expected_length:
        messagebox.showerror("錯誤", f"解碼數據長度 {len(data)} 與預期長度 {expected_length} 不匹配。")
        return

    img_data = ((data + 1) / 2 * 255).astype(np.uint8)
    img_data = img_data.reshape((height, width, 3))

    for i in range(0, len(img_data.flatten()), 1000):
        progress_var.set(min(i / len(img_data.flatten()), 1.0))

    img = Image.fromarray(img_data)
    img.save(image_path)
    progress_var.set(1.0)
    messagebox.showinfo("成功", "音頻已解碼回圖片。")

def select_image(progress_var):
    image_path = filedialog.askopenfilename(filetypes=[("圖片文件", "*.png;*.jpg;*.jpeg;*.bmp")])
    if image_path:
        threading.Thread(target=encode_image_to_audio, args=(image_path, 'encoded_audio.wav', progress_var)).start()

def select_audio(progress_var):
    audio_path = filedialog.askopenfilename(filetypes=[("音頻文件", "*.wav")])
    if audio_path:
        threading.Thread(target=decode_audio_to_image, args=(audio_path, 'decoded_image.png', progress_var)).start()

# UI 設計
root = tk.Tk()
root.title("圖片-音頻 編碼/解碼器")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

title_label = ttk.Label(root, text="圖片-音頻 編碼/解碼器", font=("Helvetica", 16), background="#f0f0f0")
title_label.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=1.0, length=300)
progress_bar.pack(pady=20)

encode_button = ttk.Button(root, text="選擇圖片以編碼", command=lambda: select_image(progress_var))
encode_button.pack(pady=10, padx=20, fill='x')

decode_button = ttk.Button(root, text="選擇音頻以解碼", command=lambda: select_audio(progress_var))
decode_button.pack(pady=10, padx=20, fill='x')

# 主循環
root.mainloop()
