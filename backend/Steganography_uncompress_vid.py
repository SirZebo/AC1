import cv2
import numpy as np
import os
import subprocess
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor

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

from tempfile import TemporaryDirectory
import shutil

def extract_audio(video_path):
    """Extract audio from video and save as a temporary WAV file."""
    with TemporaryDirectory() as tmpdirname:
        tmp_audio = os.path.join(tmpdirname, "audio.wav")
        subprocess.call(['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', tmp_audio, '-y'])
        # Copy out of the temporary directory to a permanent location
        permanent_audio_path = os.path.join("./", "audio.wav")
        shutil.copy(tmp_audio, permanent_audio_path)
    return permanent_audio_path


def encode_video_with_audio(secret_file, cover_video_path, bits_per_pixel):
    cap = cv2.VideoCapture(cover_video_path)
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'HFYU')  # Using HUFFYUV lossless codec
    
    output_video_path = "stego_video.avi"  # Changed file extension to .avi for compatibility with lossless codecs
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height), isColor=True)


    with open(secret_file, "rb") as file:
        secret_data = file.read()
    binary_secret_data = to_bin(secret_data) + to_bin("=====")
    data_index = 0
    data_len = len(binary_secret_data)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                if data_index + bits_per_pixel <= data_len:
                    pixel = frame[i, j]
                    for k in range(3): # for each color channel
                        binary_pixel = to_bin(pixel[k])
                        new_pixel = binary_pixel[:8-bits_per_pixel] + binary_secret_data[data_index:data_index+bits_per_pixel]
                        pixel[k] = int(new_pixel, 2)
                        data_index += bits_per_pixel
                if data_index >= data_len:
                    break
            if data_index >= data_len:
                break

        out.write(frame)
        if data_index >= data_len:
            break

    # Finish processing the rest of the video frames if there's more to do
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    # Release all resources
    cap.release()
    out.release()

    # Reattach the audio
    tmp_audio = extract_audio(cover_video_path)
    if os.path.exists(tmp_audio):
        final_video_path = "stego_video_with_audio.avi"  # Ensure the output format supports the codec
        subprocess.call(['ffmpeg', '-i', output_video_path, '-i', tmp_audio, '-c:v', 'copy', '-c:a', 'pcm_s16le', '-strict', '-2', final_video_path, '-y'])
        os.remove(output_video_path)  # Clean up the video without audio
        os.rename(final_video_path, output_video_path)
        os.remove(tmp_audio)

    print(f"[+] Stego video created: {output_video_path}")



def process_frame(frame, bits_per_pixel, binary_data):
    """Process a single frame to extract binary data."""
    local_binary_data = []
    for i in range(0, frame.shape[0], 10):  # Sample every 10th row to reduce data
        for j in range(0, frame.shape[1], 10):  # Sample every 10th column
            for color in frame[i, j]:
                binary_color = to_bin(color)
                local_binary_data.append(binary_color[-bits_per_pixel:])
    return ''.join(local_binary_data)

def decode_video(video_path, bits_per_pixel):
    print("[+] Decoding...")
    cap = cv2.VideoCapture(video_path)
    binary_data = ""
    delimiter = to_bin("=====")

    with ThreadPoolExecutor() as executor:
        futures = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Process each frame in a separate thread
            futures.append(executor.submit(process_frame, frame, bits_per_pixel, binary_data))

        # Consolidate results from all threads
        for future in futures:
            binary_data += future.result()
            # Check for delimiter and break if found
            if delimiter in binary_data:
                binary_data = binary_data[:binary_data.find(delimiter)]
                break

    cap.release()

    # Convert binary data to bytes
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = bytes([int(byte, 2) for byte in all_bytes])

    # Detect file type and save output
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
encode_video_with_audio("secret.zip", "cover_video.mp4", 2)
decode_video("stego_video.avi", 2)