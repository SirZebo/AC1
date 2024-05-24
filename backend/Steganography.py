import cv2, numpy as np

SUPER_SECRET_KEY = "This_is_a_very_secret_key_of_Ambrose_Goh"

def to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data ])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")
    
def byteToBinary(data):
    return ''.join([ format(i, "08b") for i in data ])

def encode(image_name, secret_file):
    image = cv2.imread(image_name) # read the image
    if image is None:
        raise FileNotFoundError("Cover image not found.")
    
    with open(secret_file, "rb") as file:
        secret_data = file.read()

    n_bytes = image.shape[0] * image.shape[1] * 3 // 8 # maximum bytes to encode
    print("[*] Maximum bytes to encode:", n_bytes)

    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
    print("[*] Encoding data...")
    
    dataIndex = [0]
    binary_secret_data = byteToBinary(secret_data) + to_bin(SUPER_SECRET_KEY) # convert data to binary
    dataLen = len(binary_secret_data) # size of data to hide
    image = writePixelBits(dataIndex, dataLen, 0, image, binary_secret_data)
    for i in range(8):
        image = writePixelBits(dataIndex, dataLen, i, image, binary_secret_data)
        if dataIndex[0] >= dataLen: # if data is encoded, just break out of the loop
            break
    return image

def writePixelBits(dataIndex: list[int], dataLen: int, bitNo: int, image, binary_secret_data: list[str]):
    bitNo = -(bitNo + 1)
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel) # convert RGB values to binary format
            if dataIndex[0] < dataLen: # modify the least significant bit only if there is still data to store
                pixel[0] = int(r[:bitNo] + binary_secret_data[dataIndex[0]] + r[bitNo:bitNo + 1], 2) # least significant red pixel bit
                dataIndex[0] += 1
            if dataIndex[0] < dataLen:
                pixel[1] = int(g[:bitNo] + binary_secret_data[dataIndex[0]] + g[bitNo:bitNo + 1], 2) # least significant green pixel bit
                dataIndex[0] += 1
            if dataIndex[0] < dataLen:
                pixel[2] = int(b[:bitNo] + binary_secret_data[dataIndex[0]] + b[bitNo:bitNo + 1], 2) # least significant blue pixel bit
                dataIndex[0] += 1
            if dataIndex[0] >= dataLen: # if data is encoded, just break out of the loop
                break
    return image


def decode(image_name):
    print("[+] Decoding...")
    # read the image
    image = cv2.imread(image_name)
    all_bytes = []
    byte = ""
    for lsb in range(1,9):
        for row in image:
            for pixel in row:
                for color in pixel:
                    pixelValues = to_bin(color)
                    byte += pixelValues[-lsb]
                    if len(byte) == 8:
                        all_bytes.append(byte)
                        byte = ""
    queue = []
    pos = 0
    for byte in all_bytes:
        pos = pos + 1
        queue.append(chr(int(byte,2)))
        if len(queue) == len(SUPER_SECRET_KEY):
            currentDelimiter = ''.join(queue)
            if currentDelimiter == SUPER_SECRET_KEY:
                break
            queue.pop(0)
    

    if pos == len(all_bytes):
        print("Decode failed!")
        return
    pos -= len(SUPER_SECRET_KEY)
    all_bytes = all_bytes[:pos]
    decoded_data = bytes([int(byte, 2) for byte in all_bytes])
    
    # File type detection
    file_signature = {
        b'\x50\x4B\x03\x04': 'ZIP',  # ZIP file header
        b'\xFF\xD8\xFF': 'JPEG',     # JPEG image header
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'PNG',  # PNG image header
        b'\x25\x50\x44\x46': 'PDF'   # PDF file header
    }
    
    # Determine file type
    for signature, extension in file_signature.items():
        if decoded_data.startswith(signature):
            output_file = f"extracted_secret.{extension.lower()}"
            break
    else:
        output_file = "extracted_secret.txt"  # Default binary file if no known signature is found

    # Write to output file
    with open(output_file, "wb") as file:
        file.write(decoded_data)
    print("[+] Data extracted and saved as", output_file)

def encodeMedia(media_path, secret_file):
    cap = cv2.VideoCapture(media_path)
    #fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #duration = frame_count/fps

    with open(secret_file, "rb") as file:
        secret_data = file.read()

    dataIndex = [0]
    binary_secret_data = byteToBinary(secret_data) + to_bin(SUPER_SECRET_KEY) # convert data to binary
    for i in range(1, frame_count):
        cap.set(1, i)
        res, frame = cap.read()
        height, width, channels = frame.shape
        for x in range(0, width) :
            for y in range(0, height):
                # print(x,y, frame[x,y,0], frame[x,y,1], frame[x,y,2])
                print(frame[x,y,0]) #B Channel Value
                print(frame[x,y,1]) #G Channel Value
                print(frame[x,y,2]) #R Channel Value

    cap.release()
    
    


if __name__ == "__main__":
    input_image = "cover_image.jpg"
    output_image = "stego.PNG"
    secret_file = "secret.ZIP"
    cover_media = "cover_media.mp4"
    # encode the data into the image
    encoded_image = encode(image_name=input_image, secret_file=secret_file)
    # save the output image (encoded image)
    cv2.imwrite(output_image, encoded_image)
    # decode the secret data from the image
    decoded_data = decode(output_image)
    print("[+] Decoded data:", decoded_data)
    ##encodeMedia(cover_media, secret_file)