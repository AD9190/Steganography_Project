import cv2
import numpy as np
import joblib
from scipy.stats import skew

# ── CONFIG — change these paths ───────────────────────────────────────────────
IMAGE_PATH  = "img2_2bpp.jpg"   # path to your 2bpp embedded image
MODEL_PATH  = "models/mlp_model.joblib"
SCALER_PATH = "models/scaler.joblib"
# ─────────────────────────────────────────────────────────────────────────────

model  = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

img = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA)
hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten().astype(np.float64)

print("=== RAW IMAGE STATS ===")
print(f"Min pixel: {img.min()}, Max pixel: {img.max()}")
print(f"Mean pixel: {img.mean():.2f}, Std: {img.std():.2f}")
print(f"Hist sum: {hist.sum()}, Hist max: {hist.max():.0f}, Hist min: {hist.min():.0f}")
print(f"Hist range (max-min): {hist.max() - hist.min():.0f}")

img_f  = img.astype(np.float64)
diff_h = np.abs(np.diff(img_f, axis=1))
print(f"\n=== SPATIAL DIFF STATS ===")
print(f"Horizontal diff mean: {diff_h.mean():.4f}")
print(f"Horizontal diff std:  {diff_h.std():.4f}")

# Quick feature vector
hist_norm     = hist / (hist.sum() + 1e-8)
intensity     = np.arange(256, dtype=np.float64)
mean          = float(np.sum(intensity * hist_norm))
variance      = float(np.sum(((intensity - mean) ** 2) * hist_norm))
std_dev       = float(np.sqrt(variance)) if variance > 0 else 0.0
kurt          = float(np.sum((((intensity - mean) / (std_dev + 1e-8)) ** 4) * hist_norm)) - 3
even_odd      = float(hist[::2].sum() / (hist[1::2].sum() + 1e-8))
pix_range     = float(hist.max() - hist.min())

print(f"\n=== KEY FEATURES ===")
print(f"Kurtosis:   {kurt:.4f}")
print(f"Std Dev:    {std_dev:.4f}")
print(f"Range:      {pix_range:.4f}")
print(f"Even-Odd:   {even_odd:.4f}")

# Full predict
from app import extract_features
x_raw    = extract_features(img)
x_scaled = scaler.transform(x_raw)
prob     = model.predict_proba(x_scaled)[0]

print(f"\n=== MODEL OUTPUT ===")
print(f"Raw features (first 10): {x_raw[0][:10]}")
print(f"Scaled features (first 10): {x_scaled[0][:10]}")
print(f"Clean prob: {prob[0]*100:.2f}%  |  Stego prob: {prob[1]*100:.2f}%")

# Also test on a known clean image if you have one
print(f"\n=== SCALER INFO ===")
print(f"Scaler mean (first 5):  {scaler.mean_[:5]}")
print(f"Scaler scale (first 5): {scaler.scale_[:5]}")