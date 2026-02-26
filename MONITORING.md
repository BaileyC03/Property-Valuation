# 👀 Monitoring Training Progress

The model is training on your real Land Registry data. Here are several ways to watch it:

## Option 1: Smart Monitor (Recommended)
Shows progress bar, epoch, loss, and tells you when training completes:

```bash
cd /home/user/uk-property-valuation
./monitor.sh
```

Output looks like:
```
========================================================================
🚀 LAND REGISTRY MODEL TRAINING MONITOR
========================================================================

📍 Monitoring training output...

[00:09:28] Elapsed: 0h 0m  (Check #1)
------------------------------------------------------------------------
📊 Epoch 41/200
📈 Loss: [1m loss: 0.4434 - mae: 0.4434 - mse: 0.9877
📁 Model file: Not yet created
💻 Process: Running (CPU: 223%, Memory: 1131624 KB)
========================================================================
```

This updates every 10 seconds and tells you when the model is ready!

---

## Option 2: Live Training Log
Watch the actual training output in real-time:

```bash
# Watch last 100 lines, updates every 1 second
tail -f -n 100 /tmp/claude-1000/-home-user/tasks/b8df353.output | grep -E "Epoch|loss:|mae:|mse:"
```

Or simpler - just last 50 lines:
```bash
tail -50 /tmp/claude-1000/-home-user/tasks/b8df353.output
```

---

## Option 3: Check Progress Manually
Quick one-liners to check status anytime:

### Current epoch:
```bash
tail -100 /tmp/claude-1000/-home-user/tasks/b8df353.output | grep "^Epoch" | tail -1
```

### Model file created?
```bash
ls -lh backend/ml/model_land_registry.h5 2>/dev/null && echo "✅ Model ready!" || echo "⏳ Still training..."
```

### CPU/Memory usage:
```bash
ps aux | grep "[p]ython ml/train_model_land_registry.py" | awk '{print "CPU: " $3 "%, Memory: " $6 " KB"}'
```

### Is process still running?
```bash
ps aux | grep "[p]ython ml/train_model_land_registry.py" | grep -v grep && echo "Training: Yes" || echo "Training: No"
```

---

## Option 4: Detailed Full Log
See everything that happened:

```bash
# Full training output
cat /tmp/claude-1000/-home-user/tasks/b8df353.output | less

# Or pipe to grep for epochs only
grep "^Epoch" /tmp/claude-1000/-home-user/tasks/b8df353.output
```

---

## How to Interpret the Output

### Epoch Progress
```
Epoch 41/200
```
- Currently on epoch 41 out of 200
- Progress: 41/200 = 20.5%
- ETA: ~1.5-2 hours remaining (depends on early stopping)

### Loss Values
```
loss: 0.4434 - mae: 0.4434 - mse: 0.9877
```
- **loss**: Mean Absolute Error (what the model optimizes)
  - Lower is better
  - Should decrease over time
  - Currently: 0.4434 (on scaled values)
- **mae**: Mean Absolute Error (same as loss in this case)
- **mse**: Mean Squared Error (related metric)

### Good Signs
✅ Loss is decreasing: 0.83 → 0.56 → 0.45 (good!)
✅ Process using CPU: "CPU: 223%"
✅ Memory stable: "Memory: 1.1GB"
✅ Epochs incrementing: 1/200 → 2/200 → 3/200...

### Bad Signs
❌ Loss increasing or flat
❌ Memory growing unbounded
❌ Process uses 0% CPU (might be stuck)
❌ No new epochs after 30 seconds

---

## When Training Completes

The monitor will show:
```
✅ MODEL FILE CREATED!
   Size: 12.5 MB

🎉 Training completed successfully!

Next steps:
  1. cd backend
  2. source venv/bin/activate
  3. python app.py
```

Or check manually:
```bash
ls -lh backend/ml/model_land_registry.h5
# -rw-r--r-- 1 user user 12M Feb 26 03:45 backend/ml/model_land_registry.h5
```

---

## Common Questions

### "Why is loss high?"
- Values are scaled (0-1 range), so 0.44 is actually good
- When unscaled, actual error will be shown after training

### "Can I stop training early?"
```bash
# Find process
ps aux | grep train_model_land_registry

# Kill it (loses progress!)
kill -9 <PID>
```
**Not recommended** - let it finish or hit patience threshold

### "How long will it take?"
- 574k samples ≈ 1-2 hours total
- Currently 40.5% done, so ~1 hour remaining
- Early stopping may kick in sooner (~epoch 50-60)

### "Is my computer OK?"
- **CPU**: 220% is normal (multi-core machine)
- **Memory**: 1.1GB is fine (model uses RAM)
- **Temperature**: Monitor your system temp if worried

---

## Pro Tips

### Keep Monitor Running in Background
```bash
nohup bash -c './monitor.sh > training_log.txt 2>&1' &
```

Then check anytime:
```bash
tail training_log.txt
```

### Get Alerts When Done
Add to crontab (runs every minute):
```bash
* * * * * [ -f ~/uk-property-valuation/backend/ml/model_land_registry.h5 ] && \
  notify-send "Model training complete!" || true
```

### Watch Multiple Metrics
```bash
watch -n 1 'echo "=== TRAINING STATUS ===" && \
  echo "Epoch: $(tail -100 /tmp/claude-1000/-home-user/tasks/b8df353.output | grep "^Epoch" | tail -1)" && \
  echo "Model exists: $([ -f backend/ml/model_land_registry.h5 ] && echo Yes || echo No)" && \
  ps aux | grep "[p]ython ml/train_model_land_registry.py" | awk "{print \"CPU: \" \$3 \"% Memory: \" \$6 \" KB\"}"'
```

---

**TL;DR**: Run `./monitor.sh` and it will tell you everything! 🚀
