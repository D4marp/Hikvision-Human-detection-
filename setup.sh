#!/bin/bash
# Quick Start Script untuk Hikvision Detection System

echo "╔════════════════════════════════════════════════════════╗"
echo "║  🎥 Hikvision Detection System - Quick Start          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 not found. Please install Python 3.9+"
    exit 1
fi
python3 --version

echo ""
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "✓ Activating virtual environment..."
source venv/bin/activate

echo ""
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✓ Downloading models..."
python3 -c "from ultralytics import YOLO; YOLO('yolov5nu.pt'); print('  ✓ YOLOv5nu downloaded')" 2>/dev/null || true
python3 -c "from ultralytics import YOLO; YOLO('yolov8m.pt'); print('  ✓ YOLOv8m downloaded')" 2>/dev/null || true

echo ""
echo "═════════════════════════════════════════════════════════"
echo ""
echo "✅ Installation Complete!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "  1️⃣  WEB DASHBOARD (Recommended)"
echo "     python run_web_server.py"
echo "     Then open: http://localhost:5000"
echo ""
echo "  2️⃣  SINGLE CAMERA"
echo "     python src/main.py --rtsp rtsp://admin:password@10.0.66.29:554/Streaming/Channels/102 --conf 0.40"
echo ""
echo "  3️⃣  MULTI-CAMERA"
echo "     python run_multi_camera.py"
echo ""
echo "  4️⃣  ADVANCED DETECTION"
echo "     python run_advanced_detection.py --rtsp <RTSP_URL> --conf 0.45"
echo ""
echo "═════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "   - README_FULL.md - Complete guide"
echo "   - WEB_DASHBOARD_GUIDE.md - Web interface guide"
echo "   - ARCHITECTURE.md - System architecture"
echo ""
echo "🎥 Example RTSP URL:"
echo "   rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102"
echo ""
echo "═════════════════════════════════════════════════════════"
