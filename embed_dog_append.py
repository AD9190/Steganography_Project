import shutil

# Copy the original image
shutil.copy("dog1.jpg", "dog1_steg.jpg")

# Create a large payload
large_payload = """
HIDDEN DATA - STEGANOGRAPHY TEST
This is embedded data appended to the end of the JPEG file.
""" * 500  # Repeat 500 times for substantial payload

# Append data to the end of the file
with open("dog1_steg.jpg", "ab") as f:
    payload_bytes = large_payload.encode('utf-8')
    f.write(payload_bytes)
    
print(f"✓ Successfully embedded {len(payload_bytes)} bytes into dog1_steg.jpg")
print(f"✓ Method: File append (EOI method)")
print(f"The image will still display normally but contains hidden data after the JPEG EOI marker")
