import cv2
import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew

def hjorth_parameters(signal):
    """Compute Hjorth mobility and complexity."""
    first_deriv = np.diff(signal)
    second_deriv = np.diff(first_deriv)
    var0 = np.var(signal)
    var1 = np.var(first_deriv)
    var2 = np.var(second_deriv)
    mobility = np.sqrt(var1 / var0)
    complexity = np.sqrt(var2 / var1) / mobility
    return mobility, complexity

def extract_features_from_image(img_path):
    # Load as grayscale (monochromatic)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image could not be loaded. Check path or format.")

    # Compute histogram (256 bins)
    hist = cv2.calcHist([img], [0], None, [256], [0,256]).flatten()
    hist = hist / hist.sum()  # normalize histogram to probabilities

    # Basic statistics
    k = kurtosis(hist)
    s = skew(hist)
    std = np.std(hist)
    rng = np.max(hist) - np.min(hist)
    med = np.median(hist)
    gmean = np.exp(np.mean(np.log(hist[hist > 0])))  # geometric mean (ignore zeros)
    mobility, complexity = hjorth_parameters(hist)

    feature_names = ['Kurtosis', 'Skewness', 'Std', 'Range', 'Median',
                     'Geometric_Mean', 'Mobility', 'Complexity']
    values = [k, s, std, rng, med, gmean, mobility, complexity]

    return pd.DataFrame([values], columns=feature_names)
