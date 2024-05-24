import cv2, numpy as np

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

def encode(image_name, secret_data):
    image = cv2.imread(image_name) # read the image
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8 # maximum bytes to encode
    print("[*] Maximum bytes to encode:", n_bytes)
    secret_data += "=====" # add stopping criteria
    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
    print("[*] Encoding data...")
    
    data_index = 0
    binary_secret_data = to_bin(secret_data) # convert data to binary
    data_len = len(binary_secret_data) # size of data to hide
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel) # convert RGB values to binary format
            if data_index < data_len: # modify the least significant bit only if there is still data to store
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2) # least significant red pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2) # least significant green pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2) # least significant blue pixel bit
                data_index += 1
            if data_index >= data_len: # if data is encoded, just break out of the loop
                break
    return image

def decode(image_name):
    print("[+] Decoding...")
    # read the image
    image = cv2.imread(image_name)
    bytes = []
    byte = ""
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            byte += r[-1]
            if len(byte) == 8:
                bytes.append(byte)
                byte = ""
            byte += g[-1]
            if len(byte) == 8:
                bytes.append(byte)
                byte = ""
            byte += b[-1]
            if len(byte) == 8:
                bytes.append(byte)
                byte = ""
    decoded_data = ""
    for byte in bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====": # we keep decoding until we see the stopping criteria.
            break
    return decoded_data[:-5]

if __name__ == "__main__":
    input_image = "cover_image.jpg"
    output_image = "stego.PNG"
    secret_data = "This is a top secret message."
    # encode the data into the image
    encoded_image = encode(image_name=input_image, secret_data=secret_data)
    # save the output image (encoded image)
    cv2.imwrite(output_image, encoded_image)
    # decode the secret data from the image
    decoded_data = decode(output_image)
    print("[+] Decoded data:", decoded_data)