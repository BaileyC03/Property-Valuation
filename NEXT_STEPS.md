# Next Steps - Once Model Training Completes

## Current Status
- ✅ Data downloaded and processed (574,226 real samples)
- ⏳ Model training in progress (Keras FCNN on real Land Registry data)
- ⏳ Estimated completion: Next 30-60 minutes

## What You Should Do Now

### Monitor Training Progress
Open a terminal and run:
```bash
cd /home/user/uk-property-valuation/backend
# Check if training process is still running
ps aux | grep train_model_land_registry

# Watch the last 50 lines of output
tail -50 /tmp/claude-1000/-home-user/tasks/b8df353.output
```

### Once Training Completes (files appear in backend/ml/)
You'll know it's done when you see these files created:
```bash
-rw-r--r-- backend/ml/model_land_registry.h5              (~10-15 MB)
-rw-r--r-- backend/ml/scaler_land_registry.joblib         (~1 KB)
-rw-r--r-- backend/ml/price_scaler_land_registry.joblib   (~1 KB)
```

### Quick Test Commands

```bash
# 1. Start the backend
cd backend
source venv/bin/activate
python app.py
# Should output:
#   ✓ Land Registry model loaded
#   Running on http://0.0.0.0:5000

# 2. In another terminal, test the API
curl http://localhost:5000/health

# 3. Get list of addresses
curl http://localhost:5000/addresses | head -20

# 4. Search for addresses
curl "http://localhost:5000/search?q=London"

# 5. Make a prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "address_id": 1,
    "beds": 3,
    "baths": 2,
    "ensuite": 1,
    "detached": 0
  }'
```

### Start the Frontend
```bash
cd frontend
npm start
# Opens at http://localhost:3000
```

## What This Model Does Differently

### Before (Synthetic Data)
- Model: Keras FCNN
- Training Data: Randomly generated properties
- Sample Size: 3,000 properties
- Average Error: ±£85,646
- Problem: Not realistic

### After (Real Land Registry Data) ⭐
- Model: Keras FCNN (same architecture)
- Training Data: Real UK government transactions
- Sample Size: 574,226 properties
- Average Error: TBD (will show after first run)
- Advantage: Based on actual market data

### The Data
- Source: HM Land Registry Price Paid Data
- Records: 1 million government property transactions
- After Cleaning: 574,226 valid records
- Coverage: All UK regions, all property types
- Price Range: £50k - £4.4M
- Property Types: Detached, Semi-detached, Terraced, Flat, Other

## File Structure After Training
```
backend/
├── app.py                           # Flask API (updated to use Land Registry model)
├── addresses.db                     # SQLite database with 1100+ predefined addresses
├── ml/
│   ├── process_land_registry.py     # Data processing script (completed)
│   ├── train_model_land_registry.py # Training script (completed)
│   ├── model_land_registry.h5       # ⭐ NEW REAL DATA MODEL
│   ├── scaler_land_registry.joblib  # Feature scaler
│   ├── price_scaler_land_registry.joblib  # Price unscaler
│   ├── model_keras.h5               # Old synthetic data model (fallback)
│   ├── scaler_keras.joblib          # Old synthetic scaler (fallback)
│   └── price_scaler_keras.joblib    # Old synthetic price scaler (fallback)
└── data/
    └── pp-complete.csv              # Your 5GB Land Registry file
```

## Expected Performance

### Accuracy Metrics You'll See
After training, the script will show:
```
📊 MODEL PERFORMANCE (with Land Registry data):
  Training MAE: £XX,XXX (±)
  Testing MAE:  £XX,XXX (±)
  Training R²:  0.XXXX
  Testing R²:   0.XXXX

  ✨ Real data accuracy: XX.X%

📈 IMPROVEMENT vs Synthetic Data:
  Before (synthetic): ±£85,646 MAE
  After (real data):  ±£XX,XXX MAE
  Improvement: XX.X%
```

These numbers show how well the model predicts actual property prices.

## Troubleshooting

### Model Training Failed
**Symptom**: No model_land_registry.h5 file created, error in output

**Solutions**:
1. Check if data file exists: `ls -lh backend/data/pp-complete.csv`
2. Check TensorFlow: `python -c "import tensorflow; print(tensorflow.__version__)"`
3. Check GPU (optional): `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`
4. Try smaller dataset: Edit `process_land_registry.py` line 290, change `nrows=1000000` to `nrows=100000`

### Models Don't Load in Backend
**Symptom**: `app.py` falls back to synthetic data model

**Solutions**:
1. Verify files exist: `ls backend/ml/model_land_registry.*`
2. Check file sizes (should be non-zero):
   ```bash
   ls -lh backend/ml/model_land_registry.h5
   ls -lh backend/ml/scaler_land_registry.joblib
   ```
3. Check for corruption: Try retraining

### Predictions Look Wrong
**Symptom**: Prices seem too high/low or unrealistic

**Possible causes**:
1. Model is still learning from synthetic data (not real model)
2. Address_id mapping is incorrect (would need to check database)
3. Feature scaling not working properly
4. Model didn't train long enough (early stopping)

**Solutions**:
1. Verify you're using Land Registry model: Check backend console for "Land Registry model loaded"
2. Test with known addresses and manually verify predictions
3. Retrain if needed: `python ml/train_model_land_registry.py`

## Key Improvements Made

### Code Changes
1. **process_land_registry.py**: Fixed date filtering to handle historical data
2. **app.py**: Added Land Registry model loading with priority system

### Data Pipeline
```
pp-complete.csv (5GB)
    ↓ [load in 50k chunks]
1,000,000 records loaded
    ↓ [clean & filter]
574,226 valid records
    ↓ [feature engineering]
land_registry_training.parquet
    ↓ [train Keras FCNN]
model_land_registry.h5
    ↓ [Flask API loads]
/predict endpoint returns real prices!
```

## Questions?

If anything goes wrong or you need help:
1. Check the LAND_REGISTRY_TRAINING_COMPLETE.md file
2. Review the training output: `tail -200 /tmp/claude-1000/-home-user/tasks/b8df353.output`
3. Look at the data processing output: `backend/land_registry_training.parquet` size/stats
4. Verify all dependencies: `pip list | grep -E "(tensorflow|keras|pandas|numpy)"`

---

**You're almost there!** Once training completes, your app will be using real government property data for valuations. This should be **significantly more accurate** than the synthetic data model.
