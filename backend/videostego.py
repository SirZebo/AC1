import numpy as np
import cv2 
from numpy import binary_repr
from PIL import Image
import skvideo.io


fps = 29.75
outputFile = "output1.avi"
secretFile = "hello.txt"
coverMedia = "elmo.gif"
SUPER_SECRET_KEY = "This_is_a_very_secret_key_of_Ambrose_Goh"

'''
writer = skvideo.io.FFmpegWriter(outputFile, outputdict={
  '-vcodec': 'libx264',  #use the h.264 codec
  '-crf': '0',           #set the constant rate factor to 0, which is lossless
  '-preset':'veryslow'   #the slower the better compression, in princple, try 
                         #other options see https://trac.ffmpeg.org/wiki/Encode/H.264
}) 
''' 
def load_secret(fname):
    with open(fname, 'rb') as f:
        data = f.read()
    return data



def encode():
    vidcap = cv2.VideoCapture(coverMedia)
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    out = cv2.VideoWriter(outputFile, fourcc, fps, size)

    secret_bytes = load_secret(secretFile) + bytes(SUPER_SECRET_KEY, 'utf-8')
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

def decode():
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
        if bytestream[-len(SUPER_SECRET_KEY):].decode("utf-8") == SUPER_SECRET_KEY:
            break
    # `bytestream` should now be equal to `secret_bytes`
    with open('extracted_secret.txt', 'wb') as f:
        f.write(bytestream[:-len(SUPER_SECRET_KEY)])


encode()
decode()