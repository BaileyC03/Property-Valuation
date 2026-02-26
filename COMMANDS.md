# Complete Commands Reference

Copy-paste ready commands to set up and run your UK Property Valuation application.

## 📋 Prerequisites Check

```bash
# Check Python version (3.8+ required)
python3 --version

# Check Node version (16+ required)
node --version

# Check npm version
npm --version
```

## 🗄️ Step 1: Initialize the Database

Run this first to create SQLite database with 1,100+ UK addresses:

```bash
cd uk-property-valuation/backend
source venv/bin/activate
python init_db.py
```

**Expected output:**
```
🏗️  Creating SQLite database...
✓ Database schema created

📍 Generating comprehensive UK address data...
✓ Generated 1,100+ addresses across UK

💾 Inserting addresses into database...
✓ Inserted 1,100+ addresses

📊 Database Statistics:
  Total addresses: 1,100+
  Regions covered: 12
  ...

✅ Database initialization complete!
```

**Result:** `backend/addresses.db` created ✅

---

## 🤖 Step 2: Train the Machine Learning Model

Train the Keras neural network (takes 2-5 minutes):

```bash
# Make sure you're in backend directory with venv activated
cd backend
source venv/bin/activate
python ml/train_model_keras_v2.py
```

**Expected output:**
```
Generating training data...
Generated 3000 samples

Training Keras FCNN...
Epoch 1/150
32/63 [===========>]  loss: 125000.0 - mae: 8750.0
...
Epoch 127/150
32/63 [===========>]  loss: 4200.0 - mae: 85646.0

Model Performance:
  Training MAE: £105,783
  Testing MAE:  £85,646

Test Predictions:
  2 Victoria Ave, PO7 5BN: 3bed - £269,000
  10 Downing Street, SW1A 2AA: 6bed - £3,580,000
  Manchester City Centre, M1 1AD: 3bed - £420,000

✓ Model saved to ml/model_keras.h5
✓ Scaler saved to ml/scaler_keras.joblib
✓ Price scaler saved to ml/price_scaler_keras.joblib
```

**Result:** Model files created ✅
- `backend/ml/model_keras.h5`
- `backend/ml/scaler_keras.joblib`
- `backend/ml/price_scaler_keras.joblib`

---

## 🚀 Step 3: Start the Backend

Run the Flask API server (keep this terminal open):

```bash
cd uk-property-valuation/backend
source venv/bin/activate
python app.py
```

**Expected output:**
```
Starting UK Property Valuation API...
Available endpoints:
  GET  /health     - Health check
  GET  /addresses  - Get list of available addresses
  GET  /search     - Search addresses by query
  POST /predict    - Get property valuation

Using Keras FCNN model (TensorFlow)
 * Running on http://0.0.0.0:5000
```

✅ Backend running on http://localhost:5000

---

## 💻 Step 4: Start the Frontend

**Open a NEW terminal** and run:

```bash
cd uk-property-valuation/frontend
npm start
```

**Expected output:**
```
> react-scripts start

Compiled successfully!

You can now view uk-property-valuation in the browser at:
  http://localhost:3000
```

✅ Frontend running on http://localhost:3000

---

## 🌐 Step 5: Use the Application

1. Open your browser: **http://localhost:3000**
2. You should see the property valuation form
3. Try these test cases:

### Test Case 1: Isle of Wight Property
```
Search: "Victoria" or "Isle of Wight"
Select: "2 Victoria Ave, Isle of Wight"
Beds: 3
Baths: 2
Ensuite: 1
Detached: ✓ YES
Expected Price: £250k - £300k
```

### Test Case 2: London Property
```
Search: "Downing" or "London"
Select: "10 Downing Street, Westminster"
Beds: 6
Baths: 2
Ensuite: 1
Detached: ✗ NO
Expected Price: £3.5M - £3.6M
```

### Test Case 3: Manchester Property
```
Search: "Manchester"
Select: "Manchester City Centre"
Beds: 3
Baths: 2
Ensuite: 0
Detached: ✗ NO
Expected Price: £400k - £450k
```

---

## 🔧 Helpful Commands

### Test Backend Health
```bash
curl http://localhost:5000/health
```

### Get All Addresses
```bash
curl http://localhost:5000/addresses | jq '.addresses | length'
```

### Search Addresses
```bash
curl "http://localhost:5000/search?q=London" | jq '.results'
```

### Test Prediction API
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "address_id": 1,
    "beds": 3,
    "baths": 2,
    "ensuite": 1,
    "detached": 1
  }' | jq '.'
```

### Restart Backend (if needed)
```bash
# Press Ctrl+C in the backend terminal, then:
python app.py
```

### Restart Frontend (if needed)
```bash
# Press Ctrl+C in the frontend terminal, then:
npm start
```

---

## 🔄 Retrain the Model

If you want to train the model again with different parameters:

```bash
cd uk-property-valuation/backend
source venv/bin/activate

# Backup old model
cp ml/model_keras.h5 ml/model_keras.h5.backup

# Retrain
python ml/train_model_keras_v2.py

# If good, keep it. If bad, restore:
# cp ml/model_keras.h5.backup ml/model_keras.h5
```

---

## 🗄️ Reset the Database

If you want to regenerate the database with new data:

```bash
cd uk-property-valuation/backend
source venv/bin/activate

# Remove old database
rm addresses.db

# Regenerate
python init_db.py
```

---

## ❌ Troubleshooting Commands

### Check if Backend is Running
```bash
curl http://localhost:5000/health
# Should return: {"status": "ok", "model_loaded": true, ...}
```

### Check if Database Exists
```bash
ls -lh backend/addresses.db
# Should show file exists with size ~1-5 MB
```

### Check if Model Files Exist
```bash
ls -lh backend/ml/model_keras.h5
ls -lh backend/ml/scaler_keras.joblib
ls -lh backend/ml/price_scaler_keras.joblib
```

### View Backend Logs
```bash
# Backend logs appear in the terminal where you ran: python app.py
# Look for any errors or warnings
```

### View Frontend Logs
```bash
# Frontend logs appear in:
# 1. Terminal where you ran: npm start
# 2. Browser DevTools Console (F12)
```

### Restart Everything
```bash
# Terminal 1 - Kill backend (Ctrl+C)
# Terminal 2 - Kill frontend (Ctrl+C)

# Then restart in order:
# Terminal 1:
cd backend && source venv/bin/activate && python app.py

# Terminal 2:
cd frontend && npm start
```

---

## 📊 Quick Status Check

```bash
# Check all components are running
echo "=== Backend Health ===" && curl -s http://localhost:5000/health | jq .
echo "=== Database ===" && ls -lh backend/addresses.db
echo "=== Model ===" && ls -lh backend/ml/model_keras.h5
echo "=== Frontend ===" && curl -s http://localhost:3000 > /dev/null && echo "Frontend responding"
```

---

## 🎯 One-Line Quick Start

If you've already run init_db.py and trained the model once:

```bash
# Terminal 1
cd uk-property-valuation/backend && source venv/bin/activate && python app.py

# Terminal 2
cd uk-property-valuation/frontend && npm start
```

Then open http://localhost:3000

---

## 💾 Full Clean Start

Reset everything and start from scratch:

```bash
# Clean database
cd uk-property-valuation/backend
rm -f addresses.db
python init_db.py

# Retrain model
python ml/train_model_keras_v2.py

# Start backend
python app.py

# In another terminal, start frontend
cd uk-property-valuation/frontend
npm start
```

---

## 📝 Notes

- **Keep terminals open**: Both backend and frontend need to keep running
- **Check ports**: Make sure ports 5000 (backend) and 3000 (frontend) are available
- **First run**: Initial requests might be slow as TensorFlow loads
- **Database**: Once created, you don't need to run `init_db.py` again
- **Model**: Once trained, you don't need to run `train_model_keras_v2.py` again
- **venv**: Always activate virtual environment before running Python scripts

---

**Happy valuating! 🏠💷**
