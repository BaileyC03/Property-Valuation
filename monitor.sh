#!/bin/bash

# Real-time training progress monitor for Land Registry model
# Usage: ./monitor.sh
# Or: bash monitor.sh

echo ""
echo "========================================================================"
echo "🚀 LAND REGISTRY MODEL TRAINING MONITOR"
echo "========================================================================"
echo ""

OUTPUT_FILE="/tmp/claude-1000/-home-user/tasks/b8df353.output"
MODEL_FILE="backend/ml/model_land_registry.h5"
START_TIME=$(date +%s)

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "❌ Training output file not found at: $OUTPUT_FILE"
    echo "Make sure training is running!"
    exit 1
fi

echo "📍 Monitoring training output..."
echo ""

check_count=0
while true; do
    check_count=$((check_count + 1))
    current_time=$(date "+%H:%M:%S")
    current_timestamp=$(date +%s)
    elapsed=$((current_timestamp - START_TIME))
    hours=$((elapsed / 3600))
    minutes=$(((elapsed % 3600) / 60))

    echo ""
    echo "[$current_time] Elapsed: ${hours}h ${minutes}m  (Check #$check_count)"
    echo "------------------------------------------------------------------------"

    # Get current epoch
    epoch_line=$(tail -100 "$OUTPUT_FILE" | grep "^Epoch" | tail -1)
    if [ ! -z "$epoch_line" ]; then
        echo "📊 $epoch_line"
    else
        echo "📊 Epoch: Waiting for training to start..."
    fi

    # Get loss info (last line with loss/mae/mse)
    loss_line=$(tail -50 "$OUTPUT_FILE" | grep -E "loss:|mae:|mse:" | tail -1)
    if [ ! -z "$loss_line" ]; then
        echo "📈 Loss: $loss_line"
    fi

    # Check if model file exists
    if [ -f "$MODEL_FILE" ]; then
        model_size=$(ls -lh "$MODEL_FILE" | awk '{print $5}')
        echo ""
        echo "✅ MODEL FILE CREATED!"
        echo "   Size: $model_size"
        echo ""
        echo "========================================================================"
        echo "🎉 Training completed successfully!"
        echo "========================================================================"
        echo ""
        echo "Next steps:"
        echo "  1. cd backend"
        echo "  2. source venv/bin/activate"
        echo "  3. python app.py"
        echo ""
        echo "In another terminal:"
        echo "  cd frontend && npm start"
        echo ""
        echo "Then visit: http://localhost:3000"
        echo ""
        break
    else
        echo "📁 Model file: Not yet created"
    fi

    # Check if training process is still running
    if ps aux | grep -q "[p]ython ml/train_model_land_registry.py"; then
        cpu_mem=$(ps aux | grep "[p]ython ml/train_model_land_registry.py" | awk '{print "CPU: " $3 "%, Memory: " $6 " KB"}')
        echo "💻 Process: Running ($cpu_mem)"
    else
        if [ ! -f "$MODEL_FILE" ]; then
            echo "❌ Training process ended but model not found!"
            echo "   Check the full output file for errors."
            break
        fi
    fi

    echo "========================================================================"

    # Wait 10 seconds before next check
    sleep 10
done

echo ""
