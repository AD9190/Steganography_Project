import joblib
import numpy as np
from feature_extraction import extract_features_from_image 

try:
    stack_model = joblib.load('stack_lr_obj.joblib')
except (ValueError, AttributeError) as e:
    print("=" * 70)
    print("ERROR: Model file incompatible with current scikit-learn version")
    print("=" * 70)
    print(f"Error details: {e}")
    print("\nThe model was trained with scikit-learn 1.2.2 but you have 1.7.0")
    print("\nSOLUTIONS:")
    print("1. Downgrade scikit-learn: pip install scikit-learn==1.2.2")
    print("2. Retrain the model with the current scikit-learn version")
    print("=" * 70)
    exit(1)
def predict_stegano_from_image(img_path, stack_model):
    # 1. Extract features
    features = extract_features_from_image(img_path)

    # 2. Get base learners and meta-learner
    bases = stack_model['trained_bases']
    meta_model = stack_model['meta_model']
    scaler = stack_model['meta_scaler']

    # 3. Get probability predictions from each base
    proba_rf = bases['rf'].predict_proba(features)[:, 1]
    proba_xgb = bases['xgb'].predict_proba(features)[:, 1]
    proba_lgb = bases['lgb'].predict_proba(features)[:, 1]

    # 4. Stack into meta-features and scale
    meta_X = np.vstack([proba_rf, proba_xgb, proba_lgb]).T
    meta_X_scaled = scaler.transform(meta_X)

    # 5. Meta-learner prediction (threshold set to 0.45)
    final_prob = meta_model.predict_proba(meta_X_scaled)[:, 1][0]
    final_pred = int(final_prob >= 0.45)

    print(f"Predicted Probability (Steganographed) = {final_prob:.4f}")
    print(f"Predicted Class = {'Steganographed (1)' if final_pred == 1 else 'Clean (0)'}")
    print(f"(Using threshold: 0.45)")

    return final_pred, final_prob

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = 'watch1.JPG'
    
    pred, prob = predict_stegano_from_image(img_path, stack_model)
