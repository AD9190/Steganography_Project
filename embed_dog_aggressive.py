import cv2
import numpy as np

# Read the image
img = cv2.imread("dog1.jpg")
print(f"Original image shape: {img.shape}")

# Create a copy for steganography
stego_img = img.copy()

# Method: Aggressive LSB manipulation that will alter histogram
# We'll set ALL LSBs to a specific pattern that changes the distribution

# For each pixel, we'll manipulate the LSB in a way that affects histogram
# This creates detectable statistical anomalies
rows, cols, channels = stego_img.shape

# Pattern 1: Toggle LSBs in a systematic way to create histogram distortion
pattern_data = np.random.randint(0, 256, size=(rows, cols, channels), dtype=np.uint8)

# Apply aggressive LSB changes - modify 2 least significant bits
# This will cause the pixel value distribution to shift
for i in range(rows):
    for j in range(cols):
        for k in range(channels):
            # Clear the 2 LSBs and replace with pattern
            original_val = stego_img[i, j, k]
            # Set bits 0 and 1 to values from our pattern
            new_val = (original_val & 0xFC) | (pattern_data[i, j, k] & 0x03)
            stego_img[i, j, k] = new_val

# Save the stego image
cv2.imwrite("dog1_steg.jpg", stego_img)

print(f"✓ Created dog1_steg.jpg with aggressive LSB manipulation")
print(f"✓ Modified all 2 LSB bits in every pixel")
print(f"✓ This creates strong histogram distortion")

# Show some statistics
print(f"\nOriginal histogram stats:")
orig_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(f"  Mean: {np.mean(orig_gray):.2f}, Std: {np.std(orig_gray):.2f}")

print(f"\nStego histogram stats:")
stego_gray = cv2.cvtColor(stego_img, cv2.COLOR_BGR2GRAY)
print(f"  Mean: {np.mean(stego_gray):.2f}, Std: {np.std(stego_gray):.2f}")

# Calculate histogram changes
orig_hist = cv2.calcHist([orig_gray], [0], None, [256], [0,256]).flatten()
stego_hist = cv2.calcHist([stego_gray], [0], None, [256], [0,256]).flatten()

# Normalize
orig_hist = orig_hist / orig_hist.sum()
stego_hist = stego_hist / stego_hist.sum()

# Calculate difference
hist_diff = np.sum(np.abs(orig_hist - stego_hist))
print(f"\nHistogram difference (L1 distance): {hist_diff:.6f}")
print(f"This should be detectable by the model!")
