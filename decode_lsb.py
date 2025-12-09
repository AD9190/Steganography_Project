import cv2
import numpy as np

def decode_lsb(image_path):
    """Decode LSB steganography"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not load image")
    
    binary_data = ""
    
    # Extract LSBs
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(3):
                binary_data += str(img[i, j, k] & 1)
    
    # Split into bytes and convert to characters
    message = ""
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if byte == '11111111':  # Check for delimiter
            next_byte = binary_data[i+8:i+16] if i+8 < len(binary_data) else ''
            if next_byte == '11111110':
                break
        
        char = chr(int(byte, 2))
        if char.isprintable():
            message += char
        else:
            break
    
    return message

if __name__ == "__main__":
    try:
        message = decode_lsb("temp1_lsb.jpg")
        print(f"Decoded message: {message}")
    except Exception as e:
        print(f"Error: {e}")
