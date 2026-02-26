# 🚀 How to Run the App

## Everything is Ready!

The backend is fully set up and tested. Now just start both servers.

---

## TERMINAL 1 - Start Backend Server

```bash
cd /home/user/uk-property-valuation/backend
source venv/bin/activate
python app.py
```

**Expected output:**
```
✓ Model loaded from /home/user/uk-property-valuation/backend/ml/model.joblib
✓ Scaler loaded from /home/user/uk-property-valuation/backend/ml/scaler.joblib
Starting UK Property Valuation API...
 * Running on http://0.0.0.0:5000
```

**Status:** ✅ Backend running on port 5000

**Keep this terminal open!** Do not close it.

---

## TERMINAL 2 - Start Frontend Server (NEW WINDOW)

```bash
cd /home/user/uk-property-valuation/frontend
npm install
npm start
```

**Expected output:**
```
webpack compiled successfully
Compiled successfully!

You can now view uk-property-valuation-frontend in the browser.
  http://localhost:3000
```

**Status:** ✅ Frontend running on port 3000

A browser window will open automatically. If not, go to: **http://localhost:3000**

---

## Test It Works

1. **Fill the form:**
   - Address: `10 Downing Street, London`
   - Beds: `6`
   - Baths: `2`
   - Ensuite: `1`
   - Detached: ✓ (check this box)

2. **Click "Get Valuation"**

3. **See results:**
   - Min Value: ~£2.9M
   - Avg Value: ~£3.4M
   - Max Value: ~£3.9M
   - Monthly Rent: ~£17k

---

## Stop the App

**Backend:** Press `Ctrl+C` in Terminal 1
**Frontend:** Press `Ctrl+C` in Terminal 2

---

## Troubleshooting

### Backend won't start
- Make sure you activated venv: `source venv/bin/activate`
- Check output for "Model loaded" message
- If error: restart Terminal 1

### Frontend won't compile
- Wait for `npm install` to complete first
- Check Terminal 2 for error messages
- Try: `rm -rf node_modules && npm install`

### "API Disconnected" in browser
- Make sure backend is running (check Terminal 1)
- Try refreshing the browser
- Check if port 5000 is in use

### Port already in use
- Another app is using port 5000
- Stop that app or edit `backend/app.py` line 87 to use different port

### Predictions not showing
- Wait for "Compiled successfully!" message
- Check browser console (F12) for errors
- Verify backend is responding: `curl http://localhost:5000/health`

---

## Next Steps

- Try different UK addresses
- Read [README.md](README.md) for API documentation
- Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for technical details
- Deploy to production (see docs)

---

## Commands Reference

```bash
# Activate Python virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Check if backend is running
curl http://localhost:5000/health

# Make a test prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "address": "London",
    "beds": 3,
    "baths": 2,
    "ensuite": 1,
    "detached": 0
  }'

# Retrain the ML model
cd backend && source venv/bin/activate && python ml/train_model.py

# Clear npm cache if needed
cd frontend && npm cache clean --force && rm -rf node_modules && npm install
```

---

## That's It! 🎉

You now have a fully functional UK property valuation app running locally!

Enjoy! 🏠✨
