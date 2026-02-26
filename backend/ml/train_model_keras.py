#!/usr/bin/env python3
"""
Improved ML training script using Keras FCNN (Fully Connected Neural Network).
Trains on realistic UK property data with address-based features.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Try to import TensorFlow/Keras
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("⚠️  TensorFlow not available. Please install it:")
    print("   pip install tensorflow")
    print("\nFalling back to RandomForest...")


def load_address_data():
    """Load predefined address list."""
    address_file = os.path.join(os.path.dirname(__file__), 'addresses.json')
    with open(address_file, 'r') as f:
        data = json.load(f)
    return {addr['id']: addr for addr in data['addresses']}


def generate_realistic_training_data(n_samples=2000):
    """
    Generate realistic training data based on actual UK property market.
    Uses address data to create price variations.
    """
    np.random.seed(42)

    # Load addresses
    addresses = load_address_data()
    address_ids = list(addresses.keys())

    # Generate training samples
    data = []

    for _ in range(n_samples):
        # Pick a random address
        addr_id = np.random.choice(address_ids)
        addr = addresses[addr_id]
        base_price = addr['avg_price']

        # Generate property characteristics
        beds = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.3, 0.35, 0.2, 0.05])
        baths = max(1, int(beds / 2 + np.random.uniform(0.5, 1.5)))
        ensuite = min(baths - 1, max(0, int(np.random.uniform(0, baths - 1))))
        detached = np.random.choice([0, 1], p=[0.6, 0.4])

        # Price variation based on property features
        price = base_price
        price += (beds - 3) * base_price * 0.15  # Each bed adds/removes 15% of base
        price += (baths - 1.5) * base_price * 0.10  # Each bath adds/removes 10%
        price += ensuite * base_price * 0.08  # Ensuite adds 8% per bathroom
        price += detached * base_price * 0.12  # Detached adds 12%

        # Add noise
        price *= np.random.normal(1.0, 0.1)
        price = max(100000, min(5000000, price))  # Realistic bounds

        data.append({
            'address_id': addr_id,
            'beds': beds,
            'baths': baths,
            'ensuite': ensuite,
            'detached': detached,
            'lat': addr['lat'],
            'lon': addr['lon'],
            'price': int(price)
        })

    return pd.DataFrame(data), addresses


def build_keras_model(input_shape):
    """Build a Fully Connected Neural Network (FCNN) for price prediction."""
    model = keras.Sequential([
        layers.Dense(128, activation='relu', input_shape=(input_shape,)),
        layers.BatchNormalization(),
        layers.Dropout(0.2),

        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),

        layers.Dense(32, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.1),

        layers.Dense(16, activation='relu'),

        layers.Dense(1)  # Output layer for price prediction
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )

    return model


def train_keras_model():
    """Train the Keras FCNN model."""
    if not KERAS_AVAILABLE:
        print("TensorFlow/Keras not available. Skipping Keras training.")
        return None

    print("Generating realistic training data...")
    df, addresses = generate_realistic_training_data(n_samples=2000)

    print(f"Generated {len(df)} training samples")
    print("\nData sample:")
    print(df.head(10))
    print("\nData statistics:")
    print(df[['beds', 'baths', 'ensuite', 'detached', 'price']].describe())

    # Prepare features and target
    feature_cols = ['address_id', 'beds', 'baths', 'ensuite', 'detached', 'lat', 'lon']
    X = df[feature_cols].values
    y = df['price'].values

    print(f"\nTraining Keras FCNN model...")
    print(f"Features: {feature_cols}")
    print(f"Target: price")
    print(f"Input shape: {X.shape[1]} features")

    # Normalize address_id to 0-1 range
    X_copy = X.copy().astype(float)
    X_copy[:, 0] = X_copy[:, 0] / max(X_copy[:, 0])  # Normalize address_id

    # Scale all features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_copy)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # Build and train model
    model = build_keras_model(input_shape=X_scaled.shape[1])

    print("\nModel architecture:")
    model.summary()

    # Train with early stopping
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=32,
        callbacks=[early_stopping],
        verbose=1
    )

    # Evaluate
    train_loss, train_mae = model.evaluate(X_train, y_train, verbose=0)
    test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)

    print(f"\nModel Performance:")
    print(f"  Training MAE: £{train_mae:,.0f}")
    print(f"  Testing MAE:  £{test_mae:,.0f}")

    # Save model and scaler
    os.makedirs('ml', exist_ok=True)

    model.save('ml/model_keras.h5')
    joblib.dump(scaler, 'ml/scaler_keras.joblib')
    joblib.dump(addresses, 'ml/addresses_map.joblib')

    print(f"\n✓ Keras model saved to ml/model_keras.h5")
    print(f"✓ Scaler saved to ml/scaler_keras.joblib")
    print(f"✓ Addresses saved to ml/addresses_map.joblib")

    # Test predictions
    print(f"\nTest Predictions:")
    test_cases = [
        {'address_id': 1, 'beds': 3, 'baths': 2, 'ensuite': 1, 'detached': 0, 'lat': 50.7908, 'lon': -1.1333},
        {'address_id': 2, 'beds': 6, 'baths': 2, 'ensuite': 1, 'detached': 0, 'lat': 51.5033, 'lon': -0.1276},
        {'address_id': 9, 'beds': 3, 'baths': 2, 'ensuite': 1, 'detached': 0, 'lat': 53.4808, 'lon': -2.2426},
    ]

    for sample in test_cases:
        X_sample = np.array([[
            sample['address_id'] / 25,  # Normalize address_id
            sample['beds'],
            sample['baths'],
            sample['ensuite'],
            sample['detached'],
            sample['lat'],
            sample['lon']
        ]])
        X_sample_scaled = scaler.transform(X_sample)
        pred = model.predict(X_sample_scaled, verbose=0)[0][0]
        addr = addresses[int(sample['address_id'])]
        print(f"  {addr['address']}: {sample['beds']}bed - £{pred:,.0f}")

    return model, scaler, addresses


if __name__ == '__main__':
    if KERAS_AVAILABLE:
        train_keras_model()
    else:
        print("TensorFlow/Keras not installed.")
        print("To use the Keras model, install it:")
        print("  pip install tensorflow")
