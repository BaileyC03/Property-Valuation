#!/usr/bin/env python3
"""
ML training script for UK property valuation model.
Trains a random forest model on synthetic property data based on Land Registry insights.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

def generate_synthetic_data(n_samples=5000):
    """
    Generate synthetic property data inspired by UK Land Registry patterns.
    Real data would come from: https://www.gov.uk/government/organisations/land-registry
    """
    np.random.seed(42)

    # Bedrooms: 1-8 (most properties are 2-4)
    beds = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.35, 0.35, 0.15, 0.05])

    # Bathrooms: typically 1 per 2 beds + 0.5
    baths = (beds / 2 + np.random.uniform(0.5, 1.5, n_samples)).astype(int)
    baths = np.maximum(baths, 1)  # At least 1

    # Ensuite bathrooms: usually 0-1, sometimes 2
    ensuite = np.random.choice([0, 1, 2], n_samples, p=[0.6, 0.3, 0.1])
    ensuite = np.minimum(ensuite, baths - 1)  # Can't exceed total baths

    # Detached property: 40% are detached
    detached = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])

    # Latitude/Longitude: UK bounds
    # Northern Scotland: ~57.5, Southern coast: ~50.0
    # Western Wales: ~-5.0, Eastern England: ~1.5
    lat = np.random.uniform(50.0, 57.5, n_samples)
    lon = np.random.uniform(-5.0, 1.5, n_samples)

    # Generate prices with regional variation
    # Base price from property characteristics
    base_price = 150000  # Base price
    bed_factor = beds * 80000
    bath_factor = baths * 30000
    ensuite_factor = ensuite * 20000
    detached_factor = detached * 100000

    # Regional multiplier (London and SE England are more expensive)
    # Simple model: closer to London (51.5, -0.1), more expensive
    london_distance = np.sqrt((lat - 51.5)**2 + (lon + 0.1)**2)
    regional_multiplier = 1.0 + (2.5 - london_distance) * 0.3
    regional_multiplier = np.clip(regional_multiplier, 0.7, 2.5)

    prices = (base_price + bed_factor + bath_factor + ensuite_factor + detached_factor) * regional_multiplier

    # Add noise
    noise = np.random.normal(1.0, 0.15, n_samples)
    prices = prices * noise
    prices = np.clip(prices, 100000, 5000000)  # Realistic bounds

    return pd.DataFrame({
        'beds': beds,
        'baths': baths,
        'ensuite': ensuite,
        'detached': detached,
        'lat': lat,
        'lon': lon,
        'price': prices.astype(int)
    })

def train_model():
    """Train the ML model and save it."""
    print("Generating synthetic property data...")
    df = generate_synthetic_data(n_samples=5000)

    print(f"Generated {len(df)} property records")
    print("\nData sample:")
    print(df.head(10))
    print("\nData statistics:")
    print(df.describe())

    # Prepare features and target
    feature_cols = ['beds', 'baths', 'ensuite', 'detached', 'lat', 'lon']
    X = df[feature_cols].values
    y = df['price'].values

    print(f"\nTraining random forest model...")
    print(f"Features: {feature_cols}")
    print(f"Target: price")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train_scaled, y_train)

    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)

    print(f"\nModel Performance:")
    print(f"  Training R² score: {train_score:.4f}")
    print(f"  Testing R² score:  {test_score:.4f}")

    # Feature importance
    print(f"\nFeature Importance:")
    for col, importance in zip(feature_cols, model.feature_importances_):
        print(f"  {col}: {importance:.4f}")

    # Save model and scaler
    os.makedirs('ml', exist_ok=True)

    model_path = 'ml/model.joblib'
    scaler_path = 'ml/scaler.joblib'

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    print(f"\n✓ Model saved to {model_path}")
    print(f"✓ Scaler saved to {scaler_path}")

    # Test prediction
    print(f"\nTest Predictions:")
    test_samples = [
        {'beds': 3, 'baths': 2, 'ensuite': 1, 'detached': 1, 'lat': 51.5, 'lon': -0.1},  # London detached
        {'beds': 2, 'baths': 1, 'ensuite': 0, 'detached': 0, 'lat': 53.5, 'lon': -2.0},   # Manchester terrace
        {'beds': 4, 'baths': 2, 'ensuite': 1, 'detached': 0, 'lat': 52.0, 'lon': -1.0},   # Midlands semi
    ]

    for i, sample in enumerate(test_samples, 1):
        X_sample = np.array([[sample['beds'], sample['baths'], sample['ensuite'],
                             sample['detached'], sample['lat'], sample['lon']]])
        X_sample_scaled = scaler.transform(X_sample)
        pred = model.predict(X_sample_scaled)[0]
        print(f"  Sample {i}: {sample['beds']}bed, {sample['baths']}bath - £{pred:,.0f}")

if __name__ == '__main__':
    train_model()
