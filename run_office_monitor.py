#!/usr/bin/env python3
"""
Office Productivity Monitor - Web Server Launcher
Real-time monitoring for office workers with zero delay
"""

import sys
import logging
from src.web_server import run_server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🏢 OFFICE PRODUCTIVITY MONITOR - WEB SERVER              ║
║                                                                ║
║     Real-Time Worker Activity & Effectiveness Tracking       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📊 Features:
   ✓ Real-time sitting duration tracking
   ✓ Posture & activity level detection
   ✓ Effectiveness scoring (0-100)
   ✓ Health & productivity recommendations
   ✓ Zero delay WebSocket streaming
   ✓ Professional dashboard UI

🌐 Access URLs:
   General Dashboard: http://localhost:5000
   Office Monitor:    http://localhost:5000/office
   API Status:        http://localhost:5000/api/status

📌 Quick Start:
   1. Add camera with "office" mode
   2. Enter RTSP URL (e.g., rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102)
   3. Start monitoring

⚙️ Detection Modes:
   - office:    Productivity & sitting duration tracking
   - advanced:  Helmet, weapon, safety detection
   - simple:    Person detection only

🚀 Starting server...
""")

    try:
        run_server(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        sys.exit(1)
