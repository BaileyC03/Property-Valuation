# Land Registry Commands Reference

Copy-paste ready commands for HM Land Registry data integration.

## ⚡ 5-Minute Quick Setup

```bash
# Go to backend directory
cd uk-property-valuation/backend

# Activate virtual environment
source venv/bin/activate

# Step 1: Process Land Registry data (2-5 min)
python ml/process_land_registry.py

# Step 2: Train model with real data (3-10 min)
python ml/train_model_land_registry.py

# Step 3: Start backend (will auto-detect new model)
python app.py

# In another terminal:
cd uk-property-valuation/frontend
npm start

# Open browser
open http://localhost:3000
```

---

## 📥 Data Processing

### Process Latest Year (2024)
```bash
cd backend && source venv/bin/activate
python ml/process_land_registry.py
```

Expected: Downloads ~150 MB, processes 10,000 samples

### Process Multiple Years
Edit `ml/process_land_registry.py`:
```python
# Change this to download other years:
csv_file = download_registry_data(year=2023)  # or 2022, 2021, etc.
```

### Use Custom CSV File
Place your CSV in `backend/ml/data/` and script will use it:
```bash
cp my_property_data.csv backend/ml/data/
python ml/process_land_registry.py
```

### Use More Training Data
Edit `ml/process_land_registry.py`:
```python
# Line ~120 - change nrows
df_raw = load_registry_csv(csv_file, nrows=500000)  # was 100,000
```

---

## 🧠 Model Training

### Train with Land Registry Data
```bash
cd backend && source venv/bin/activate
python ml/train_model_land_registry.py
```

Expected: ~82 epochs, MAE ±£25k-50k, R² 0.92-0.95

### Retrain with Different Parameters
Edit `ml/train_model_land_registry.py`:
```python
# Adjust epochs
epochs=300  # was 200

# Adjust batch size
batch_size=64  # was 32

# Adjust early stopping patience
patience=30  # was 20
```

### Train with Different Data Split
```python
# In train_model():
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_scaled, test_size=0.3, random_state=42  # was 0.2
)
```

---

## 🚀 Running the Application

### Start Backend (Auto-Detects Land Registry Model)
```bash
cd backend
source venv/bin/activate
python app.py
```

Will show:
```
✓ Land Registry Keras model loaded
# OR falls back to synthetic if files not found
```

### Start Frontend
```bash
cd frontend
npm start
```

### Run Both Simultaneously
```bash
# Terminal 1
cd backend && source venv/bin/activate && python app.py

# Terminal 2
cd frontend && npm start
```

---

## 🔍 Verification Commands

### Check Data Files
```bash
# Check if processing worked
ls -lh backend/ml/data/
# Should show: pp-2024.csv (if downloaded)

# Check if training data created
ls -lh backend/land_registry_training.parquet
# Should show: 50-200 MB file
```

### Check Model Files
```bash
# Check if model was created
ls -lh backend/ml/model_land_registry.h5
# Should show: ~20 MB file

# Check scalers
ls -lh backend/ml/*land_registry*.joblib
# Should show: 2 joblib files
```

### Test Backend Health
```bash
curl http://localhost:5000/health | jq .
# Should show: "model_type": "Keras FCNN"
```

### Check Backend Logs
```bash
# Look for Land Registry indication
python backend/app.py 2>&1 | grep -i "land\|model"
```

---

## 🔄 Reprocessing Data

### Reset Everything
```bash
cd backend

# Remove old data
rm -f land_registry_training.parquet
rm -f ml/data/pp-*.csv

# Remove old models
rm -f ml/model_land_registry.h5
rm -f ml/*land_registry*.joblib

# Start fresh
source venv/bin/activate
python ml/process_land_registry.py
python ml/train_model_land_registry.py
```

### Keep Old Model as Backup
```bash
cd backend/ml

# Backup before retraining
cp model_land_registry.h5 model_land_registry.h5.backup
cp scaler_land_registry.joblib scaler_land_registry.joblib.backup
cp price_scaler_land_registry.joblib price_scaler_land_registry.joblib.backup

# Retrain
cd .. && python ml/train_model_land_registry.py

# Restore if needed
# cp ml/model_land_registry.h5.backup ml/model_land_registry.h5
# cp ml/scaler_land_registry.joblib.backup ml/scaler_land_registry.joblib
# cp ml/price_scaler_land_registry.joblib.backup ml/price_scaler_land_registry.joblib
```

---

## 📊 Testing Predictions

### Test via Frontend
```bash
# Open http://localhost:3000
# Try these test cases:

Test 1 - London Property:
  Search: "London" or "SW1"
  Beds: 3, Baths: 2, Ensuite: 1, Detached: Yes
  Expected: £400k-600k

Test 2 - Manchester:
  Search: "Manchester" or "M1"
  Beds: 3, Baths: 2, Ensuite: 0, Detached: No
  Expected: £300k-350k

Test 3 - Rural:
  Search: "Devon" or any rural area
  Beds: 2, Baths: 1, Ensuite: 0, Detached: No
  Expected: £250k-300k
```

### Test via API
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "address_id": 1,
    "beds": 3,
    "baths": 2,
    "ensuite": 1,
    "detached": 1
  }' | jq .

# Check the response:
# {
#   "avg_value": 269000,  # Predicted price
#   "model_type": "Keras FCNN",
#   "model_loaded": true
# }
```

---

## ⚠️ Troubleshooting Commands

### Check Python Version
```bash
python3 --version
# Should be 3.8 or higher
```

### Check TensorFlow
```bash
python -c "import tensorflow as tf; print(tf.__version__)"
# Should work without errors

# If TensorFlow missing:
pip install tensorflow==2.20.0
```

### Check Required Packages
```bash
python -c "import pandas; import numpy; import joblib; print('All good!')"
```

### Check if Port is Available
```bash
# Check port 5000 (backend)
lsof -i :5000
# If in use, kill it:
kill -9 <PID>

# Check port 3000 (frontend)
lsof -i :3000
# If in use, kill it:
kill -9 <PID>
```

### Run with Verbose Logging
```bash
# Process data with verbose output
python ml/process_land_registry.py 2>&1 | tee process.log

# Train with verbose output
python ml/train_model_land_registry.py 2>&1 | tee training.log

# Check logs
cat process.log
cat training.log
```

---

## 📈 Performance Optimization

### Parallel Processing (if available)
```bash
# Edit process_land_registry.py to use parallel processing
# (Advanced - see documentation)
```

### Use GPU for Training
```bash
# TensorFlow will auto-detect GPU if available
python ml/train_model_land_registry.py

# Check if GPU is used:
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### Reduce Training Time
```bash
# Edit train_model_land_registry.py:

# Reduce epochs
epochs=50  # was 200

# Reduce batch size
batch_size=128  # was 32, faster but less accurate

# Larger patience for early stopping
patience=10  # was 20, stops sooner
```

---

## 🔗 Data Sources

### Download 2024 Data Manually
```bash
cd backend/ml/data
curl -O "https://publicdata.landregistry.org.uk/pp-2024.csv"
```

### Download Multiple Years
```bash
cd backend/ml/data

for year in 2024 2023 2022 2021 2020; do
  echo "Downloading $year..."
  curl -O "https://publicdata.landregistry.org.uk/pp-${year}.csv"
done
```

### Check Download Size
```bash
# List all downloaded files
ls -lh backend/ml/data/

# Total size
du -sh backend/ml/data/
```

---

## 📝 Development Notes

### Edit Process Script
```bash
nano backend/ml/process_land_registry.py
```

Common edits:
- Line 15: `download_registry_data(year=2024)` - change year
- Line 120: `nrows=100000` - change sample size
- Line 65: Price filters `(50000, 5000000)` - change range

### Edit Training Script
```bash
nano backend/ml/train_model_land_registry.py
```

Common edits:
- Line 59: Layer sizes in `build_model()`
- Line 78: `epochs=200` - change max epochs
- Line 92: `batch_size=32` - change batch size

---

## 🎯 Complete Workflow

```bash
# 1. Setup (one time)
cd uk-property-valuation/backend
mkdir -p ml/data
source venv/bin/activate

# 2. Process data
python ml/process_land_registry.py
# Wait for: ✅ Data processing complete!

# 3. Train model
python ml/train_model_land_registry.py
# Wait for: ✅ Training complete!

# 4. Verify files created
ls -lh ml/model_land_registry.h5
ls -lh land_registry_training.parquet

# 5. Run backend
python app.py
# Should show: ✓ Land Registry Keras model loaded

# 6. Run frontend (new terminal)
cd frontend && npm start

# 7. Test
# Open http://localhost:3000
# Make a prediction
# See real data accuracy!
```

---

## 🚀 Production Deployment

### Export Model for Deployment
```bash
# All model files are already portable
# Copy to server:
scp backend/ml/model_land_registry.h5 user@server:/path/to/app/ml/
scp backend/ml/scaler_land_registry.joblib user@server:/path/to/app/ml/
scp backend/ml/price_scaler_land_registry.joblib user@server:/path/to/app/ml/
```

### Schedule Regular Retraining
```bash
# Crontab entry (monthly)
0 2 1 * * cd /path/to/app && python ml/process_land_registry.py && python ml/train_model_land_registry.py
```

---

**Happy valuating! 🏠💷**
