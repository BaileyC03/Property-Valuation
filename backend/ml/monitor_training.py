#!/usr/bin/env python3
"""
Real-time training progress monitor.
Watch the training of the Land Registry model in your terminal.
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

def get_current_epoch():
    """Extract current epoch from training output."""
    try:
        # Check if task output file exists
        output_files = [
            "/tmp/claude-1000/-home-user/tasks/b8df353.output",
            "/tmp/claude-*/tasks/b8df353.output"
        ]

        for pattern in output_files:
            if "*" in pattern:
                import glob
                files = glob.glob(pattern)
                if files:
                    output_file = files[0]
                    break
            else:
                output_file = pattern
                if os.path.exists(output_file):
                    break
        else:
            return None, None, None

        if not os.path.exists(output_file):
            return None, None, None

        # Get last 50 lines
        result = subprocess.run(
            f"tail -50 {output_file}",
            shell=True,
            capture_output=True,
            text=True
        )

        lines = result.stdout.split('\n')

        # Look for epoch and loss info
        epoch_info = None
        loss_info = None

        for line in reversed(lines):
            if 'Epoch' in line and '/' in line:
                # Extract epoch number (e.g., "Epoch 37/200")
                parts = line.split('Epoch')
                if len(parts) > 1:
                    epoch_str = parts[1].strip().split('[')[0].strip()
                    epoch_info = epoch_str

            if 'loss:' in line or 'mae:' in line or 'mse:' in line:
                loss_info = line.strip()
                break

        return epoch_info, loss_info, output_file
    except Exception as e:
        return None, None, None

def check_model_file():
    """Check if model file has been created."""
    model_path = Path("ml/model_land_registry.h5")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        return True, size_mb
    return False, 0

def print_header():
    """Print monitor header."""
    print("\n" + "="*70)
    print("🚀 LAND REGISTRY MODEL TRAINING MONITOR")
    print("="*70 + "\n")

def main():
    """Main monitoring loop."""
    print_header()

    start_time = datetime.now()
    check_count = 0

    while True:
        check_count += 1
        current_time = datetime.now()
        elapsed = current_time - start_time
        elapsed_str = f"{int(elapsed.total_seconds() // 3600)}h {int((elapsed.total_seconds() % 3600) // 60)}m"

        # Get training status
        epoch_info, loss_info, output_file = get_current_epoch()
        model_exists, model_size = check_model_file()

        # Clear and print status
        print(f"\n[{current_time.strftime('%H:%M:%S')}] Elapsed: {elapsed_str}")
        print("-" * 70)

        if epoch_info:
            print(f"📊 Epoch: {epoch_info}")

            # Parse epoch to show progress
            try:
                current, total = epoch_info.split('/')
                current_int = int(current)
                total_int = int(total)
                progress_pct = (current_int / total_int) * 100

                # Progress bar
                bar_length = 40
                filled = int(bar_length * current_int / total_int)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"   Progress: [{bar}] {progress_pct:.1f}%")
            except:
                pass
        else:
            print("📊 Epoch: Waiting for training to start...")

        if loss_info:
            print(f"📈 Loss: {loss_info}")

        if model_exists:
            print(f"\n✅ MODEL FILE CREATED!")
            print(f"   Size: {model_size:.1f} MB")
            print("\n" + "="*70)
            print("🎉 Training completed successfully!")
            print("="*70)
            print("\nNext steps:")
            print("  1. Press Ctrl+C to exit this monitor")
            print("  2. Run: cd backend && source venv/bin/activate && python app.py")
            print("  3. In another terminal: cd frontend && npm start")
            print("  4. Open http://localhost:3000")
            print()
            break
        else:
            print(f"📁 Model file: Not yet created")

        # Check if process is still running
        result = subprocess.run(
            "ps aux | grep '[p]ython ml/train_model_land_registry.py'",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            # Process is running
            # Extract CPU and memory
            parts = result.stdout.split()
            if len(parts) > 5:
                cpu = parts[2]
                mem = parts[5]
                print(f"💻 Process: Running (CPU: {cpu}%, Memory: {mem} KB)")
        else:
            # Process finished
            if not model_exists:
                print("❌ Training process ended but model not found!")
                print("   Check output file for errors.")
                break

        print("="*70)

        # Wait before next check
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
