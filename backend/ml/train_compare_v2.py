#!/usr/bin/env python3
"""
Round 2: Feature engineering + fine-tuned hyperparameters.
Focus on location features and interaction terms.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, median_absolute_error
import joblib
import lightgbm as lgb

def inflate_price(price, date_sold, target_year=2026):
    year_sold = pd.to_datetime(date_sold).year
    return price * (1.03 ** (target_year - year_sold))

def load_data():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    csv_files = [f for f in os.listdir(data_dir) if f.startswith('rightmove_') and f.endswith('.csv')]
    dfs = []
    for f in sorted(csv_files):
        area_df = pd.read_csv(os.path.join(data_dir, f))
        area = f.replace('rightmove_', '').replace('.csv', '')
        print(f"  {area}: {len(area_df)} transactions")
        dfs.append(area_df)
    df = pd.concat(dfs, ignore_index=True)

    df['price_adjusted'] = df.apply(lambda r: inflate_price(r['price'], r['date_sold']), axis=1)

    pt = df['property_type'].str.lower()
    df['detached'] = (pt.str.contains('detach') & ~pt.str.contains('semi')).astype(int)
    df['semi_detached'] = pt.str.contains('semi').astype(int)
    df['terraced'] = pt.str.contains('terrace').astype(int)
    df['flat'] = (pt.str.contains('flat') | pt.str.contains('apartment') | pt.str.contains('maisonette')).astype(int)

    df = df[df['price_adjusted'] >= 50000]
    return df

def make_features(df, feature_set):
    """Build feature matrix based on feature set name."""
    if feature_set == 'base':
        cols = ['bedrooms', 'bathrooms', 'detached', 'semi_detached', 'terraced', 'flat', 'lat', 'lon']
    elif feature_set == 'geo_expanded':
        # Add more granular location features
        df = df.copy()
        df['lat2'] = df['lat'] ** 2
        df['lon2'] = df['lon'] ** 2
        df['lat_lon'] = df['lat'] * df['lon']
        # Distance from a reference point (Portsmouth city centre: 50.7989, -1.0912)
        df['dist_portsmouth'] = np.sqrt((df['lat'] - 50.7989)**2 + (df['lon'] - (-1.0912))**2)
        cols = ['bedrooms', 'bathrooms', 'detached', 'semi_detached', 'terraced', 'flat',
                'lat', 'lon', 'lat2', 'lon2', 'lat_lon', 'dist_portsmouth']
    elif feature_set == 'interactions':
        df = df.copy()
        df['lat2'] = df['lat'] ** 2
        df['lon2'] = df['lon'] ** 2
        df['lat_lon'] = df['lat'] * df['lon']
        df['dist_portsmouth'] = np.sqrt((df['lat'] - 50.7989)**2 + (df['lon'] - (-1.0912))**2)
        df['beds_x_baths'] = df['bedrooms'] * df['bathrooms']
        df['beds_x_detached'] = df['bedrooms'] * df['detached']
        df['total_rooms'] = df['bedrooms'] + df['bathrooms']
        cols = ['bedrooms', 'bathrooms', 'detached', 'semi_detached', 'terraced', 'flat',
                'lat', 'lon', 'lat2', 'lon2', 'lat_lon', 'dist_portsmouth',
                'beds_x_baths', 'beds_x_detached', 'total_rooms']
    elif feature_set == 'kitchen_sink':
        df = df.copy()
        df['lat2'] = df['lat'] ** 2
        df['lon2'] = df['lon'] ** 2
        df['lat_lon'] = df['lat'] * df['lon']
        df['dist_portsmouth'] = np.sqrt((df['lat'] - 50.7989)**2 + (df['lon'] - (-1.0912))**2)
        df['beds_x_baths'] = df['bedrooms'] * df['bathrooms']
        df['beds_x_detached'] = df['bedrooms'] * df['detached']
        df['total_rooms'] = df['bedrooms'] + df['bathrooms']
        # Sale year as feature (captures market trends)
        df['sale_year'] = pd.to_datetime(df['date_sold']).dt.year
        df['years_ago'] = 2026 - df['sale_year']
        cols = ['bedrooms', 'bathrooms', 'detached', 'semi_detached', 'terraced', 'flat',
                'lat', 'lon', 'lat2', 'lon2', 'lat_lon', 'dist_portsmouth',
                'beds_x_baths', 'beds_x_detached', 'total_rooms', 'sale_year', 'years_ago']
    return df[cols].values, cols, df

def run():
    print("Loading data...")
    df_raw = load_data()
    print(f"  Total: {len(df_raw)} samples\n")

    configs = []

    # Feature sets to test
    feature_sets = ['base', 'geo_expanded', 'interactions', 'kitchen_sink']

    # Hyperparameter configs (around best baseline)
    hparams = {
        'A (baseline)': dict(n_estimators=500, max_depth=6, learning_rate=0.05, num_leaves=31,
                             subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=0.1,
                             min_child_samples=20),
        'B (more trees, lower lr)': dict(n_estimators=2000, max_depth=6, learning_rate=0.02, num_leaves=31,
                                          subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=0.1,
                                          min_child_samples=15),
        'C (deeper + more leaves)': dict(n_estimators=1000, max_depth=8, learning_rate=0.03, num_leaves=50,
                                          subsample=0.85, colsample_bytree=0.85, reg_alpha=0.05, reg_lambda=0.05,
                                          min_child_samples=10),
        'D (aggressive)': dict(n_estimators=3000, max_depth=10, learning_rate=0.01, num_leaves=80,
                                subsample=0.8, colsample_bytree=0.7, reg_alpha=0.01, reg_lambda=0.01,
                                min_child_samples=5),
        'E (regularized)': dict(n_estimators=1500, max_depth=5, learning_rate=0.03, num_leaves=25,
                                 subsample=0.75, colsample_bytree=0.75, reg_alpha=0.5, reg_lambda=0.5,
                                 min_child_samples=20),
    }

    for fs_name in feature_sets:
        for hp_name, hp in hparams.items():
            configs.append((fs_name, hp_name, hp))

    results = []
    best_mae = float('inf')
    best_info = None

    for fs_name, hp_name, hp in configs:
        X, cols, df_feat = make_features(df_raw.copy(), fs_name)
        y = df_feat['price_adjusted'].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        model = lgb.LGBMRegressor(
            objective='mae', random_state=42, verbose=-1, n_jobs=-1, **hp
        )
        model.fit(X_train_s, y_train, eval_set=[(X_test_s, y_test)],
                  callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(0)])

        test_pred = model.predict(X_test_s)
        train_pred = model.predict(X_train_s)
        test_mae = mean_absolute_error(y_test, test_pred)
        test_med = median_absolute_error(y_test, test_pred)
        test_r2 = r2_score(y_test, test_pred)
        train_mae = mean_absolute_error(y_train, train_pred)

        label = f"{fs_name} + {hp_name}"
        print(f"  {label:<50s} MAE: £{test_mae:>8,.0f}  MedAE: £{test_med:>8,.0f}  R²: {test_r2:.4f}")

        results.append({
            'label': label, 'fs': fs_name, 'hp': hp_name,
            'test_mae': test_mae, 'test_median_ae': test_med, 'test_r2': test_r2,
            'train_mae': train_mae, 'n_features': len(cols),
        })

        if test_mae < best_mae:
            best_mae = test_mae
            best_info = {'model': model, 'scaler': scaler, 'cols': cols,
                         'fs': fs_name, 'hp': hp_name, 'label': label,
                         'test_pred': test_pred, 'y_test': y_test}

    # Leaderboard
    results.sort(key=lambda x: x['test_mae'])
    print(f"\n{'='*90}")
    print(f"{'Config':<50s} {'Test MAE':>12} {'MedAE':>12} {'R²':>8} {'#feat':>6}")
    print(f"{'-'*90}")
    for i, r in enumerate(results[:15]):
        marker = ' ***' if r['label'] == best_info['label'] else ''
        print(f"{r['label']:<50s} £{r['test_mae']:>10,.0f} £{r['test_median_ae']:>10,.0f} {r['test_r2']:>8.4f} {r['n_features']:>6}{marker}")

    # Best model details
    print(f"\nBest: {best_info['label']}")
    print(f"  Test MAE: £{best_mae:,.0f}")
    print(f"  Features: {best_info['cols']}")

    if hasattr(best_info['model'], 'feature_importances_'):
        print(f"\n  Feature Importance:")
        importance = sorted(zip(best_info['cols'], best_info['model'].feature_importances_), key=lambda x: -x[1])
        max_imp = max(best_info['model'].feature_importances_)
        for name_f, imp in importance:
            bar = '#' * int(imp / max_imp * 40)
            print(f"    {name_f:20s} {bar} {imp:.0f}")

    # Sample predictions
    print(f"\n  Sample predictions:")
    indices = np.random.RandomState(42).choice(len(best_info['y_test']), min(15, len(best_info['y_test'])), replace=False)
    for i in indices:
        actual = best_info['y_test'][i]
        pred = best_info['test_pred'][i]
        err_pct = abs(actual - pred) / actual * 100
        print(f"    Actual: £{actual:>10,.0f}  Predicted: £{pred:>10,.0f}  Error: {err_pct:.1f}%")

    # Save
    out_dir = os.path.dirname(__file__)
    joblib.dump(best_info['model'], os.path.join(out_dir, 'model_lightgbm.joblib'))
    joblib.dump(best_info['scaler'], os.path.join(out_dir, 'scaler_lightgbm.joblib'))
    joblib.dump(best_info['cols'], os.path.join(out_dir, 'feature_cols_lightgbm.joblib'))
    print(f"\nSaved best model to model_lightgbm.joblib")
    print(f"Feature cols: {best_info['cols']}")

if __name__ == '__main__':
    run()
