# 📊 How to Monitor Training - Quick Guide

## The Easiest Way 🚀

Open a terminal in your project directory and run:

```bash
./monitor.sh
```

That's it! You'll see live updates every 10 seconds showing:
- ✅ Current epoch (e.g., "Epoch 41/200")
- ✅ Progress percentage
- ✅ Current loss value
- ✅ CPU/Memory usage
- ✅ **Tells you when training is done** ✨

Example output:
```
========================================================================
🚀 LAND REGISTRY MODEL TRAINING MONITOR
========================================================================

📍 Monitoring training output...


[00:09:28] Elapsed: 0h 15m  (Check #2)
------------------------------------------------------------------------
📊 Epoch 41/200
📈 Loss: loss: 0.4434 - mae: 0.4434 - mse: 0.9877
📁 Model file: Not yet created
💻 Process: Running (CPU: 223%, Memory: 1131624 KB)
========================================================================
```

**Just wait for the ✅ MODEL FILE CREATED message!**

---

## What the Monitor Shows

### 📊 Epoch
```
Epoch 41/200
```
You're on epoch 41 of 200 maximum epochs.
- **41 ÷ 200 = 20.5% complete**
- With ~60 epochs remaining, expect 30-60 minutes more
- Early stopping might finish sooner

### 📈 Loss
```
Loss: loss: 0.4434 - mae: 0.4434 - mse: 0.9877
```
- **Loss should go DOWN** → that means learning! ✓
- Current: 0.4434 (values are scaled 0-1)
- Trend: Started at 0.83, now 0.44 = Great progress!

### 💻 Process
```
Process: Running (CPU: 223%, Memory: 1131624 KB)
```
- CPU at 223% = Using multiple cores (good!)
- Memory 1.1GB = Normal for 574k samples
- Both stable = Training is healthy

### 📁 Model File
```
Model file: Not yet created
```
Once you see:
```
✅ MODEL FILE CREATED!
   Size: 12.5 MB
```
**Your model is ready!** 🎉

---

## Other Ways to Check

### Quick Manual Check
```bash
# Is training still running?
ps aux | grep "[p]ython ml/train_model_land_registry.py" | grep -v grep

# What epoch is it on?
tail -100 /tmp/claude-1000/-home-user/tasks/b8df353.output | grep "^Epoch" | tail -1

# Is the model file there yet?
ls -lh backend/ml/model_land_registry.h5
```

### Watch Raw Training Output
```bash
# Last 50 lines of training (updates in real-time)
tail -f /tmp/claude-1000/-home-user/tasks/b8df353.output
```

Press `Ctrl+C` to stop watching.

---

## Understanding the Training

### Timeline (Rough Estimate)
- **Epoch 1-10**: Loss drops fast (0.83 → 0.70)
- **Epoch 11-30**: Good steady improvement (0.70 → 0.50)
- **Epoch 31-50**: Improvements slowing (0.50 → 0.43)
- **Epoch 51+**: Very small gains (0.43 → 0.42...)
- **Early Stopping**: Triggers when no improvement for 20 epochs

### When Does It Stop?
Training will stop when:
1. ✅ Reaches 200 epochs, OR
2. ✅ Early stopping triggers (validation loss stops improving for 20 epochs)

Currently around epoch 41, so probably stops around epoch 60-80.

---

## When Training Completes

The monitor will show:
```
========================================================================
🎉 Training completed successfully!
========================================================================

Next steps:
  1. cd backend
  2. source venv/bin/activate
  3. python app.py
```

Or manually verify:
```bash
ls -lh backend/ml/model_land_registry.h5
# Should show: -rw-r--r-- ... 12M ... model_land_registry.h5 ✓
```

---

## Troubleshooting

### Monitor Says "Still Running" But No Output Changes
**Normal!** Training takes time. The monitor updates every 10 seconds.

### "Training process ended but model not found!"
Something went wrong. Check the full log:
```bash
tail -200 /tmp/claude-1000/-home-user/tasks/b8df353.output | grep -E "Error|Traceback|Exception"
```

### Monitor Keeps Running After Model Created
Press `Ctrl+C` to exit. (Doesn't hurt training.)

### "Model file not found" error in monitor
**Temporary** - it exists, just haven't been created yet. Keep waiting!

---

## Quick Reference Commands

| What You Want | Command |
|---|---|
| **Watch live** | `./monitor.sh` |
| **Check epoch** | `tail -100 /tmp/claude-1000/-home-user/tasks/b8df353.output \| grep "^Epoch" \| tail -1` |
| **See full output** | `tail -f /tmp/claude-1000/-home-user/tasks/b8df353.output` |
| **Model ready?** | `ls backend/ml/model_land_registry.h5` |
| **Process running?** | `ps aux \| grep "[p]ython ml/train_model_land_registry"` |

---

## That's It!

Just run `./monitor.sh` and let it do the work. It will tell you when everything is ready! 🚀

**Current Status**: Epoch 41/200 (20.5% complete) - About 1 hour remaining ⏱️
