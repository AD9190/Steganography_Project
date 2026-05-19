import cv2
import numpy as np
import os

def embed_lsb_grayscale(image_path, bpp):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found!")
    if not (0 < bpp <= 8):
        raise ValueError("bpp must be between 1 and 8")

    bpp = int(bpp)

    h, w = img.shape
    total_pixels = h * w
    total_bits = bpp * total_pixels

    print(f"Embedding {total_bits} bits ({bpp} bpp)")

    payload = np.random.randint(0, 2, total_bits, dtype=np.uint8)

    flat_img = img.flatten().astype(np.uint8)
    mask = np.uint8(0xFF ^ ((1 << bpp) - 1))

    # Vectorized embedding
    payload_matrix = payload.reshape(total_pixels, bpp)
    shifts         = np.arange(bpp, dtype=np.uint8)
    embed_values   = (payload_matrix << shifts).sum(axis=1).astype(np.uint8)
    flat_img       = (flat_img & mask) | embed_values

    stego_img = flat_img.reshape((h, w))

    # ── Auto output path: <name>_<bpp>bpp.jpg ────────────────────────────────
    base, _ = os.path.splitext(image_path)
    output_path = f"{base}_{bpp}bpp.jpg"

    cv2.imwrite(output_path, stego_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
    print(f"Saved → {output_path}")
    return output_path


# ----------- RUN -----------
if __name__ == "__main__":
    image_path = input("Enter image path: ")
    bpp        = float(input("Enter payload (bpp, max 8): "))
    embed_lsb_grayscale(image_path, bpp)