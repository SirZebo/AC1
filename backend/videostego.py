import os
import numpy as np
import cv2 
from numpy import binary_repr
from moviepy.editor import VideoFileClip, ImageSequenceClip
#import os
#import subprocess
from zip import zipSecretFile
from zip import unzipSecretFile


SUPER_SECRET_KEY = "This_is_a_very_secret_key_of_Ambrose_Goh"

def load_secret(fname):
    with open(fname, 'rb') as f:
        data = f.read()
    return data

# def zipSecretFile(inputFile):
#     with ZipFile(ZIPPED_SECRET_FILE_NAME,'w') as zip:
#         print("Zipping secret...")
#         zip.write(inputFile)
#         print("Zipping secret Done!")

# def unzipSecretFile(file_name: str):
#     try:
#         with ZipFile(file_name, 'r') as zip:
#             zip.extractall()
#             print(f"Successfully extracted contents from {file_name}")
#     except FileNotFoundError:
#         print(f"File {file_name} not found")
#     except Exception as e:
#         print(f"Error in unzipping the file: {e}")

#def convert_avi_to_mp4(input_file: str, output_file: str):
#    command = f"ffmpeg -i {input_file} -vcodec libx264 {output_file}"
#    subprocess.run(command, shell=True)

def encode_video(coverMedia: str, secretFile: str, outputFile: str):
    vidcap = cv2.VideoCapture(coverMedia)
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    #temp_avi_file = outputFile.replace(".mp4", ".avi")
    #out = cv2.VideoWriter(temp_avi_file, fourcc, fps, size)
    out = cv2.VideoWriter(outputFile, fourcc, fps, size)

    zipFile_path = zipSecretFile(secretFile)
    secret_bytes = load_secret(zipFile_path) + bytes(SUPER_SECRET_KEY, 'utf-8')
    bits = []
    # As it's assumed you'll be embedding 3 bits in each pixel,
    # we'll split each byte in three triplets.
    for byte in secret_bytes:
        for k in range(6, -1, -3):
            bits.append((byte >> k) & 0x07)

    # Now start reading your video frames and count how many
    # triplets you have embedded so far.
    index = 0
    while True:
        ret, frame = vidcap.read()
        if ret==False:
            print("Bad frame")
            break
        if index < len(bits):
            # Assuming you want to embed in each RGB pixels,
            # you can embed up to `width x height x 3` triplets.
            size = np.prod(frame.shape)
            bit_groups = np.array(bits[index:index+size], dtype=np.uint8)
            # Flatten the frame for quick embedding
            frame_flat = frame.flatten()
            # Embed as many bit groups as necessary
            frame_flat[:len(bit_groups)] = (frame_flat[:len(bit_groups)] & 0b11111000) | bit_groups
            # Reshape it back
            new_frame = np.reshape(frame_flat, frame.shape)
            #writer.writeFrame(new_frame)
            index += size
        else:
            # You can now write `new_frame` to a new video.
            new_frame = frame
        out.write(new_frame)

    
    vidcap.release()
    out.release()
    cv2.destroyAllWindows()

    #convert_avi_to_mp4(temp_avi_file, outputFile)
    #os.remove(temp_avi_file) 
def encode_video_with_audio(input_video_path, payload_file_path, output_video_path, lsb_selected):
    # Read the input video
    video = VideoFileClip(input_video_path)

    # Extract video frames and audio
    frames = []
    for frame in video.iter_frames():
        frames.append(frame)

    audio = video.audio

    # Convert frames to a NumPy array
    frames_array = np.array(frames)
    
    # Read the payload file
    with open(payload_file_path, 'rb') as f:
        payload = f.read()
    
    # Convert the payload to binary
    payload_binary = ''.join(format(byte, '08b') for byte in payload)

    # Embed the payload into the video frames
    payload_index = 0
    for i in range(frames_array.shape[0]):
        for j in range(frames_array.shape[1]):
            for k in range(frames_array.shape[2]):
                for bit in range(lsb_selected):
                    if payload_index < len(payload_binary):
                        frames_array[i, j, k] = (frames_array[i, j, k] & ~1) | int(payload_binary[payload_index])
                        payload_index += 1
    
    # Create a new video clip with the modified frames
    new_video = ImageSequenceClip(list(frames_array), fps=video.fps)
    
    # Set the original audio to the new video
    new_video = new_video.set_audio(audio)
    
    # Write the result video to a file
    new_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
    
# def decode_video(outputFile: str):
    vidcap = cv2.VideoCapture(outputFile)
    bits = []
    
    while True:
        ret, frame = vidcap.read()
        if not ret:
            print("End of video or bad frame")
            break
        
        flat_frame = frame.flatten()
        bits.extend(flat_frame & 0x07)  # Extract 3 LSBs from each pixel
        
    bytestream = bytearray()
    byte_buffer = []
    
    for bit in bits:
        byte_buffer.append(bit)
        if len(byte_buffer) == 8:  # Accumulate 8 bits to form a byte
            byte_val = bits_to_byte(byte_buffer)
            bytestream.append(byte_val)
            byte_buffer = []
            
            # Check if the secret key is found at the end of bytestream
            try:
                if bytestream[-len(SUPER_SECRET_KEY):].decode("utf-8") == SUPER_SECRET_KEY:
                    break
            except UnicodeDecodeError:
                continue

    # Write the extracted bytestream to a file
    with open(ZIPPED_SECRET_FILE_NAME, 'wb') as f:
        f.write(bytestream[:-len(SUPER_SECRET_KEY)])  # Remove the secret key bytes

    # Unzip the secret file
    unzipSecretFile(ZIPPED_SECRET_FILE_NAME)

def bits_to_byte(bits):
    """Convert a list of 8 bits (0 or 1) into a single byte (0-255)."""
    byte_val = 0
    for bit in bits:
        byte_val = (byte_val << 1) | bit
    return byte_val & 0xFF  # Ensure the byte value is within valid range (0-255)


def decode_video(outputFile: str):
    vidcap = cv2.VideoCapture(outputFile)
    bits = []
    while True:
        ret, frame = vidcap.read()
        if ret==False:
            print("Bad frame")
            break
        flat_frame = frame.flatten()
        bits.extend(flat_frame & 0x07)
        # You need to decide how many triplets is enough to extract

    bytestream = b''
    for i in range(0, len(bits), 3):
        bytestream += bytes([(bits[i] << 6) | (bits[i+1] << 3) | bits[i+2]])
        print(bytestream)
        try:
            if bytestream[-len(SUPER_SECRET_KEY):].decode("utf-8") == SUPER_SECRET_KEY:
                break
        except UnicodeDecodeError:
            continue

    # File type detection and saving
    file_signature = {
        b'\x50\x4B\x03\x04': 'zip',
    }
    parent_directory = os.path.dirname(os.path.dirname(__file__))
    video_file_name = os.path.basename(outputFile)
    file_name, _ = os.path.splitext(video_file_name)  # Split file name and extension
    save_path = os.path.join(parent_directory, "Media/Steganalysis", file_name)

    
    for signature, extension in file_signature.items():
            if bytestream.startswith(signature):
                output_file = f"{save_path}.{extension}"
                break

    with open(output_file, "wb") as file:
        file.write(bytestream)
    
    print(f"[+] Data extracted and saved as {output_file}")

    result = None
    if output_file.endswith(".zip"):
        result = unzipSecretFile(output_file)
    # if result is not None:
    #     if os.path.exists(outputFile):
    #         os.remove(outputFile)
    #     if os.path.exists(output_file):
    #         os.remove(output_file)
    return result

    



outputFile = "stego_video.avi"
secretFile = "hello.txt"
coverMedia = "elmo.gif"

encode_video(coverMedia, secretFile, outputFile)
decode_video(outputFile)
