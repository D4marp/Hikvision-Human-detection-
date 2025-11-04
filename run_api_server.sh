#!/bin/bash

# Human Detection REST API Server Launcher
# Untuk integrasi dengan Node-RED, Milesight, dan sistem IoT lainnya

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Human Detection REST API Server"
echo "=========================================="
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment tidak ditemukan!"
    echo "Run: python3.10 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Flask installed
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask tidak terinstall!"
    echo "Run: pip install flask flask-cors requests"
    exit 1
fi

# Check model
if [ ! -f "models/yolov8n.pt" ]; then
    echo "❌ Model yolov8n.pt tidak ditemukan!"
    echo "Model akan di-download otomatis saat pertama kali run"
fi

echo "✅ Environment ready"
echo ""
echo "🚀 Starting API Server..."
echo "   URL: http://localhost:5000"
echo "   Documentation: http://localhost:5000/"
echo ""
echo "📡 Integration endpoints:"
echo "   - Node-RED: http://localhost:5000/api/events"
echo "   - Milesight: Configure via /api/milesight/configure"
echo "   - Webhook: Configure via /api/webhook/configure"
echo ""
echo "Press Ctrl+C to stop server"
echo "=========================================="
echo ""

# Start API server
python src/api_server.py
