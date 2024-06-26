import wave
import os
from tempfile import TemporaryDirectory
import shutil
import zipfile
from backend.zip import unzipSecretFile

import numpy as np
import threading
from pydub import AudioSegment

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

def encode_audio(secret_file, cover_audio_path, bits_per_sample):
    print("[+] Encoding audio...")

    # Determine the file extension and read the cover audio
    file_extension = cover_audio_path.split('.')[-1].lower()
    if file_extension in ['wav', 'mp3', 'mp4']:
        cover_audio = AudioSegment.from_file(cover_audio_path)
    else:
        raise ValueError("Unsupported audio format")

    # Get the frame bytes
    frame_bytes = bytearray(cover_audio.raw_data)

    # Embed secret data
    with open(secret_file, "rb") as file:
        secret_data = file.read()
    binary_secret_data = to_bin(secret_data) + to_bin("=====")
    
    available_space_bits = len(frame_bytes) * bits_per_sample
    required_space_bits = len(binary_secret_data)

    if required_space_bits > available_space_bits:
        available_space_bytes = available_space_bits // 8
        required_space_bytes = required_space_bits // 8
        current_payload_size = len(secret_data)
        raise ValueError(
            f"Insufficient bytes, need bigger audio file or less data. "
            f"Available space: {available_space_bytes} bytes, "
            f"Required space: {required_space_bytes} bytes, "
            f"Current payload size: {current_payload_size} bytes."
        )

    data_index = 0
    data_len = len(binary_secret_data)

    # Modify bytes of the audio data
    for i in range(len(frame_bytes)):
        if data_index + bits_per_sample <= data_len:
            frame_part = frame_bytes[i:i+1]
            binary_frame = to_bin(frame_part[0])
            new_frame = binary_frame[:8-bits_per_sample] + binary_secret_data[data_index:data_index+bits_per_sample]
            frame_bytes[i] = int(new_frame, 2)
            data_index += bits_per_sample
        if data_index >= data_len:
            break

    # Convert bytearray back to audio
    modified_audio = cover_audio._spawn(frame_bytes)

    parent_directory = os.path.dirname(os.path.dirname(__file__))
    audio_file_name = os.path.basename(cover_audio_path)
    file_name, _ = os.path.splitext(audio_file_name)  # Split file name and extension
    save_path = os.path.join(parent_directory, "Media/Steganography", f"{file_name}.wav")

    # Export modified audio
    modified_audio.export(save_path, format='wav')
    print(f"[+] Stego audio created: {save_path}")
    return save_path

def thread_decode_audio(frame_segment, bits_per_sample, output, lock, delimiter):
    binary_data = ""
    for byte in frame_segment:
        binary_data += to_bin(byte)[-bits_per_sample:]
        # Check if the last 'n' bits contain the delimiter
        if binary_data[-len(delimiter):] == delimiter:
            with lock:
                output.append(binary_data[:binary_data.find(delimiter)])
            return  # Exit as soon as the delimiter is found

def decode_audio(audio_path, bits_per_sample, n_threads=4):
    print("[+] Decoding audio...")
    # print(audio_path)

    with wave.open(audio_path, 'rb') as stego_audio:
        n_frames = stego_audio.getnframes()
        frames = stego_audio.readframes(n_frames)
        frame_bytes = bytearray(frames)

    # Prepare threading
    bytes_per_thread = len(frame_bytes) // n_threads
    threads = []
    output = []
    lock = threading.Lock()
    delimiter = to_bin("=====")

    for i in range(n_threads):
        start_index = i * bytes_per_thread
        end_index = (i + 1) * bytes_per_thread if i != n_threads - 1 else len(frame_bytes)
        frame_segment = frame_bytes[start_index:end_index]
        thread = threading.Thread(target=thread_decode_audio, args=(frame_segment, bits_per_sample, output, lock, delimiter))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Combine data from all threads
    binary_data = ''.join(output)

    # Convert binary data to bytes
    output_bytes = bytes([int(binary_data[i: i+8], 2) for i in range(0, len(binary_data), 8)])

    # File type detection and saving
    file_signature = {
        b'\x50\x4B\x03\x04': 'zip',
    }

    parent_directory = os.path.dirname(os.path.dirname(__file__))
    audio_file_name = os.path.basename(audio_path)
    file_name, _ = os.path.splitext(audio_file_name)  # Split file name and extension
    save_path = os.path.join(parent_directory, "Media/Steganalysis", file_name)

    output_file = f"{save_path}.txt"  # Default to .txt if no match found
    
    for signature, extension in file_signature.items():
        if output_bytes.startswith(signature):
            output_file = f"{save_path}.{extension}"
            break

    with open(output_file, "wb") as file:
        file.write(output_bytes)
    
    print(f"[+] Data extracted and saved as {output_file}")

    result = None
    if output_file.endswith(".zip"):
        result = unzipSecretFile(output_file)
    if result is not None:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(output_file):
            os.remove(output_file)
    return result

# Example usage:
# encode_audio("./secret.zip", "./cover_audio.mp3", 6)
# decode_audio("./Media/Steganography/cover_audio.wav", 6)
