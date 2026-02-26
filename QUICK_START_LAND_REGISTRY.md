# Quick Start - Land Registry Model

## ✅ What's Done
- ✅ Downloaded and processed real HM Land Registry data (574k+ samples)
- ⏳ Training Keras model on real government transaction data
- ✅ Updated backend to use real data model

## ⏳ When Ready (Model Training Completes)

### 1️⃣ Verify Model Files
```bash
cd backend
ls -lh ml/model_land_registry.h5
# Should show: model_land_registry.h5 (~10-15 MB)
```

### 2️⃣ Start Backend
```bash
cd backend
source venv/bin/activate
python app.py
```

**You should see:**
```
✓ Land Registry model loaded from ml/model_land_registry.h5
  Training data: Real HM Land Registry transactions (574k+ samples)
✓ Feature scaler loaded
✓ Price scaler loaded
 * Running on http://0.0.0.0:5000
```

### 3️⃣ Start Frontend (new terminal)
```bash
cd frontend
npm start
```

### 4️⃣ Open Browser
Visit: **http://localhost:3000**

### 5️⃣ Test It
1. Search for an address (e.g., "London")
2. Select an address from dropdown
3. Enter property details (beds, baths, etc.)
4. Click "Get Valuation"
5. See the predicted price from real market data!

## 📊 How to Know It's Working

### Check Backend Console
```
✓ Land Registry model loaded from ml/model_land_registry.h5
  Training data: Real HM Land Registry transactions (574k+ samples)
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
    "detached": 0
  }'

# Response should be: {"prediction": 123456.78}
```

## 🔍 Monitor Training Progress

### Check if Model File Exists
```bash
ls -lh backend/ml/model_land_registry.h5 2>/dev/null && \
echo "✅ Model file created!" || \
echo "⏳ Still training..."
```

### Watch Training Output
```bash
# Last 30 lines of training log
tail -30 /tmp/claude-1000/-home-user/tasks/b8df353.output

# Or full history (large file)
cat /tmp/claude-1000/-home-user/tasks/b8df353.output | tail -100
```

### Check Training Process
```bash
ps aux | grep "[p]ython ml/train_model_land_registry.py"
# If you see output: training is running
# If no output: training completed
```

## 🎯 Expected Results

### Dataset Comparison
| Aspect | Synthetic | **Real Data** |
|--------|-----------|--------------|
| Source | Generated | HM Land Registry |
| Samples | 3,000 | **574,226** |
| Avg Error | ±£85,646 | TBD (will show after training) |
| Realism | Moderate | **High** ✨ |

### What You'll See
After predictions, you might see:
```
Address: 10 Downing Street, London
Beds: 3, Baths: 2, Detached: No
Predicted Price: £450,000
```

Actual market value would determine accuracy!

## 🛠️ Troubleshooting

### "Land Registry model not found"
- **Cause**: Training hasn't completed yet
- **Check**: `ls backend/ml/model_land_registry.h5`
- **Wait**: Training may take 1-2 hours total

### "Failed to load model"
- **Cause**: TensorFlow not installed or model corrupted
- **Fix**:
  ```bash
  pip install tensorflow==2.20.0
  # Retrain if needed
  python ml/train_model_land_registry.py
  ```

### Backend falls back to synthetic model
- **Cause**: Land Registry model not found
- **Check**: `echo backend/ml/model_land_registry.h5`
- **Status in console**: Will show "Keras model loaded" instead of "Land Registry model"

### Predictions seem off
- **First check**: Are you using the right model? (Check backend console)
- **Second check**: Is the address_id correct?
- **Data quality**: Model is as good as training data

## 📚 More Info
- See `LAND_REGISTRY_TRAINING_COMPLETE.md` for detailed status
- See `NEXT_STEPS.md` for advanced options

---

**That's it!** Your UK property valuation app is now powered by real government market data. 🚀
