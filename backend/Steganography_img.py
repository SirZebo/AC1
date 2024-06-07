import os
import zipfile
import cv2
import numpy as np
import threading
from backend.zip import unzipSecretFile


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
    if (bits_per_pixel != 1 or bits_per_pixel != 2 or bits_per_pixel != 4):
        bits_per_pixel = 4
        
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
    if (bits_per_pixel != 1 or bits_per_pixel != 2 or bits_per_pixel != 4):
        bits_per_pixel = 4
    # Get parent directory
    parent_directory = os.path.dirname(os.path.dirname(__file__))
    file_name = os.path.basename(image_path)
    save_path = os.path.join(parent_directory, "Media/Steganalysis", f"{file_name}")

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

    output_file = f"{save_path}.bin"
    for signature, extension in file_signature.items():
        if decoded_data.startswith(signature):
            output_file = f"{save_path}.{extension.lower()}"
            break

    with open(output_file, "wb") as file:
        file.write(decoded_data)
    print("[+] Data extracted and saved as", output_file)
    
    if output_file.endswith(".zip"):
        return unzipSecretFile(output_file)
    
    # # If the file is a ZIP, read the contents and return text
    # if output_file.endswith(".zip"):
    #     return read_zip_file(output_file)
    # else:
    #     return None
    
    # If the file is a ZIP, read the contents and return text


# def read_zip_file(zip_path):
#     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#         text_data = ""
#         for file_info in zip_ref.infolist():
#             with zip_ref.open(file_info) as file:
#                 if file_info.filename.endswith(".txt"):
#                     text_data += file.read().decode('utf-8') + "\n"
#         return text_data

# Example usage:
# encoded_image = encode("./secret.zip", "./cover_image.jpg",1)
# cv2.imwrite("stego_image.png", encoded_image)
# decode("stego_image.png", 1)