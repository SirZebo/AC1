import numpy as np
import cv2 
from numpy import binary_repr
#import os
#import subprocess

from zipfile import ZipFile

ZIPPED_SECRET_FILE_NAME = 'zippedSecret.zip'

def load_secret(fname):
    with open(fname, 'rb') as f:
        data = f.read()
    return data

def zipSecretFile(inputFile):
    with ZipFile(ZIPPED_SECRET_FILE_NAME,'w') as zip:
        print("Zipping secret...")
        zip.write(inputFile)
        print("Zipping secret Done!")

def unzipSecretFile(file_name: str):
    with ZipFile(file_name, 'r') as zip:
        print("Unzipping secret...")
        zip.extractall() 
        print("Unzipping secret Done!")

#def convert_avi_to_mp4(input_file: str, output_file: str):
#    command = f"ffmpeg -i {input_file} -vcodec libx264 {output_file}"
#    subprocess.run(command, shell=True)

def encode(coverMedia: str, secretFile: str, outputFile: str):
    vidcap = cv2.VideoCapture(coverMedia)
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    #temp_avi_file = outputFile.replace(".mp4", ".avi")
    #out = cv2.VideoWriter(temp_avi_file, fourcc, fps, size)
    out = cv2.VideoWriter(outputFile, fourcc, fps, size)

    zipSecretFile(secretFile)
    secret_bytes = load_secret(ZIPPED_SECRET_FILE_NAME) + bytes(SUPER_SECRET_KEY, 'utf-8')
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

def decode(outputFile: str):
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
    # `bytestream` should now be equal to `secret_bytes`
    with open(ZIPPED_SECRET_FILE_NAME, 'wb') as f:
        f.write(bytestream[:-len(SUPER_SECRET_KEY)])
    
    unzipSecretFile(ZIPPED_SECRET_FILE_NAME)

outputFile = "output1.avi"
secretFile = "hello.txt"
coverMedia = "elmo.gif"
outputSecret = 'extracted_secret.txt'
SUPER_SECRET_KEY = "This_is_a_very_secret_key_of_Ambrose_Goh"

#encode(coverMedia, secretFile, outputFile)
#decode(outputFile)