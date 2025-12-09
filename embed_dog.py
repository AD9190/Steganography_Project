from embed_lsb import embed_lsb
import cv2

# Get image dimensions to calculate maximum capacity
img = cv2.imread("dog1.jpg")
max_capacity = (img.shape[0] * img.shape[1] * 3 * 2) // 8  # 2 LSB bits per channel, converted to bytes

print(f"Image size: {img.shape[0]}x{img.shape[1]}")
print(f"Maximum capacity: {max_capacity} bytes ({max_capacity} characters)")

# Create a MUCH larger payload - aim for 80-90% capacity to cause detectable statistical changes
target_size = int(max_capacity * 0.85)  # Use 85% of capacity

base_message = """
STEGANOGRAPHY TEST DATA - LARGE PAYLOAD FOR DETECTION TESTING
================================================================
This is a substantial payload designed to create detectable statistical anomalies.
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident.

The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs.
ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 !@#$%^&*()_+-=[]{}|;:,.<>?
Binary data simulation: 01010101 11110000 10101010 00001111 11111111 00000000 10011001 01100110
Hexadecimal: 0x1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9A0B1C2D3E4F5A6B7C8D9E0F1A2B3C4D5E6F
Random characters: qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890

Statistical anomaly generation - repeating patterns to affect histogram analysis:
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD

Varying data patterns for entropy modification:
AlTeRnAtInG CaSe TeXt FoR PaTtErN ChAnGeS - alternating case text for pattern changes
12321234321234543212345654321234567654321234567876543212345678987654321234567890
mixedMIXEDmixedMIXEDmixedMIXEDmixedMIXEDmixedMIXEDmixedMIXEDmixedMIXEDmixedMIXED

Additional entropy: The model uses ensemble learning with Random Forest, XGBoost, and LightGBM
combined with Logistic Regression meta-learner to detect statistical anomalies in image histograms.
Feature extraction analyzes mean, variance, skewness, kurtosis, entropy, and energy of color channels.
"""

# Calculate how many repetitions needed
repetitions = (target_size // len(base_message)) + 1
large_message = (base_message * repetitions)[:target_size]

print(f"Target payload size: {target_size} characters")
print(f"Actual payload size: {len(large_message)} characters")
print(f"Capacity utilization: {(len(large_message)/max_capacity)*100:.1f}%")
print(f"\nEmbedding message...")

# Apply LSB steganography with 2 LSB bits for higher capacity
embed_lsb("dog1.jpg", large_message, "dog1_steg.jpg", num_lsb_bits=2)

print(f"\n✓ Successfully created dog1_steg.jpg with {len(large_message)} character payload")
print(f"This should create detectable statistical changes in the image!")
