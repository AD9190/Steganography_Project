import joblib
import numpy as np
from feature_extraction import extract_features_from_image 
import warnings
warnings.filterwarnings('ignore')

# Load model
stack_model = joblib.load('stack_lr_obj.joblib')

# Test on multiple images
test_images = ['tree.jpg', 'watch1.JPG', 'temp1_lsb.jpg', 'temp1_heavy.jpg']

print("="*80)
print("DIAGNOSTIC TEST - Model Predictions")
print("="*80)

for img_path in test_images:
    try:
        print(f"\n📸 Testing: {img_path}")
        print("-"*80)
        
        # Extract features
        features = extract_features_from_image(img_path)
        print(f"Features shape: {features.shape}")
        print(f"Features:\n{features.to_dict('records')[0]}")
        
        # Get base learners
        bases = stack_model['trained_bases']
        meta_model = stack_model['meta_model']
        scaler = stack_model['meta_scaler']
        
        # Base predictions
        proba_rf = bases['rf'].predict_proba(features)[:, 1][0]
        proba_xgb = bases['xgb'].predict_proba(features)[:, 1][0]
        proba_lgb = bases['lgb'].predict_proba(features)[:, 1][0]
        
        print(f"\nBase Model Probabilities:")
        print(f"  Random Forest:  {proba_rf:.4f}")
        print(f"  XGBoost:        {proba_xgb:.4f}")
        print(f"  LightGBM:       {proba_lgb:.4f}")
        
        # Stack predictions
        meta_X = np.array([[proba_rf, proba_xgb, proba_lgb]])
        print(f"\nMeta features (before scaling): {meta_X}")
        
        meta_X_scaled = scaler.transform(meta_X)
        print(f"Meta features (after scaling):  {meta_X_scaled}")
        
        # Final prediction
        final_prob = meta_model.predict_proba(meta_X_scaled)[:, 1][0]
        final_pred = int(final_prob >= 0.5)
        
        print(f"\n🎯 FINAL PREDICTION:")
        print(f"   Probability: {final_prob:.4f}")
        print(f"   Class: {'STEGANOGRAPHED' if final_pred == 1 else 'CLEAN'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
