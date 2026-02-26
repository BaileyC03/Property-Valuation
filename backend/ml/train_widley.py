#!/usr/bin/env python3
"""
Train LightGBM model on scraped Rightmove data (Widley + Stamshaw + any other areas).
Uses real beds, baths, property type, lat/lon, and inflation-adjusted prices.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, median_absolute_error
import joblib

try:
    import lightgbm as lgb
except ImportError:
    print("LightGBM not available. Install with: pip install lightgbm")
    exit(1)

def inflate_price(price, date_sold, target_year=2026):
    """Adjust historical prices to present-day values using 3% annual inflation."""
    year_sold = pd.to_datetime(date_sold).year
    years_diff = target_year - year_sold
    return price * (1.03 ** years_diff)

def train():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

    # Load all rightmove CSVs
    csv_files = [f for f in os.listdir(data_dir) if f.startswith('rightmove_') and f.endswith('.csv')]
    if not csv_files:
        print(f"Error: No rightmove_*.csv files found in {data_dir}")
        exit(1)

    dfs = []
    for f in sorted(csv_files):
        path = os.path.join(data_dir, f)
        area_df = pd.read_csv(path)
        area_name = f.replace('rightmove_', '').replace('.csv', '')
        print(f"  {area_name}: {len(area_df)} transactions from {area_df['address'].nunique()} properties")
        dfs.append(area_df)

    df = pd.concat(dfs, ignore_index=True)
    print(f"\nCombined: {len(df)} transactions from {df['address'].nunique()} properties")
    print(f"Price range: {df['price'].min():,} - {df['price'].max():,}")
    print(f"Bedrooms: {df['bedrooms'].min()} - {df['bedrooms'].max()}")
    print(f"Property types: {df['property_type'].value_counts().to_dict()}")

    # Inflate prices to 2026
    df['price_adjusted'] = df.apply(lambda r: inflate_price(r['price'], r['date_sold']), axis=1)
    print(f"\nInflation-adjusted price range: {df['price_adjusted'].min():,.0f} - {df['price_adjusted'].max():,.0f}")
    print(f"Mean adjusted price: {df['price_adjusted'].mean():,.0f}")

    # Encode property type as binary: detached=1, else=0
    df['detached'] = df['property_type'].str.lower().str.contains('detach').astype(int)
    # Also encode semi-detached separately for more granularity
    df['semi_detached'] = df['property_type'].str.lower().apply(
        lambda x: 1 if 'semi' in x else 0
    )
    df['terraced'] = df['property_type'].str.lower().apply(
        lambda x: 1 if 'terrace' in x else 0
    )
    df['flat'] = df['property_type'].str.lower().apply(
        lambda x: 1 if 'flat' in x or 'apartment' in x or 'maisonette' in x else 0
    )

    # Filter out very old/cheap transactions that might be noise even after inflation
    df = df[df['price_adjusted'] >= 50000]
    print(f"After filtering < 50k adjusted: {len(df)} transactions")

    # Features
    feature_cols = ['bedrooms', 'bathrooms', 'detached', 'semi_detached', 'terraced', 'flat', 'lat', 'lon']
    X = df[feature_cols].values
    y = df['price_adjusted'].values

    print(f"\nFeatures: {feature_cols}")
    print(f"Samples: {len(X)}")

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Train LightGBM
    print("\nTraining LightGBM...")
    model = lgb.LGBMRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=0.1,
        objective='mae',
        metric='mae',
        random_state=42,
        verbose=-1,
        n_jobs=-1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[
            lgb.log_evaluation(period=50),
            lgb.early_stopping(stopping_rounds=30, verbose=True)
        ]
    )

    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_mae = mean_absolute_error(y_train, train_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    test_median_ae = median_absolute_error(y_test, test_pred)
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)

    print(f"\nResults:")
    print(f"  Train MAE: {train_mae:,.0f}  R2: {train_r2:.4f}")
    print(f"  Test  MAE: {test_mae:,.0f}  R2: {test_r2:.4f}")
    print(f"  Test  Median AE: {test_median_ae:,.0f}")

    # Feature importance
    print(f"\nFeature Importance:")
    importance = sorted(zip(feature_cols, model.feature_importances_), key=lambda x: -x[1])
    for name, imp in importance:
        bar = '#' * int(imp / max(model.feature_importances_) * 30)
        print(f"  {name:16s} {bar} {imp}")

    # Sample predictions
    print(f"\nSample predictions:")
    indices = np.random.RandomState(42).choice(len(X_test), min(10, len(X_test)), replace=False)
    for i in indices:
        actual = y_test[i]
        pred = test_pred[i]
        err_pct = abs(actual - pred) / actual * 100
        print(f"  Actual: {actual:>10,.0f}  Predicted: {pred:>10,.0f}  Error: {err_pct:.1f}%")

    # Save model
    out_dir = os.path.dirname(__file__)
    joblib.dump(model, os.path.join(out_dir, 'model_lightgbm.joblib'))
    joblib.dump(scaler, os.path.join(out_dir, 'scaler_lightgbm.joblib'))

    # Save feature column names for the backend to know
    joblib.dump(feature_cols, os.path.join(out_dir, 'feature_cols_lightgbm.joblib'))

    print(f"\nSaved model_lightgbm.joblib, scaler_lightgbm.joblib, feature_cols_lightgbm.joblib")
    print("Done!")

if __name__ == '__main__':
    train()
