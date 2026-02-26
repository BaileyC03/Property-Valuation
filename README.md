# UK Property Valuation Web App

A full-stack web application for predicting UK property values using machine learning.

## Features

- React + TypeScript frontend with form inputs for property details
- Flask backend with ML model for property valuation predictions
- OpenStreetMap API integration for address enrichment
- Trained on UK Land Registry Price Paid Data (placeholder model for demo)
- No database required - self-contained

## Project Structure

```
uk-property-valuation/
├── frontend/          # React + TypeScript application
├── backend/           # Flask API + ML model
├── data/              # Sample Land Registry data
└── README.md
```

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Git

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The React app will open at `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:5000`

### Training the ML Model

```bash
cd backend
python ml/train_model.py
```

This will:
1. Download sample UK Land Registry data
2. Train a random forest model
3. Export the model as `model.joblib`

## API Endpoints

### POST `/predict`

Predicts property value based on property characteristics.

**Request:**
```json
{
  "address": "10 Downing Street, London",
  "beds": 6,
  "baths": 2,
  "ensuite": 1,
  "detached": false
}
```

**Response:**
```json
{
  "min_value": 2500000,
  "avg_value": 3200000,
  "max_value": 4000000,
  "predicted_rent": 12000,
  "address": "10 Downing Street, London",
  "confidence": 0.85
}
```

## Development Notes

- The ML model is a placeholder random forest trained on synthetic property data
- Address enrichment uses OpenStreetMap Nominatim API (no authentication required)
- CORS is enabled for frontend-backend communication
- Error handling included for invalid addresses and malformed requests

## Troubleshooting

**Frontend won't connect to backend:**
- Ensure backend is running on `http://localhost:5000`
- Check CORS settings in `backend/app.py`

**Model file not found:**
- Run `python ml/train_model.py` in the backend directory

**Address lookup fails:**
- Check your internet connection
- The app has a fallback for address resolution
