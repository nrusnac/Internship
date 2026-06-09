from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

app = Flask(__name__)

# Configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'internship_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password123')

MODEL_PATH = os.getenv('MODEL_PATH', '/workspace/Docker/models/iris_model.joblib')

# Species mapping
SPECIES_MAP = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}
FEATURES = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']

# Load model at startup
model = joblib.load(MODEL_PATH)
print(f"Model loaded successfully from {MODEL_PATH}")


def save_prediction_to_db(input_data, prediction, confidence):
    """Save prediction to database"""
    conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

    cursor = conn.cursor()

    # Insert prediction record
    cursor.execute(
        """
        INSERT INTO predictions (input_data, prediction_result, confidence)
        VALUES (%s, %s, %s)
        """,
        (json.dumps(input_data), prediction, confidence)
    )

    conn.commit()
    cursor.close()
    conn.close()

@app.route('/predict', methods=['POST'])
def predict():
    # Get JSON data
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    # Extract features in correct order
    features = []
    for feature in FEATURES:
        if feature not in data:
            return jsonify({'error': f'Missing feature: {feature}'}), 400
        features.append(float(data[feature]))

    # Convert to numpy array and reshape
    X = np.array([features])

    # Make prediction
    prediction_class = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    confidence = float(probabilities[prediction_class])

    # Map class to species name
    prediction_name = SPECIES_MAP[prediction_class]

    # Save to database
    saved = save_prediction_to_db(data, prediction_name, confidence)

    return jsonify({
        'prediction': prediction_name,
        'prediction_class': int(prediction_class),
        'confidence': round(confidence, 4),
        'probabilities': {
            'setosa': round(float(probabilities[0]), 4),
            'versicolor': round(float(probabilities[1]), 4),
            'virginica': round(float(probabilities[2]), 4)
        },
        'input': data,
        'saved_to_db': saved,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/history', methods=['GET'])
def get_history():
    """Get prediction history from database(cool function)"""
    conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, prediction_result, confidence, created_at FROM predictions ORDER BY created_at DESC LIMIT 50"
    )
    predictions = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({
        'count': len(predictions),
        'predictions': predictions
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'name': 'Iris Prediction Service',
        'endpoints': {
            'POST /predict': 'Make a prediction (requires JSON with flower measurements)',
            'GET /history': 'Get prediction history'
        },
        'example_request': {
            'sepal_length': 5.1,
            'sepal_width': 3.5,
            'petal_length': 1.4,
            'petal_width': 0.2
        }
    }), 200


if __name__ == '__main__':
    print(f"Starting Flask app...")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"Model path: {MODEL_PATH}")
    app.run(host='0.0.0.0', port=5000, debug=False)
