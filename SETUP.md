# Setup Guide - UK Property Valuation App

This guide will help you get the application running locally with both frontend and backend.

## Prerequisites

- **Node.js 16+** and npm (for frontend)
- **Python 3.9+** (for backend)
- **Git** (optional, for version control)

## Quick Start (5-10 minutes)

### Step 1: Train the ML Model

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train the model
python ml/train_model.py
```

You should see output like:
```
Generating synthetic property data...
Generated 5000 property records
Training random forest model...
✓ Model saved to ml/model.joblib
✓ Scaler saved to ml/scaler.joblib
```

### Step 2: Start Backend Server

Keep the virtual environment activated and run:

```bash
python app.py
```

You should see:
```
Starting UK Property Valuation API...
Available endpoints:
  GET  /health
  POST /predict
 * Running on http://0.0.0.0:5000
```

### Step 3: Start Frontend (in a new terminal)

```bash
cd frontend
npm install
npm start
```

The React app will automatically open at `http://localhost:3000`

## Testing the Application

### Manual Testing

1. Fill in the property form:
   - Address: "10 Downing Street, London"
   - Bedrooms: 6
   - Bathrooms: 2
   - Ensuite: 1
   - Detached: No

2. Click "Get Valuation"

3. You should see estimated property values and rental income

### API Testing with curl

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "address": "10 Downing Street, London",
    "beds": 6,
    "baths": 2,
    "ensuite": 1,
    "detached": 0
  }'
```

Response:
```json
{
  "address": "10 Downing Street, London",
  "beds": 6,
  "baths": 2,
  "ensuite": 1,
  "detached": false,
  "min_value": 2891847,
  "avg_value": 3401533,
  "max_value": 3911220,
  "predicted_rent": 17008,
  "model_loaded": true,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Health Check

```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Backend Won't Start

**Error: "ModuleNotFoundError: No module named 'flask'"**

Solution:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Error: "Port 5000 already in use"**

Solution: Change the port in `backend/app.py`:
```python
if __name__ == '__main__':
    load_model()
    app.run(debug=True, port=5001)  # Change to different port
```

Then update the frontend API URL in `frontend/src/App.tsx`:
```typescript
const response = await axios.post<PredictionResult>(
  'http://localhost:5001/predict',  // Match the new port
  ...
);
```

### Frontend Won't Connect to Backend

**Error: "Cannot connect to backend API"**

1. Ensure backend is running on `http://localhost:5000`
2. Check CORS is enabled in `backend/app.py` (it is by default)
3. Check browser console for detailed error messages
4. Try health check: `curl http://localhost:5000/health`

**Error: "API Disconnected" in UI**

Wait a few seconds and refresh the page. The health check runs on page load.

### Model File Not Found

**Error: "Model not available - Please train the model first"**

Solution:
```bash
cd backend
python ml/train_model.py
```

Then restart the Flask app.

### Address Geocoding Fails

The app uses OpenStreetMap Nominatim API (no authentication needed). If geocoding fails:

1. Check internet connection
2. Try a different address
3. The app has a fallback that defaults to London coordinates

## Project Structure

```
uk-property-valuation/
├── backend/
│   ├── app.py              # Flask API
│   ├── requirements.txt     # Python dependencies
│   ├── ml/
│   │   ├── train_model.py   # Model training script
│   │   ├── model.joblib     # Trained model (generated)
│   │   └── scaler.joblib    # Feature scaler (generated)
│   └── .gitignore
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── PropertyForm.tsx
│   │   │   ├── PropertyForm.css
│   │   │   ├── ResultsDisplay.tsx
│   │   │   └── ResultsDisplay.css
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   └── .gitignore
├── README.md               # Main documentation
├── SETUP.md               # This file
└── .gitignore
```

## Development

### Making Changes

**Backend Changes:**
1. Edit files in `backend/`
2. Flask auto-reloads when files change (debug=True)
3. No need to restart server

**Frontend Changes:**
1. Edit files in `frontend/src/`
2. React dev server hot-reloads
3. Browser refreshes automatically

### Retraining Model

If you modify `backend/ml/train_model.py`:

```bash
cd backend
python ml/train_model.py
```

Restart the Flask server to load the new model.

## Next Steps

### Enhancements

1. **Add Real Land Registry Data:**
   - Download from https://www.gov.uk/government/organisations/land-registry
   - Replace synthetic data in `train_model.py`

2. **Improve Model:**
   - Try different algorithms (XGBoost, LightGBM)
   - Add more features (year built, garden size, etc.)
   - Cross-validation and hyperparameter tuning

3. **Add Database:**
   - Store predictions for analytics
   - Track model performance over time

4. **Deploy to Production:**
   - Heroku for backend
   - Vercel/Netlify for frontend
   - Set appropriate CORS configuration

## Support

For issues or questions:
- Check the README.md
- Review error messages in terminal/browser console
- Check API response format in health check
- Ensure all dependencies are installed

---

**Created:** January 2024
**Status:** Ready for local development
