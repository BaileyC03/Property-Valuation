# Quick Start Guide

Get the UK Property Valuation app running in 5 minutes!

## Prerequisites

- Python 3.8+
- Node.js 16+
- Git (optional)

## Step 1: Set Up the Database (NEW!)

The app now uses SQLite to store 1,100+ UK addresses. Initialize it with:

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
  Regions: East Anglia, East Midlands, Isle of Wight, London, ...

✅ Database initialization complete!
```

This creates `addresses.db` with addresses from all major UK cities and regions.

## Step 2: Train the Model

The machine learning model predicts property prices. Train it with:

```bash
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

This creates trained model files in the `ml/` folder.

## Step 3: Start the Backend

```bash
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

Keep this terminal open. The backend is now running!

## Step 4: Start the Frontend

In a **new terminal**:

```bash
cd uk-property-valuation/frontend
npm start
```

**Expected output:**
```
> react-scripts start

On Your Network: http://192.168.x.x:3000

Compiled successfully!

You can now view uk-property-valuation in the browser at:
  http://localhost:3000
```

Open http://localhost:3000 in your browser.

## Step 5: Use the Application

1. **Search for an address**: Type in the address field (e.g., "London", "Manchester", "PO7")
2. **Select an address**: Click on a suggestion from the dropdown
3. **Enter property details**:
   - Bedrooms: 1-10
   - Bathrooms: 1-10
   - Ensuite bathrooms: 0 to total bathrooms
   - Detached: Yes/No checkbox
4. **Click "Get Valuation"**: See the predicted property price!

### Example Predictions

| Address | Beds | Baths | Detached | Price |
|---------|------|-------|----------|-------|
| 2 Victoria Ave, Isle of Wight | 3 | 2 | Yes | £269k |
| 10 Downing Street, London | 6 | 2 | No | £3.58M |
| Manchester City Centre | 3 | 2 | No | £420k |
| Cambridge City Centre | 3 | 1 | No | £520k |

## Troubleshooting

### "Database not found" error
```bash
# Re-initialize the database
python init_db.py
```

### "Model not loaded" error
```bash
# Make sure you ran the training script
python ml/train_model_keras_v2.py
```

### Port already in use (port 5000)
```bash
# Change the port in backend/app.py
app.run(debug=True, port=5001)  # Use 5001 instead
```

### npm start fails
```bash
# Reinstall node_modules
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### "TensorFlow not found" error
```bash
# Install TensorFlow in the backend venv
pip install tensorflow==2.20.0
```

## File Structure

```
uk-property-valuation/
├── backend/
│   ├── app.py                 # Flask API
│   ├── init_db.py             # Database initialization
│   ├── addresses.db           # SQLite database (created by init_db.py)
│   ├── requirements.txt        # Python dependencies
│   └── ml/
│       ├── train_model_keras_v2.py    # Model training script
│       ├── model_keras.h5             # Trained model (created by training)
│       ├── scaler_keras.joblib        # Feature scaler
│       └── price_scaler_keras.joblib  # Price scaler
│
├── frontend/
│   ├── package.json           # npm dependencies
│   ├── src/
│   │   ├── App.tsx           # Main React component
│   │   └── components/
│   │       ├── PropertyForm.tsx    # Address search + property form
│   │       └── ResultsDisplay.tsx  # Valuation results
│
├── README.md                  # Full documentation
├── TRAINING_GUIDE.md          # Detailed model training info
└── QUICKSTART.md              # This file
```

## API Reference

### GET /addresses
Returns all available addresses.

```bash
curl http://localhost:5000/addresses
```

### GET /search?q=London
Search addresses (for autocomplete).

```bash
curl "http://localhost:5000/search?q=London"
```

### POST /predict
Predict property value.

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "address_id": 1,
    "beds": 3,
    "baths": 2,
    "ensuite": 1,
    "detached": 1
  }'
```

### GET /health
Check if backend is running.

```bash
curl http://localhost:5000/health
```

## Next Steps

1. Read TRAINING_GUIDE.md for model details
2. Retrain the model by editing train_model_keras_v2.py
3. Customize addresses in init_db.py
4. Deploy to cloud (Heroku, AWS, etc.)

---

**You're all set!** 🎉 Visit http://localhost:3000 to start valuating properties.
