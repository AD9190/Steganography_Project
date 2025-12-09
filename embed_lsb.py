import cv2
import numpy as np

def embed_lsb(image_path, message, output_path, num_lsb_bits=2):

    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not load image")
    
    # Convert message to binary
    message_bin = ''.join(format(ord(char), '08b') for char in message)
    message_bin += '1111111111111110'  # Delimiter
    
    # Check if message fits
    max_bytes = img.shape[0] * img.shape[1] * 3 * num_lsb_bits
    if len(message_bin) > max_bytes:
        raise ValueError("Message too large for image")
    
    # Create bitmask to preserve upper bits
    # For 2 LSBs: 0xFC (11111100) - preserves top 6 bits
    # For 1 LSB:  0xFE (11111110) - preserves top 7 bits
    mask = (0xFF << num_lsb_bits) & 0xFF
    
    # Embed message
    data_index = 0
    bits_per_pixel = num_lsb_bits
    
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(3):  # RGB channels
                if data_index < len(message_bin):
                    # Extract bits for this pixel
                    bits_to_embed = ''
                    for _ in range(bits_per_pixel):
                        if data_index < len(message_bin):
                            bits_to_embed += message_bin[data_index]
                            data_index += 1
                        else:
                            bits_to_embed += '0'
                    
                    # Modify LSBs
                    img[i, j, k] = (img[i, j, k] & mask) | int(bits_to_embed, 2)
                else:
                    break
            if data_index >= len(message_bin):
                break
        if data_index >= len(message_bin):
            break
    
    # Save embedded image
    cv2.imwrite(output_path, img)
    print(f"✓ Message embedded successfully in {output_path}")
    print(f"  Embedded {len(message)} characters ({len(message_bin)} bits)")
    print(f"  Using {num_lsb_bits} LSB bits per color channel")

if __name__ == "__main__":
    embed_lsb("model.png", "this is for testing steganography", "temp1_lsb.png", num_lsb_bits=2)
