#!/usr/bin/env python3
"""
Compare multiple models and hyperparameter configs on Rightmove data.
80/20 train/test split, evaluate on held-out test set.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, median_absolute_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
import joblib
import lightgbm as lgb
import xgboost as xgb

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
    print(f"  Total: {len(df)} transactions\n")

    # Inflate
    df['price_adjusted'] = df.apply(lambda r: inflate_price(r['price'], r['date_sold']), axis=1)

    # Property type encoding
    pt = df['property_type'].str.lower()
    df['detached'] = (pt.str.contains('detach') & ~pt.str.contains('semi')).astype(int)
    df['semi_detached'] = pt.str.contains('semi').astype(int)
    df['terraced'] = pt.str.contains('terrace').astype(int)
    df['flat'] = (pt.str.contains('flat') | pt.str.contains('apartment') | pt.str.contains('maisonette')).astype(int)

    # Filter noise
    df = df[df['price_adjusted'] >= 50000]
    return df

def run():
    print("Loading data...")
    df = load_data()

    feature_cols = ['bedrooms', 'bathrooms', 'detached', 'semi_detached', 'terraced', 'flat', 'lat', 'lon']
    X = df[feature_cols].values
    y = df['price_adjusted'].values

    # Fixed 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}\n")

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # ---- Models to compare ----
    models = {}

    # LightGBM variants
    models['LightGBM (baseline)'] = lgb.LGBMRegressor(
        n_estimators=500, max_depth=6, learning_rate=0.05, num_leaves=31,
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=0.1,
        objective='mae', random_state=42, verbose=-1, n_jobs=-1,
    )
    models['LightGBM (deeper)'] = lgb.LGBMRegressor(
        n_estimators=1000, max_depth=10, learning_rate=0.03, num_leaves=63,
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.05, reg_lambda=0.05,
        min_child_samples=5, objective='mae', random_state=42, verbose=-1, n_jobs=-1,
    )
    models['LightGBM (huber)'] = lgb.LGBMRegressor(
        n_estimators=1000, max_depth=8, learning_rate=0.03, num_leaves=50,
        subsample=0.85, colsample_bytree=0.85, reg_alpha=0.1, reg_lambda=0.1,
        min_child_samples=5, objective='huber', random_state=42, verbose=-1, n_jobs=-1,
    )
    models['LightGBM (low lr)'] = lgb.LGBMRegressor(
        n_estimators=2000, max_depth=7, learning_rate=0.01, num_leaves=40,
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.05, reg_lambda=0.1,
        min_child_samples=3, objective='mae', random_state=42, verbose=-1, n_jobs=-1,
    )

    # XGBoost variants
    models['XGBoost (mae)'] = xgb.XGBRegressor(
        n_estimators=1000, max_depth=7, learning_rate=0.03, subsample=0.8,
        colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=0.1,
        objective='reg:absoluteerror', random_state=42, verbosity=0, n_jobs=-1,
    )
    models['XGBoost (huber)'] = xgb.XGBRegressor(
        n_estimators=1000, max_depth=8, learning_rate=0.03, subsample=0.85,
        colsample_bytree=0.85, reg_alpha=0.05, reg_lambda=0.05,
        objective='reg:pseudohubererror', random_state=42, verbosity=0, n_jobs=-1,
    )

    # Sklearn ensembles
    models['RandomForest (500)'] = RandomForestRegressor(
        n_estimators=500, max_depth=12, min_samples_leaf=3,
        random_state=42, n_jobs=-1,
    )
    models['ExtraTrees (500)'] = ExtraTreesRegressor(
        n_estimators=500, max_depth=12, min_samples_leaf=3,
        random_state=42, n_jobs=-1,
    )
    models['GradientBoosting (500)'] = GradientBoostingRegressor(
        n_estimators=500, max_depth=6, learning_rate=0.05,
        subsample=0.8, loss='absolute_error', random_state=42,
    )

    # ---- Train & evaluate ----
    results = []
    best_mae = float('inf')
    best_name = None
    best_model = None

    for name, model in models.items():
        print(f"Training {name}...", end=' ', flush=True)

        # Use early stopping for boosting models
        if isinstance(model, lgb.LGBMRegressor):
            model.fit(X_train_s, y_train, eval_set=[(X_test_s, y_test)],
                      callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(0)])
        elif isinstance(model, xgb.XGBRegressor):
            model.fit(X_train_s, y_train, eval_set=[(X_test_s, y_test)],
                      verbose=False)
        else:
            model.fit(X_train_s, y_train)

        test_pred = model.predict(X_test_s)
        train_pred = model.predict(X_train_s)

        test_mae = mean_absolute_error(y_test, test_pred)
        test_med = median_absolute_error(y_test, test_pred)
        test_r2 = r2_score(y_test, test_pred)
        train_mae = mean_absolute_error(y_train, train_pred)
        train_r2 = r2_score(y_train, train_pred)

        results.append({
            'name': name, 'test_mae': test_mae, 'test_median_ae': test_med,
            'test_r2': test_r2, 'train_mae': train_mae, 'train_r2': train_r2,
        })

        if test_mae < best_mae:
            best_mae = test_mae
            best_name = name
            best_model = model

        print(f"MAE: £{test_mae:,.0f}  MedAE: £{test_med:,.0f}  R²: {test_r2:.4f}")

    # ---- Leaderboard ----
    results.sort(key=lambda x: x['test_mae'])
    print(f"\n{'='*80}")
    print(f"{'Model':<30} {'Test MAE':>12} {'MedAE':>12} {'Test R²':>10} {'Train MAE':>12} {'Train R²':>10}")
    print(f"{'-'*80}")
    for r in results:
        marker = ' <-- BEST' if r['name'] == best_name else ''
        print(f"{r['name']:<30} £{r['test_mae']:>10,.0f} £{r['test_median_ae']:>10,.0f} {r['test_r2']:>10.4f} £{r['train_mae']:>10,.0f} {r['train_r2']:>10.4f}{marker}")

    # ---- Feature importance for best model ----
    print(f"\nBest model: {best_name}")
    if hasattr(best_model, 'feature_importances_'):
        print(f"\nFeature Importance:")
        importance = sorted(zip(feature_cols, best_model.feature_importances_), key=lambda x: -x[1])
        max_imp = max(best_model.feature_importances_)
        for name_f, imp in importance:
            bar = '#' * int(imp / max_imp * 40)
            print(f"  {name_f:16s} {bar} {imp:.1f}")

    # ---- Sample predictions from best ----
    test_pred = best_model.predict(X_test_s)
    print(f"\nSample predictions ({best_name}):")
    indices = np.random.RandomState(42).choice(len(X_test), min(15, len(X_test)), replace=False)
    for i in indices:
        actual = y_test[i]
        pred = test_pred[i]
        err_pct = abs(actual - pred) / actual * 100
        print(f"  Actual: £{actual:>10,.0f}  Predicted: £{pred:>10,.0f}  Error: {err_pct:.1f}%")

    # ---- Save best ----
    out_dir = os.path.dirname(__file__)
    joblib.dump(best_model, os.path.join(out_dir, 'model_lightgbm.joblib'))
    joblib.dump(scaler, os.path.join(out_dir, 'scaler_lightgbm.joblib'))
    joblib.dump(feature_cols, os.path.join(out_dir, 'feature_cols_lightgbm.joblib'))
    print(f"\nSaved best model ({best_name}) to model_lightgbm.joblib")

if __name__ == '__main__':
    run()
