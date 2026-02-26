# UK Property Valuation App - Project Summary

## Overview

A complete full-stack web application for predicting UK property values and rental income using machine learning. The app features a modern React frontend with TypeScript and a Flask backend with scikit-learn ML models.

## What's Included

### ✅ Frontend (React + TypeScript)

- **Modern UI** with gradient styling and animations
- **Form validation** with error messages
- **Real-time API status** indicator
- **Responsive design** for mobile and desktop
- **Loading states** with spinner animation
- **Results display** with:
  - Value range visualization
  - Currency formatting
  - Property details summary
  - Monthly/annual rent estimates

**Key Files:**
- `frontend/src/App.tsx` - Main app component with API integration
- `frontend/src/components/PropertyForm.tsx` - Property input form
- `frontend/src/components/ResultsDisplay.tsx` - Results visualization
- Professional CSS styling in `*.css` files

### ✅ Backend (Flask + Python)

- **RESTful API** with CORS enabled
- **ML Model** - Random Forest regressor for price prediction
- **Feature Scaling** - StandardScaler for normalized predictions
- **Address Geocoding** - OpenStreetMap Nominatim integration
- **Error Handling** - Comprehensive validation and error messages
- **Health Check** - `/health` endpoint for monitoring

**Key Files:**
- `backend/app.py` - Flask API server
- `backend/ml/train_model.py` - Model training script
- `backend/requirements.txt` - Python dependencies

### ✅ Machine Learning

**Model Details:**
- **Type:** Random Forest Regressor
- **Trees:** 100 estimators
- **Max Depth:** 15
- **Features:** 6 input features
  - Bedrooms (1-10)
  - Total bathrooms (1-10)
  - Ensuite bathrooms (0-total)
  - Detached (0/1)
  - Latitude (50.0-57.5)
  - Longitude (-5.0-1.5)

**Training:**
- Generates 5000 synthetic property records
- Inspired by UK Land Registry patterns
- Regional price multiplier based on distance from London
- Test R² score ~0.85+

**Export:**
- Model exported as `joblib` for fast loading
- Feature scaler also saved for preprocessing

### ✅ API Specification

**Endpoint:** `POST /predict`

**Request:**
```json
{
  "address": "10 Downing Street, London",
  "beds": 6,
  "baths": 2,
  "ensuite": 1,
  "detached": 0
}
```

**Response:**
```json
{
  "address": "10 Downing Street, London",
  "geocoded_address": "10, Downing Street, London, England, United Kingdom",
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

## Running Locally

### Quick Start

1. **Setup Everything:**
   ```bash
   ./start.sh  # Automated setup
   ```

2. **Terminal 1 - Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

3. **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm start
   ```

4. **Open Browser:**
   - Navigate to `http://localhost:3000`

### Detailed Setup

See `SETUP.md` for step-by-step instructions and troubleshooting.

## Features

### Frontend Features
- ✅ Form validation with error messages
- ✅ Address field with OpenStreetMap integration
- ✅ Bedroom/bathroom inputs with validation
- ✅ Detached property toggle
- ✅ API status indicator (connected/disconnected)
- ✅ Loading spinner during prediction
- ✅ Responsive grid layout
- ✅ Value range visualization
- ✅ Currency formatting (GBP)
- ✅ Monthly and annual rent estimates
- ✅ Timestamp of prediction
- ✅ Disclaimer about estimates

### Backend Features
- ✅ Input validation and error handling
- ✅ OpenStreetMap Nominatim geocoding
- ✅ Feature extraction and scaling
- ✅ ML model predictions
- ✅ CORS support for frontend
- ✅ Health check endpoint
- ✅ Comprehensive logging
- ✅ Graceful error messages

### ML Features
- ✅ Random Forest model
- ✅ Feature scaling (StandardScaler)
- ✅ Regional price variation
- ✅ Property characteristic encoding
- ✅ Model persistence (joblib)
- ✅ Synthetic data generation
- ✅ Model evaluation (R² score)
- ✅ Feature importance display

## Technology Stack

### Frontend
- React 18.2
- TypeScript 5.2
- Axios (HTTP client)
- CSS3 (no frameworks needed)

### Backend
- Flask 2.3
- Flask-CORS 4.0
- scikit-learn 1.3
- joblib 1.3
- numpy 1.24
- pandas 2.0
- requests 2.31

### Tools & Services
- OpenStreetMap Nominatim API (address geocoding)
- Synthetic data (based on Land Registry patterns)

## File Structure

```
uk-property-valuation/
├── backend/
│   ├── app.py                    # Flask API
│   ├── requirements.txt           # Dependencies
│   ├── ml/
│   │   └── train_model.py         # Model training
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
├── README.md                      # Main documentation
├── SETUP.md                       # Setup instructions
├── PROJECT_SUMMARY.md             # This file
├── start.sh                       # Startup helper
└── .gitignore
```

## How It Works

### User Journey

1. **User enters property details:**
   - Address
   - Number of bedrooms
   - Number of bathrooms
   - Number of ensuite bathrooms
   - Property type (detached/attached)

2. **Frontend validates** and sends to backend

3. **Backend processes:**
   - Validates input
   - Geocodes address using OpenStreetMap
   - Extracts features (bedrooms, bathrooms, location, etc.)
   - Scales features for ML model
   - Makes prediction using trained Random Forest

4. **Backend returns:**
   - Min, average, max property values
   - Estimated monthly rent
   - Geocoded address
   - Prediction timestamp

5. **Frontend displays:**
   - Property details summary
   - Value range with visual bar
   - Estimated average value (large)
   - Monthly rent estimate
   - Annual rent calculation
   - Disclaimer about estimates

## Customization

### Train on Real Data

Replace the synthetic data in `backend/ml/train_model.py` with real UK Land Registry data:

1. Download from: https://www.gov.uk/government/organisations/land-registry
2. Replace the `generate_synthetic_data()` function
3. Retrain: `python ml/train_model.py`

### Improve the Model

- Try other algorithms: XGBoost, LightGBM, Neural Networks
- Add more features: year built, garden size, floor area, etc.
- Hyperparameter tuning
- Cross-validation

### Add More Features

- Property age
- Total floor area (sqft/sqm)
- Garden size
- Parking spaces
- Energy efficiency rating
- Listed building status

## Deployment

### Production Checklist

- [ ] Add database for storing predictions
- [ ] Implement rate limiting
- [ ] Add authentication for user accounts
- [ ] Deploy backend to Heroku/Railway/DigitalOcean
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Update API URLs for production
- [ ] Set up monitoring and logging
- [ ] Add integration with real Land Registry API
- [ ] Implement caching for address geocoding

### Environment Variables

Create `.env` files:

**backend/.env:**
```
FLASK_ENV=production
FLASK_DEBUG=False
API_PORT=5000
```

**frontend/.env:**
```
REACT_APP_API_URL=https://api.yourdomain.com
```

## Known Limitations

1. **Model is synthetic** - Based on generated data, not real Land Registry data
2. **Regional accuracy** - Simplified distance-from-London pricing
3. **Limited features** - Only 6 features currently used
4. **No historical data** - Doesn't account for market trends
5. **No user accounts** - All predictions are public
6. **No persistence** - Predictions are not stored

## Future Enhancements

1. ✨ Real Land Registry data integration
2. ✨ Historical price trends
3. ✨ Similar properties comparison
4. ✨ Investment calculator (ROI, yield)
5. ✨ Mortgage calculator
6. ✨ Property image upload and analysis
7. ✨ User accounts and saved searches
8. ✨ Export predictions to PDF
9. ✨ Market analytics dashboard
10. ✨ Mobile app (React Native)

## Support & Resources

- **Main Docs:** See `README.md`
- **Setup Guide:** See `SETUP.md`
- **Issues:** Check terminal/browser console for errors
- **API Testing:** Use curl or Postman

## License

MIT (Create LICENSE.md if needed)

## Contributors

Built with ❤️ for UK property valuation

---

**Ready to use!** Follow the Quick Start section above to get running.
