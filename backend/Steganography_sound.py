import subprocess
import wave
import os
from tempfile import TemporaryDirectory

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

def convert_to_wav(input_audio_path):
    """Convert an audio file to WAV format using ffmpeg."""
    output_audio_path = os.path.splitext(input_audio_path)[0] + ".wav"
    subprocess.run(['ffmpeg', '-i', input_audio_path, output_audio_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_audio_path

def encode_audio(secret_file, cover_audio_path, bits_per_sample):
    # Convert cover audio to WAV if necessary
    if not cover_audio_path.endswith(".wav"):
        cover_audio_path = convert_to_wav(cover_audio_path)

    # Open cover audio
    with wave.open(cover_audio_path, 'rb') as cover_audio:
        n_frames = cover_audio.getnframes()
        frames = cover_audio.readframes(n_frames)
        frame_bytes = bytearray(frames)

    # Embed secret data
    with open(secret_file, "rb") as file:
        secret_data = file.read()
    binary_secret_data = to_bin(secret_data) + to_bin("=====")
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

    # Write the modified bytes back
    with wave.open('stego_sound.wav', 'wb') as modified_audio:
        modified_audio.setparams(cover_audio.getparams())
        modified_audio.writeframes(frame_bytes)

    print(f"[+] Stego audio created: stego_sound.wav")

def decode_audio(audio_path, bits_per_sample):
    print("[+] Decoding...")
    with wave.open(audio_path, 'rb') as stego_audio:
        n_frames = stego_audio.getnframes()
        frames = stego_audio.readframes(n_frames)
        frame_bytes = bytearray(frames)

    binary_data = ""
    for byte in frame_bytes:
        binary_data += to_bin(byte)[-bits_per_sample:]

    # Find the delimiter
    delimiter = to_bin("=====")
    data_end = binary_data.find(delimiter)
    if data_end != -1:
        binary_data = binary_data[:data_end]

    # Convert binary data to bytes
    output_bytes = bytes([int(binary_data[i: i+8], 2) for i in range(0, len(binary_data), 8)])

    # File type detection
    file_signature = {
        b'\x50\x4B\x03\x04': 'zip',
        b'\xFF\xD8\xFF': 'jpeg',
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'png',
        b'\x25\x50\x44\x46': 'pdf',
        b'\x49\x44\x33': 'mp3',
        b'\x42\x4D': 'bmp',
        b'\x47\x49\x46\x38': 'gif'
    }

    output_file = "extracted_secret.txt"  # Default to .txt if no match found
    for signature, extension in file_signature.items():
        if output_bytes.startswith(signature):
            output_file = f"extracted_secret.{extension}"
            break

    with open(output_file, "wb") as file:
        file.write(output_bytes)
    
    print(f"[+] Data extracted and saved as {output_file}")

# Example usage:
encode_audio("secret.txt", "cover_audio.mp3", 2)
decode_audio("stego_sound.wav", 2)
