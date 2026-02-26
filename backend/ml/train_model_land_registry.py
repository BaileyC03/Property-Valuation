#!/usr/bin/env python3
"""
Train Keras model using HM Land Registry real data.
This replaces synthetic data with government property transaction data.
"""

import os
import pandas as pd
import numpy as np
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
    print("TensorFlow not available. Install with: pip install tensorflow==2.20.0")
    exit(1)

def load_land_registry_data():
    """Load processed Land Registry training data."""
    filepath = 'land_registry_training.parquet'

    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found")
        print("Run: python ml/process_land_registry.py")
        exit(1)

    print(f"Loading {filepath}...")
    df = pd.read_parquet(filepath)
    print(f"✓ Loaded {len(df)} training samples from Land Registry data")

    return df

def build_model(input_shape):
    """Build improved FCNN for Land Registry data."""
    model = keras.Sequential([
        layers.Input(shape=(input_shape,)),

        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.4),

        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),

        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),

        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.1),

        layers.Dense(32, activation='relu'),
        layers.Dense(1)  # Price output
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mae',
        metrics=['mae', 'mse']
    )

    return model

def train_model():
    """Train model with HM Land Registry data."""
    print("\n" + "="*70)
    print("Training Keras Model with HM Land Registry Data")
    print("="*70)

    # Load data
    df = load_land_registry_data()

    # Display data info
    print("\nData Overview:")
    print(f"  Property types: {df['property_type'].unique()}")
    print(f"  Bedrooms range: {df['beds'].min():.0f} - {df['beds'].max():.0f}")
    print(f"  Price range: £{df['price'].min():,.0f} - £{df['price'].max():,.0f}")
    print(f"  Locations: {len(df['address'].unique())} unique")

    # Prepare features
    feature_cols = ['beds', 'baths', 'ensuite', 'detached', 'lat', 'lon']
    X = df[feature_cols].values
    y = df['price'].values.reshape(-1, 1)

    print(f"\nFeature shape: {X.shape}")
    print(f"Target shape: {y.shape}")

    # Scale features
    print("\nScaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Scale prices
    price_scaler = StandardScaler()
    y_scaled = price_scaler.fit_transform(y)

    # Split data
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_scaled, test_size=0.2, random_state=42
    )

    print(f"\nData split:")
    print(f"  Training: {len(X_train)} samples")
    print(f"  Testing: {len(X_test)} samples")
    print(f"  Train/Test ratio: {len(X_train)/len(X_test):.1f}:1")

    # Build model
    print("\nBuilding model...")
    model = build_model(X_scaled.shape[1])
    print("Model architecture:")
    model.summary()

    # Train
    print(f"\nTraining for up to 200 epochs with early stopping...")
    print("(This may take 2-10 minutes depending on data size)")

    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=20,
        restore_best_weights=True
    )

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=200,
        batch_size=32,
        callbacks=[early_stopping],
        verbose=1
    )

    # Evaluate
    print("\nEvaluating model...")
    train_pred = model.predict(X_train, verbose=0)
    test_pred = model.predict(X_test, verbose=0)

    # Convert back to original scale
    train_pred_original = price_scaler.inverse_transform(train_pred)
    test_pred_original = price_scaler.inverse_transform(test_pred)
    y_train_original = price_scaler.inverse_transform(y_train)
    y_test_original = price_scaler.inverse_transform(y_test)

    train_mae = np.mean(np.abs(train_pred_original - y_train_original))
    test_mae = np.mean(np.abs(test_pred_original - y_test_original))

    train_r2 = 1 - (np.sum((y_train_original - train_pred_original)**2) /
                    np.sum((y_train_original - np.mean(y_train_original))**2))
    test_r2 = 1 - (np.sum((y_test_original - test_pred_original)**2) /
                   np.sum((y_test_original - np.mean(y_test_original))**2))

    print(f"\n📊 MODEL PERFORMANCE (with Land Registry data):")
    print(f"  Training MAE: £{train_mae:,.0f}")
    print(f"  Testing MAE:  £{test_mae:,.0f}")
    print(f"  Training R²:  {train_r2:.4f}")
    print(f"  Testing R²:   {test_r2:.4f}")
    print(f"\n  ✨ Real data accuracy: {test_r2*100:.1f}%")

    # Compare with synthetic data
    print(f"\n📈 IMPROVEMENT vs Synthetic Data:")
    print(f"  Before (synthetic): ±£85,646 MAE")
    print(f"  After (real data):  ±£{test_mae:,.0f} MAE")
    improvement = ((85646 - test_mae) / 85646) * 100
    print(f"  Improvement: {improvement:.1f}%")

    # Sample predictions
    print(f"\n🏠 Sample Predictions:")
    sample_indices = np.random.choice(len(X_test), min(5, len(X_test)), replace=False)
    for idx in sample_indices:
        actual = y_test_original[idx][0]
        predicted = test_pred_original[idx][0]
        error = abs(actual - predicted) / actual * 100
        print(f"  Actual: £{actual:,.0f} → Predicted: £{predicted:,.0f} (error: {error:.1f}%)")

    # Save model
    print(f"\n💾 Saving model...")
    os.makedirs('ml', exist_ok=True)
    model.save('ml/model_land_registry.h5')
    joblib.dump(scaler, 'ml/scaler_land_registry.joblib')
    joblib.dump(price_scaler, 'ml/price_scaler_land_registry.joblib')

    print(f"  ✓ Model saved to ml/model_land_registry.h5")
    print(f"  ✓ Scaler saved to ml/scaler_land_registry.joblib")
    print(f"  ✓ Price scaler saved to ml/price_scaler_land_registry.joblib")

    print(f"\n✅ Training complete!")
    print(f"Next step: python app.py")
    print(f"The app will automatically use the Land Registry model!")

if __name__ == '__main__':
    train_model()
