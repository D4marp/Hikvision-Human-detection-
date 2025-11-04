#!/bin/bash

# Multi-Camera Human Detection Runner
# Easy way to start multi-camera system

echo "=========================================="
echo "Multi-Camera Human Detection System"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if model exists
if [ ! -f "models/yolov8n.pt" ]; then
    echo "❌ Model not found!"
    echo "   Model will be downloaded automatically..."
fi

# Run multi-camera system
echo "Starting multi-camera system..."
echo ""

python run_multi_camera.py

# Deactivate when done
deactivate

echo ""
echo "=========================================="
echo "System stopped"
echo "=========================================="
