# Installation Guide - UK Property Valuation App

## Issue: Python venv not available

If you see an error about `python3-venv` not being installed, follow these steps:

### Step 1: Install Python venv (One-time)

```bash
# If you have sudo access:
sudo apt-get update
sudo apt-get install -y python3.12-venv

# If you're already root (no sudo needed):
apt-get update
apt-get install -y python3.12-venv
```

### Step 2: Manual Setup (After venv is installed)

#### Terminal 1 - Backend Setup & Start

```bash
cd /home/user/uk-property-valuation/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train the ML model (takes ~30 seconds)
python ml/train_model.py

# Start the backend server
python app.py
```

You should see:
```
Starting UK Property Valuation API...
 * Running on http://0.0.0.0:5000
```

#### Terminal 2 - Frontend Setup & Start (New Terminal Window)

```bash
cd /home/user/uk-property-valuation/frontend

# Install npm dependencies (first time only)
npm install

# Start the development server
npm start
```

The app will automatically open at `http://localhost:3000`

### Step 3: Test It!

1. In the form, enter:
   - Address: `10 Downing Street, London`
   - Beds: `6`
   - Baths: `2`
   - Ensuite: `1`
   - Detached: ✓ (checked)

2. Click "Get Valuation"

3. You should see predicted values (around £3.4M)

### Stopping the App

**Backend:** Press `Ctrl+C` in the backend terminal
**Frontend:** Press `Ctrl+C` in the frontend terminal

---

## Quick Troubleshooting

**Error: "ModuleNotFoundError: No module named 'flask'"**
- Make sure venv is activated (you should see `(venv)` at the start of your terminal)
- Run: `pip install -r requirements.txt`

**Error: "Port 5000 already in use"**
- Either wait for the previous process to stop, or edit `backend/app.py` line 87:
  ```python
  app.run(debug=True, port=5001)  # Change 5000 to 5001
  ```
- Then update frontend API URL in `frontend/src/App.tsx`

**Error: "npm command not found"**
- Install Node.js: https://nodejs.org/
- Requires Node.js 16+

**Frontend shows "API Disconnected"**
- Make sure backend is running on port 5000
- Check terminal for backend errors
- Try refreshing the page

---

## What's Next?

Once it's running:
- Try different addresses
- Read [README.md](README.md) for full documentation
- Check [SETUP.md](SETUP.md) for more details
- See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for technical details

---

**All set!** You now have a working property valuation app! 🏠✨
