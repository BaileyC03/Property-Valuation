import os
import json
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import requests
from datetime import datetime
import lightgbm as lgb

app = Flask(__name__)
CORS(app)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'addresses.db')

# Model paths (LightGBM only)
LIGHTGBM_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'model_lightgbm.joblib')
LIGHTGBM_SCALER_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'scaler_lightgbm.joblib')
LIGHTGBM_FEATURES_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'feature_cols_lightgbm.joblib')

model = None
scaler = None
feature_cols = None

def get_db_connection():
    """Create database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_address_by_id(address_id):
    """Query address from database by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM postcodes WHERE id = ?', (address_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row['id'],
                'address': row['address'],
                'postcode': row['postcode'],
                'lat': row['latitude'],
                'lon': row['longitude'],
                'region': row['region']
            }
        return None
    except Exception as e:
        print(f"Database query error: {e}")
        return None

def search_addresses(query):
    """Search addresses by partial match (for autocomplete)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT id, address, postcode, region
            FROM postcodes
            WHERE address LIKE ? OR postcode LIKE ?
            ORDER BY address
            LIMIT 50
        ''', (search_term, search_term))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        print(f"Database search error: {e}")
        return []

def load_model():
    """Load the LightGBM model and scaler."""
    global model, scaler, feature_cols
    try:
        if os.path.exists(LIGHTGBM_MODEL_PATH):
            model = joblib.load(LIGHTGBM_MODEL_PATH)
            print(f"✓ LightGBM model loaded from {LIGHTGBM_MODEL_PATH}")

            if os.path.exists(LIGHTGBM_SCALER_PATH):
                scaler = joblib.load(LIGHTGBM_SCALER_PATH)
                print(f"✓ Feature scaler loaded")

            if os.path.exists(LIGHTGBM_FEATURES_PATH):
                feature_cols = joblib.load(LIGHTGBM_FEATURES_PATH)
                print(f"✓ Feature columns: {feature_cols}")
            else:
                feature_cols = ['beds', 'baths', 'ensuite', 'detached', 'lat', 'lon']
                print(f"  Using default feature columns: {feature_cols}")
        else:
            print(f"⚠ No model found at {LIGHTGBM_MODEL_PATH}")
            print("Train with: python ml/train_lightgbm_with_plot.py")

    except Exception as e:
        print(f"Error loading model: {e}")

def lookup_postcode(postcode):
    """Look up a UK postcode using postcodes.io (free, no API key needed)."""
    try:
        clean = postcode.strip().upper()
        url = f"https://api.postcodes.io/postcodes/{clean}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 200 and data.get('result'):
                r = data['result']
                return {
                    'postcode': r['postcode'],
                    'lat': r['latitude'],
                    'lon': r['longitude'],
                    'region': r.get('region') or r.get('country', 'UK'),
                    'district': r.get('admin_district', ''),
                }
        return None
    except Exception as e:
        print(f"Postcode lookup error: {e}")
        return None

def extract_features(address_id, beds, baths, ensuite, detached):
    """
    Extract and prepare features for the ML model using address_id.
    """
    features = {
        'address_id': float(address_id),
        'beds': float(beds),
        'baths': float(baths),
        'ensuite': float(ensuite),
        'detached': float(detached),
    }

    # Get coordinates from database
    address_info = query_address_by_id(int(address_id))

    if address_info:
        features['lat'] = address_info['lat']
        features['lon'] = address_info['lon']
    else:
        # Default to London if address not found
        print(f"⚠ Address ID {address_id} not found in database, using default coordinates")
        features['lat'] = 51.5074
        features['lon'] = -0.1278

    return features, address_info

def predict_value(features):
    """
    Use the ML model to predict property value.
    Returns min, avg, max values and predicted rent.
    """
    if model is None or scaler is None:
        # Return dummy values if model not loaded
        base_value = 300000
        base_rent = 1000
        return {
            'min_value': int(base_value * 0.8),
            'avg_value': int(base_value),
            'max_value': int(base_value * 1.2),
            'predicted_rent': int(base_rent),
            'model_loaded': False
        }

    try:
        # Build feature vector from the model's expected columns
        cols = feature_cols or ['beds', 'baths', 'ensuite', 'detached', 'lat', 'lon']
        feature_vector = np.array([[features.get(c, 0.0) for c in cols]])

        # Scale features
        feature_scaled = scaler.transform(feature_vector)

        # LightGBM prediction
        predicted_price = model.predict(feature_scaled)[0]

        # Ensure price is within reasonable bounds
        predicted_price = max(30000, min(5000000, predicted_price))

        # Calculate range (±10%) and estimated rent
        variance = predicted_price * 0.10
        predicted_rent = predicted_price / 200  # Rough rent estimate (1/200 of value per month)

        return {
            'min_value': int(predicted_price - variance),
            'avg_value': int(predicted_price),
            'max_value': int(predicted_price + variance),
            'predicted_rent': int(predicted_rent),
            'model_loaded': True
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'model_loaded': False
        }

@app.route('/addresses', methods=['GET'])
def get_addresses():
    """Get list of all available addresses from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, address, postcode, region FROM postcodes ORDER BY address')
        addresses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'addresses': addresses})
    except Exception as e:
        print(f"Error fetching addresses: {e}")
        return jsonify({'error': 'Addresses not available', 'details': str(e)}), 500

@app.route('/search', methods=['GET'])
def search_address():
    """Search addresses by query string (for autocomplete)."""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'results': []}), 200

    results = search_addresses(query)
    return jsonify({'results': results})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'model_type': 'LightGBM (Gradient Boosting)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint.
    Expects JSON with: postcode, beds, baths, ensuite, detached
    Also supports legacy address_id for backward compatibility.
    """
    try:
        data = request.json

        # Validate common fields
        required_fields = ['beds', 'baths']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Validate types and ranges
        try:
            beds = int(data['beds'])
            baths = int(data['baths'])
            property_type = str(data.get('property_type', 'semi-detached')).lower()

            if beds < 1 or baths < 1:
                return jsonify({'error': 'Invalid bedroom/bathroom values'}), 400
        except ValueError as e:
            return jsonify({'error': f'Invalid input types: {str(e)}'}), 400

        # Derive property type flags
        detached = 1 if property_type == 'detached' else 0
        semi_detached = 1 if property_type == 'semi-detached' else 0
        terraced = 1 if property_type == 'terraced' else 0
        flat = 1 if property_type == 'flat' else 0

        # Get location from postcode or legacy address_id
        lat = None
        lon = None
        address_display = ''

        if 'postcode' in data and data['postcode']:
            postcode = str(data['postcode']).strip().upper()
            postcode_info = lookup_postcode(postcode)
            if postcode_info:
                lat = postcode_info['lat']
                lon = postcode_info['lon']
                district = postcode_info.get('district', '')
                region = postcode_info.get('region', 'UK')
                address_display = f"{district}, {postcode} ({region})" if district else f"{postcode} ({region})"
            else:
                return jsonify({'error': f'Could not find postcode: {postcode}. Please enter a valid UK postcode.'}), 400

        elif 'address_id' in data:
            address_id = int(data['address_id'])
            addr_info = query_address_by_id(address_id)
            if addr_info:
                lat = addr_info['lat']
                lon = addr_info['lon']
                address_display = f"{addr_info['address']} ({addr_info['postcode']})"
            else:
                return jsonify({'error': f'Address ID {address_id} not found'}), 400
        else:
            return jsonify({'error': 'Must provide a postcode'}), 400

        # Build feature dict (matching training column names)
        features = {
            'beds': float(beds),
            'bedrooms': float(beds),
            'baths': float(baths),
            'bathrooms': float(baths),
            'ensuite': 0.0,
            'detached': float(detached),
            'semi_detached': float(semi_detached),
            'terraced': float(terraced),
            'flat': float(flat),
            'lat': lat,
            'lon': lon,
            # Derived geo features
            'lat2': lat ** 2,
            'lon2': lon ** 2,
            'lat_lon': lat * lon,
            'dist_portsmouth': ((lat - 50.7989)**2 + (lon - (-1.0912))**2) ** 0.5,
            # Interaction features
            'beds_x_baths': float(beds * baths),
            'beds_x_detached': float(beds * detached),
            'total_rooms': float(beds + baths),
            # Time features (predicting at "now")
            'sale_year': 2026.0,
            'years_ago': 0.0,
        }

        # Get prediction
        prediction = predict_value(features)

        if 'error' in prediction and not prediction.get('model_loaded'):
            return jsonify({
                'error': 'Model not available',
                'message': 'Train the model first'
            }), 500

        # Assemble response
        response = {
            'address': address_display,
            'postcode': data.get('postcode', ''),
            'beds': beds,
            'baths': baths,
            'property_type': property_type,
            'min_value': prediction['min_value'],
            'avg_value': prediction['avg_value'],
            'max_value': prediction['max_value'],
            'predicted_rent': prediction['predicted_rent'],
            'model_loaded': prediction.get('model_loaded', True),
            'model_type': 'LightGBM (Gradient Boosting)',
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error in /predict: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

load_model()

if __name__ == '__main__':
    print("Starting UK Property Valuation API...")
    print("Available endpoints:")
    print("  GET  /health     - Health check")
    print("  GET  /addresses  - Get list of addresses (legacy)")
    print("  POST /predict    - Get property valuation (accepts any UK postcode)")
    print(f"Model loaded: {model is not None}")
    app.run(debug=True, port=5000, host='0.0.0.0')
