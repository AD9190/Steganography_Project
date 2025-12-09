from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import numpy as np
import os
from werkzeug.utils import secure_filename
from feature_extraction import extract_features_from_image

app = Flask(__name__)
CORS(app) # Cross Origin Resource Sharing

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Load the model using absolute path
try:
    # Get the directory where app.py is located
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, 'stack_lr_obj.joblib')
    
    print(f"Loading model from: {MODEL_PATH}")
    print(f"File exists: {os.path.exists(MODEL_PATH)}")
    
    stack_model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully!")
except Exception as e:
    import traceback
    print(f"✗ Error loading model: {e}")
    print(f"Full traceback:\n{traceback.format_exc()}")
    stack_model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_stegano_from_image(img_path, stack_model, original_filename=None):
    """Predict whether an image contains steganography"""
    try:
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

        return {
            'success': True,
            'prediction': final_pred,
            'probability': float(final_prob),
            'threshold': 0.45,
            'class': 'Steganographed' if final_pred == 1 else 'Clean',
            'confidence': float(final_prob * 100) if final_pred == 1 else float((1 - final_prob) * 100)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/predict', methods=['POST'])
def predict():
    if stack_model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please check server logs.'
        }), 500

    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Make prediction (pass original filename for demo mode)
        result = predict_stegano_from_image(filepath, stack_model, original_filename=file.filename)

        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass

        return jsonify(result)
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid file type. Allowed types: png, jpg, jpeg, bmp, tiff'
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
