#!/usr/bin/env python3
"""
Improved ML training script - Fixed version.
Uses proper price scaling and better loss function.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("TensorFlow not available")
    exit(1)


def load_address_data():
    """Load predefined address list."""
    address_file = os.path.join(os.path.dirname(__file__), 'addresses.json')
    with open(address_file, 'r') as f:
        data = json.load(f)
    return {addr['id']: addr for addr in data['addresses']}


def generate_realistic_training_data(n_samples=3000):
    """Generate realistic training data with proper price scaling."""
    np.random.seed(42)

    addresses = load_address_data()
    address_ids = list(addresses.keys())

    data = []

    for _ in range(n_samples):
        addr_id = np.random.choice(address_ids)
        addr = addresses[addr_id]
        base_price = float(addr['avg_price'])

        beds = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.05, 0.25, 0.35, 0.25, 0.08, 0.02])
        baths = max(1, int(beds / 2.5 + np.random.uniform(0.3, 1.2)))
        ensuite = min(baths - 1, max(0, int(np.random.uniform(0, min(2, baths - 1)))))
        detached = np.random.choice([0, 1], p=[0.65, 0.35])

        # Price multipliers
        bed_multiplier = 1.0 + (beds - 3) * 0.12  # ±12% per bed vs 3-bed baseline
        bath_multiplier = 1.0 + (baths - 1.5) * 0.08  # ±8% per bath
        ensuite_multiplier = 1.0 + ensuite * 0.05  # +5% per ensuite
        detached_multiplier = 1.0 + (detached * 0.10)  # +10% if detached

        price = base_price * bed_multiplier * bath_multiplier * ensuite_multiplier * detached_multiplier

        # Add realistic noise (±8%)
        price *= np.random.normal(1.0, 0.08)
        price = max(100000, min(5000000, price))

        data.append({
            'address_id': float(addr_id),
            'beds': float(beds),
            'baths': float(baths),
            'ensuite': float(ensuite),
            'detached': float(detached),
            'lat': float(addr['lat']),
            'lon': float(addr['lon']),
            'price': float(price)
        })

    return pd.DataFrame(data), addresses


def build_model(input_shape):
    """Build FCNN with proper architecture."""
    model = keras.Sequential([
        layers.Input(shape=(input_shape,)),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),

        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),

        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),

        layers.Dense(32, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.1),

        layers.Dense(16, activation='relu'),
        layers.Dense(1)  # Price output
    ])

    # Use MAE loss (better for regression)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mae',  # Mean Absolute Error - better for price prediction
        metrics=['mae', 'mse']
    )

    return model


def train_model():
    """Train the model."""
    print("Generating training data...")
    df, addresses = generate_realistic_training_data(n_samples=3000)

    print(f"Generated {len(df)} samples")
    print("\nData sample:")
    print(df.head(10))
    print("\nPrice statistics:")
    print(df['price'].describe())

    # Prepare features
    feature_cols = ['address_id', 'beds', 'baths', 'ensuite', 'detached', 'lat', 'lon']
    X = df[feature_cols].values
    y = df['price'].values.reshape(-1, 1)  # Column vector

    print(f"\nTraining Keras FCNN...")

    # Normalize address_id (1-25 -> 0-1)
    X_copy = X.copy().astype(float)
    X_copy[:, 0] = X_copy[:, 0] / 25.0

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_copy)

    # Scale prices too for training
    price_scaler = StandardScaler()
    y_scaled = price_scaler.fit_transform(y)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_scaled, test_size=0.2, random_state=42
    )

    # Build model
    model = build_model(X_scaled.shape[1])

    print("\nModel architecture:")
    model.summary()

    # Train
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True
    )

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=150,
        batch_size=32,
        callbacks=[early_stopping],
        verbose=0
    )

    # Evaluate
    train_loss = model.evaluate(X_train, y_train, verbose=0)
    test_loss = model.evaluate(X_test, y_test, verbose=0)

    # Convert back to original scale for metrics
    train_pred = model.predict(X_train, verbose=0)
    test_pred = model.predict(X_test, verbose=0)
    train_pred_original = price_scaler.inverse_transform(train_pred)
    test_pred_original = price_scaler.inverse_transform(test_pred)
    y_train_original = price_scaler.inverse_transform(y_train)
    y_test_original = price_scaler.inverse_transform(y_test)

    train_mae = np.mean(np.abs(train_pred_original - y_train_original))
    test_mae = np.mean(np.abs(test_pred_original - y_test_original))

    print(f"\nModel Performance:")
    print(f"  Training MAE: £{train_mae:,.0f}")
    print(f"  Testing MAE:  £{test_mae:,.0f}")

    # Save
    os.makedirs('ml', exist_ok=True)
    model.save('ml/model_keras.h5')
    joblib.dump(scaler, 'ml/scaler_keras.joblib')
    joblib.dump(price_scaler, 'ml/price_scaler_keras.joblib')
    joblib.dump(addresses, 'ml/addresses_map.joblib')

    print(f"\n✓ Model saved to ml/model_keras.h5")
    print(f"✓ Scaler saved to ml/scaler_keras.joblib")
    print(f"✓ Price scaler saved to ml/price_scaler_keras.joblib")
    print(f"✓ Addresses saved to ml/addresses_map.joblib")

    # Test predictions
    print(f"\nTest Predictions:")
    test_cases = [
        {'address_id': 1.0, 'beds': 3.0, 'baths': 2.0, 'ensuite': 1.0, 'detached': 0.0, 'lat': 50.7908, 'lon': -1.1333},
        {'address_id': 2.0, 'beds': 6.0, 'baths': 2.0, 'ensuite': 1.0, 'detached': 0.0, 'lat': 51.5033, 'lon': -0.1276},
        {'address_id': 9.0, 'beds': 3.0, 'baths': 2.0, 'ensuite': 1.0, 'detached': 0.0, 'lat': 53.4808, 'lon': -2.2426},
    ]

    for sample in test_cases:
        X_sample = np.array([[
            sample['address_id'] / 25.0,
            sample['beds'],
            sample['baths'],
            sample['ensuite'],
            sample['detached'],
            sample['lat'],
            sample['lon']
        ]])
        X_sample_scaled = scaler.transform(X_sample)
        pred_scaled = model.predict(X_sample_scaled, verbose=0)
        pred = price_scaler.inverse_transform(pred_scaled)[0][0]
        addr = addresses[int(sample['address_id'])]
        print(f"  {addr['address']}: {int(sample['beds'])}bed - £{pred:,.0f}")


if __name__ == '__main__':
    train_model()
