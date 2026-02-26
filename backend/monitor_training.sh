#!/bin/bash
# Monitor LightGBM training progress

echo "🚀 Monitoring LightGBM Training..."
echo "=================================="
echo ""

while true; do
    clear
    echo "🚀 LightGBM Training Monitor"
    echo "============================="
    echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    # Check if training is still running
    if pgrep -f "train_lightgbm_with_plot.py" > /dev/null; then
        echo "✓ Training is running..."
        echo ""

        # Show tail of output
        if [ -f "/tmp/claude-1000/-home-user/tasks/bfa40e0.output" ]; then
            echo "📊 Recent output:"
            tail -20 "/tmp/claude-1000/-home-user/tasks/bfa40e0.output"
        fi
    else
        echo "✓ Training completed or not running"
        echo ""

        # Check for output files
        if [ -f "ml/lightgbm_loss_progression.png" ]; then
            echo "✅ Loss graph created: ml/lightgbm_loss_progression.png"
            ls -lh ml/lightgbm_loss_progression.png
        fi

        if [ -f "ml/lightgbm_loss_history.csv" ]; then
            echo "✅ Loss history CSV created: ml/lightgbm_loss_history.csv"
            head -10 ml/lightgbm_loss_history.csv
        fi

        break
    fi

    echo ""
    echo "Refreshing in 10 seconds... (Press Ctrl+C to exit)"
    sleep 10
done

echo ""
echo "Done! Check the loss graph at: ml/lightgbm_loss_progression.png"
