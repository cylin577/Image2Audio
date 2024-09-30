from concurrent.futures import ThreadPoolExecutor

def decode_audio_to_image(audio_path, image_path, progress_var, lang_dict):
    audio_data, _ = sf.read(audio_path)
    height = int(audio_data[0])
    width = int(audio_data[1])
    data = audio_data[2:]
    expected_length = height * width * 3

    if len(data) != expected_length:
        messagebox.showerror("Error", lang_dict['error_decode'])
        return

    # 使用多線程來並行處理音頻數據
    def process_chunk(chunk):
        return ((chunk + 1) / 2 * 255).astype(np.uint8)
    
    num_threads = 4  # 設置線程數，可以根據CPU核心數調整
    chunk_size = len(data) // num_threads

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_chunk, data[i:i+chunk_size]) for i in range(0, len(data), chunk_size)]
        results = np.concatenate([f.result() for f in futures])

    img_data = results.reshape((height, width, 3))
    img = Image.fromarray(img_data)
    img.save(image_path)
    progress_var.set(1.0)
    messagebox.showinfo("Success", lang_dict['success_decode'])
                   
