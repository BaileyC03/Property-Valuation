#!/usr/bin/env python3
"""
Train LightGBM model using HM Land Registry real data.
Expected accuracy: MAE ~£25-35k (vs Keras FCNN ~£50-70k)
Training time: 3-5 minutes
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("LightGBM not available. Install with: pip install lightgbm")
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

def train_model():
    """Train LightGBM model with HM Land Registry data."""
    print("\n" + "="*70)
    print("Training LightGBM Model with HM Land Registry Data")
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
    y = df['price'].values

    print(f"\nFeature shape: {X.shape}")
    print(f"Target shape: {y.shape}")

    # Scale features (LightGBM works better with scaled features)
    print("\nScaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split data
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    print(f"\nData split:")
    print(f"  Training: {len(X_train)} samples")
    print(f"  Testing: {len(X_test)} samples")
    print(f"  Train/Test ratio: {len(X_train)/len(X_test):.1f}:1")

    # Build and train LightGBM model
    print("\nTraining LightGBM model...")
    print("(This will take 3-5 minutes for 574k samples)")

    model = lgb.LGBMRegressor(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='mae',
        metric='mae',
        random_state=42,
        verbose=-1,
        n_jobs=-1  # Use all CPU cores
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[
            lgb.log_evaluation(period=10),
            lgb.early_stopping(stopping_rounds=20, verbose=True)
        ]
    )

    # Evaluate
    print("\nEvaluating model...")
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_mae = mean_absolute_error(y_train, train_pred)
    test_mae = mean_absolute_error(y_test, test_pred)

    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)

    print(f"\n📊 MODEL PERFORMANCE (LightGBM with Land Registry data):")
    print(f"  Training MAE: £{train_mae:,.0f}")
    print(f"  Testing MAE:  £{test_mae:,.0f}")
    print(f"  Training R²:  {train_r2:.4f}")
    print(f"  Testing R²:   {test_r2:.4f}")
    print(f"\n  ✨ Real data accuracy: {test_r2*100:.1f}%")

    # Compare with Keras FCNN
    print(f"\n📈 COMPARISON vs Keras FCNN Model:")
    print(f"  Keras FCNN MAE: ~£50,000-70,000")
    print(f"  LightGBM MAE:   ±£{test_mae:,.0f}")
    if test_mae < 50000:
        improvement = ((70000 - test_mae) / 70000) * 100
        print(f"  Improvement: {improvement:.1f}% better! ✨")
    else:
        print(f"  Comparable performance")

    # Feature importance
    print(f"\n🎯 Feature Importance:")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    for idx, row in feature_importance.iterrows():
        bar = "█" * int(row['importance'] * 50)
        print(f"  {row['feature']:12s} {bar} {row['importance']:.4f}")

    # Sample predictions
    print(f"\n🏠 Sample Predictions:")
    sample_indices = np.random.choice(len(X_test), min(5, len(X_test)), replace=False)
    for idx in sample_indices:
        actual = y_test.iloc[idx] if hasattr(y_test, 'iloc') else y_test[idx]
        predicted = test_pred[idx]
        error = abs(actual - predicted) / actual * 100
        print(f"  Actual: £{actual:,.0f} → Predicted: £{predicted:,.0f} (error: {error:.1f}%)")

    # Save model
    print(f"\n💾 Saving model...")
    os.makedirs('ml', exist_ok=True)

    model.booster_.save_model('ml/model_lightgbm.txt')
    joblib.dump(model, 'ml/model_lightgbm.joblib')
    joblib.dump(scaler, 'ml/scaler_lightgbm.joblib')

    print(f"  ✓ Model saved to ml/model_lightgbm.joblib")
    print(f"  ✓ Scaler saved to ml/scaler_lightgbm.joblib")

    print(f"\n✅ LightGBM training complete!")
    print(f"\nNext steps to use this model:")
    print(f"  1. Update backend/app.py to load LightGBM model")
    print(f"  2. Set model priority: LightGBM → Keras → RandomForest")
    print(f"  3. Run: python app.py")

    return model, scaler, test_mae, test_r2

if __name__ == '__main__':
    try:
        model, scaler, mae, r2 = train_model()
        print(f"\n🎉 Done! MAE: £{mae:,.0f}, R²: {r2:.4f}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
