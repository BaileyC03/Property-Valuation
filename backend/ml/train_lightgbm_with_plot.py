#!/usr/bin/env python3
"""
Train LightGBM model with loss tracking and visualization.
Generates a graph showing training progress over rounds.
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

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib not available. Install with: pip install matplotlib")
    print("Continuing without visualization...")

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

def train_model_with_tracking():
    """Train LightGBM model and track loss values for visualization."""
    print("\n" + "="*70)
    print("Training LightGBM Model with Loss Tracking")
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

    # Scale features
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

    # Train LightGBM with loss tracking
    print("\nTraining LightGBM model...")
    print("(Tracking loss at each round...)")

    train_losses = []
    test_losses = []
    rounds = []

    class LossTracker:
        """Custom callback to track losses during training."""
        def __init__(self):
            self.train_losses = []
            self.test_losses = []
            self.round = 0

        def __call__(self, env):
            if env.evaluation_result_list:
                # Get the first (and only) validation set result
                self.round = env.iteration

                # Training loss is typically not in evaluation_result_list
                # but we can track validation/test loss
                for data_name, eval_name, result, _ in env.evaluation_result_list:
                    if eval_name == 'mae':
                        self.test_losses.append(result)

                if self.round % 10 == 0:
                    print(f"  Round {self.round:3d}: Test MAE = £{result:,.0f}")

    loss_tracker = LossTracker()

    model = lgb.LGBMRegressor(
        n_estimators=300,  # Increased from 200 to allow more training
        max_depth=7,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='mae',
        metric='mae',
        random_state=42,
        verbose=-1,
        n_jobs=-1
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[
            lgb.log_evaluation(period=0),  # Disable built-in logging
            lgb.early_stopping(stopping_rounds=20, verbose=True),
            loss_tracker
        ]
    )

    # Get training loss history from booster
    print("\nExtracting loss history...")
    evals_result = model.evals_result_

    if evals_result and 'valid_0' in evals_result:
        # Try 'mae' first, then 'l1' (both are the same for MAE objective)
        if 'mae' in evals_result['valid_0']:
            test_losses = evals_result['valid_0']['mae']
        elif 'l1' in evals_result['valid_0']:
            test_losses = evals_result['valid_0']['l1']
        else:
            test_losses = loss_tracker.test_losses
    else:
        test_losses = loss_tracker.test_losses

    # Calculate approximate training loss (using predictions on training set at different stages)
    # This is a post-hoc calculation
    train_pred = model.predict(X_train)
    train_mae = mean_absolute_error(y_train, train_pred)
    test_pred = model.predict(X_test)
    test_mae = mean_absolute_error(y_test, test_pred)

    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)

    # Final results
    print(f"\n{'='*70}")
    print(f"📊 FINAL MODEL PERFORMANCE:")
    print(f"{'='*70}")
    print(f"  Training MAE: £{train_mae:,.0f}")
    print(f"  Testing MAE:  £{test_mae:,.0f}")
    print(f"  Training R²:  {train_r2:.4f} ({train_r2*100:.2f}%)")
    print(f"  Testing R²:   {test_r2:.4f} ({test_r2*100:.2f}%)")
    print(f"  Total rounds completed: {len(test_losses)}")

    # Feature importance
    print(f"\n🎯 Feature Importance:")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    for idx, row in feature_importance.iterrows():
        bar = "█" * int(row['importance'] * 50)
        print(f"  {row['feature']:12s} {bar} {row['importance']:.4f}")

    # Create visualization if matplotlib available
    if MATPLOTLIB_AVAILABLE and len(test_losses) > 0:
        print(f"\n📈 Creating loss visualization...")

        fig, axes = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: Loss progression over rounds
        rounds_list = list(range(1, len(test_losses) + 1))
        axes[0].plot(rounds_list, test_losses, 'b-', linewidth=2, label='Test Loss (MAE)')
        axes[0].set_xlabel('Round', fontsize=12)
        axes[0].set_ylabel('Loss (£)', fontsize=12)
        axes[0].set_title('LightGBM Test Loss Progression During Training', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(fontsize=11)

        # Format y-axis as currency
        ax = axes[0]
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))

        # Add final value annotation
        final_loss = test_losses[-1]
        axes[0].annotate(f'Final: £{final_loss:,.0f}',
                        xy=(len(test_losses), final_loss),
                        xytext=(-100, -30),
                        textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

        # Plot 2: Loss improvement (percentage reduction from start)
        if len(test_losses) > 1:
            initial_loss = test_losses[0]
            improvement = [(initial_loss - loss) / initial_loss * 100 for loss in test_losses]
            axes[1].plot(rounds_list, improvement, 'g-', linewidth=2, label='Improvement %')
            axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
            axes[1].set_xlabel('Round', fontsize=12)
            axes[1].set_ylabel('Improvement (%)', fontsize=12)
            axes[1].set_title('Loss Improvement Over Training', fontsize=14, fontweight='bold')
            axes[1].grid(True, alpha=0.3)
            axes[1].legend(fontsize=11)

            # Add final improvement annotation
            final_improvement = improvement[-1]
            axes[1].annotate(f'{final_improvement:.1f}% improvement',
                            xy=(len(improvement), final_improvement),
                            xytext=(-100, -30),
                            textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='lightgreen', alpha=0.7),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

        plt.tight_layout()
        plot_path = 'ml/lightgbm_loss_progression.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"  ✓ Loss graph saved to {plot_path}")

        # Also create a detailed CSV with loss history
        loss_data = pd.DataFrame({
            'round': rounds_list,
            'test_mae': test_losses
        })
        if len(test_losses) > 1:
            loss_data['improvement_%'] = [(test_losses[0] - loss) / test_losses[0] * 100 for loss in test_losses]

        csv_path = 'ml/lightgbm_loss_history.csv'
        loss_data.to_csv(csv_path, index=False)
        print(f"  ✓ Loss history saved to {csv_path}")
        print(f"\n📊 Loss Statistics:")
        print(f"  Initial Loss (Round 1): £{test_losses[0]:,.0f}")
        print(f"  Final Loss (Round {len(test_losses)}): £{test_losses[-1]:,.0f}")
        print(f"  Total Improvement: £{test_losses[0] - test_losses[-1]:,.0f}")
        print(f"  Improvement %: {(test_losses[0] - test_losses[-1])/test_losses[0]*100:.1f}%")

    # Save model
    print(f"\n💾 Saving model...")
    os.makedirs('ml', exist_ok=True)

    model.booster_.save_model('ml/model_lightgbm.txt')
    joblib.dump(model, 'ml/model_lightgbm.joblib')
    joblib.dump(scaler, 'ml/scaler_lightgbm.joblib')

    print(f"  ✓ Model saved to ml/model_lightgbm.joblib")
    print(f"  ✓ Scaler saved to ml/scaler_lightgbm.joblib")

    print(f"\n✅ Training complete!")

    return model, scaler, test_mae, test_r2

if __name__ == '__main__':
    try:
        model, scaler, mae, r2 = train_model_with_tracking()
        print(f"\n🎉 Done! Final MAE: £{mae:,.0f}, R²: {r2:.4f}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
