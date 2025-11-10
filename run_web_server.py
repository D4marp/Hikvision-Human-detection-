#!/usr/bin/env python3
"""
Hikvision Detection Web Server - Launcher
Flask + SocketIO untuk monitoring dashboard
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.web_server import app, socketio, logger

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("HIKVISION DETECTION WEB SERVER")
    logger.info("="*60)
    logger.info("")
    logger.info("🚀 Starting server...")
    logger.info("")
    logger.info("📊 Open Dashboard at:")
    logger.info("   http://localhost:5000")
    logger.info("")
    logger.info("🔌 WebSocket enabled for real-time streaming")
    logger.info("🎥 Multi-camera support")
    logger.info("📌 Embed-ready for integration")
    logger.info("")
    logger.info("="*60)
    
    # Run Flask + SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True,
        log_output=True
    )
