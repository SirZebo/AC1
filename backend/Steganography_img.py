import cv2
import numpy as np
import threading


def to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        return ''.join([format(byte, "08b") for byte in data])
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def encode(secret_file, cover_image_path, bits_per_pixel):
    image = cv2.imread(cover_image_path)
    if image is None:
        raise FileNotFoundError("Cover image not found.")
    
    with open(secret_file, "rb") as file:
        secret_data = file.read()

    binary_secret_data = to_bin(secret_data) + to_bin("=====")
    n_bits = image.shape[0] * image.shape[1] * 3 * bits_per_pixel
    if len(binary_secret_data) > n_bits:
        raise ValueError("Insufficient bytes, need bigger image or less data.")

    data_index = 0
    data_len = len(binary_secret_data)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if data_index + bits_per_pixel <= data_len:
                pixel = image[i, j]
                for k in range(3):  # for each color channel
                    binary_pixel = to_bin(pixel[k])
                    new_pixel = binary_pixel[:8-bits_per_pixel] + binary_secret_data[data_index:data_index+bits_per_pixel]
                    pixel[k] = int(new_pixel, 2)
                    data_index += bits_per_pixel
            if data_index >= data_len:
                break
        if data_index >= data_len:
            break

    return image


def thread_decode(start_row, end_row, image, bits_per_pixel, output, lock):
    binary_data = ""
    delimiter = to_bin("=====")
    for row in image[start_row:end_row]:
        for pixel in row:
            for color in pixel:
                binary_color = to_bin(color)
                binary_data += binary_color[-bits_per_pixel:]
                # Check if the last 'n' bits contain the delimiter
                if binary_data[-len(delimiter):] == delimiter:
                    binary_data = binary_data[:binary_data.find(delimiter)]
                    with lock:
                        output.append(binary_data)
                    return  # Exit as soon as the delimiter is found

def decode(image_path, bits_per_pixel, n_threads=4):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError("Image not found for decoding.")

    rows_per_thread = image.shape[0] // n_threads
    threads = []
    output = []
    lock = threading.Lock()

    for i in range(n_threads):
        start_row = i * rows_per_thread
        end_row = (i + 1) * rows_per_thread if i != n_threads - 1 else image.shape[0]
        thread = threading.Thread(target=thread_decode, args=(start_row, end_row, image, bits_per_pixel, output, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Combine data from all threads
    binary_data = ''.join(output)

    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = bytes([int(byte, 2) for byte in all_bytes])

    # File type detection and saving to file as shown in the original function
    file_signature = {
        b'\x50\x4B\x03\x04': 'ZIP',
        b'\xFF\xD8\xFF': 'JPEG',
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'PNG',
        b'\x25\x50\x44\x46': 'PDF'
    }

    output_file = "extracted_secret.bin"
    for signature, extension in file_signature.items():
        if decoded_data.startswith(signature):
            output_file = f"extracted_secret.{extension.lower()}"
            break

    with open(output_file, "wb") as file:
        file.write(decoded_data)
    print("[+] Data extracted and saved as", output_file)

# Example usage:
encoded_image = encode("secret.zip", "cover_image.jpg", 2)
cv2.imwrite("stego_image.png", encoded_image)
decode("stego_image.png", 2)