#!/usr/bin/env python3
"""
Web Dashboard Test & Demo
Shows how the office detection system works with camera feed
"""

import sys
import json
from datetime import datetime

print("\n" + "="*80)
print("🎥 WEB DASHBOARD - INTERACTIVE DEMO")
print("="*80)

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              🌐 OFFICE DETECTION WEB DASHBOARD - DEMO                     ║
║                                                                            ║
║  This demo shows what the web interface looks like and how it works       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📍 DASHBOARD URL: http://localhost:5000

""")

# Demo dashboard structure
dashboard = {
    "header": {
        "title": "📹 Hikvision Monitoring System",
        "mode_buttons": ["🎯 General", "🔒 Security", "🏢 Office"],
        "active_mode": "🏢 Office"
    },
    "add_camera_form": {
        "label": "➕ Add Camera [🏢 Office Mode]",
        "fields": {
            "camera_id": "office-desk-1",
            "rtsp_url": "rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102",
            "detection_mode": "office"
        }
    },
    "statistics": {
        "🎥 Active Cameras": 2,
        "🔍 Total Detections": 8,
        "📊 Average FPS": "18.5",
        "⚠️  Active Alerts": 1
    },
    "cameras": [
        {
            "id": "cam-office-1",
            "name": "Office Desk 1",
            "mode": "🏢 Office",
            "status": "🟢 Connected",
            "fps": 22,
            "frames": 1850
        },
        {
            "id": "cam-office-2", 
            "name": "Office Desk 2",
            "mode": "🏢 Office",
            "status": "🟢 Connected",
            "fps": 20,
            "frames": 1640
        }
    ],
    "worker_stats": [
        {
            "id": 0,
            "name": "Worker #0",
            "effectiveness_score": 85,
            "grade": "B",
            "sitting_duration": "145 seconds",
            "activity": "Active (60%)",
            "posture": "Sitting",
            "risk": "🟢 NORMAL",
            "recommendation": "Keep working! Good activity level"
        },
        {
            "id": 1,
            "name": "Worker #1",
            "effectiveness_score": 62,
            "grade": "D",
            "sitting_duration": "340 seconds",
            "activity": "Idle (20%)",
            "posture": "Bending",
            "risk": "🔴 HIGH",
            "recommendation": "Take a break! You've been sitting for 5+ minutes"
        }
    ],
    "alerts": [
        {
            "timestamp": "14:32",
            "level": "warning",
            "message": "Worker #1 sitting 340s - Take a break!",
            "icon": "⏰"
        },
        {
            "timestamp": "14:30",
            "level": "info",
            "message": "Camera office-desk-1 added",
            "icon": "✅"
        }
    ]
}

print("┌" + "─"*78 + "┐")
print("│" + " DASHBOARD LAYOUT ".center(78) + "│")
print("└" + "─"*78 + "┘\n")

# Header section
print("📌 HEADER SECTION")
print("─" * 80)
print(f"  Title: {dashboard['header']['title']}")
print(f"  Mode Selector: {' | '.join(dashboard['header']['mode_buttons'])}")
print(f"  Current Mode: {dashboard['header']['active_mode']}")
print()

# Add Camera Form
print("📝 ADD CAMERA FORM")
print("─" * 80)
print(f"  {dashboard['add_camera_form']['label']}")
print(f"  Camera ID:      {dashboard['add_camera_form']['fields']['camera_id']}")
print(f"  RTSP URL:       {dashboard['add_camera_form']['fields']['rtsp_url']}")
print(f"  Mode:           {dashboard['add_camera_form']['fields']['detection_mode']}")
print(f"  Action:         [Add Camera →]")
print()

# Statistics
print("📊 REAL-TIME STATISTICS")
print("─" * 80)
for key, value in dashboard['statistics'].items():
    print(f"  {key:<25} {value}")
print()

# Camera Grid
print("🎥 CAMERA FEED GRID")
print("─" * 80)
for cam in dashboard['cameras']:
    print(f"""
  ┌─ {cam['name']}
  ├─ ID:      {cam['id']}
  ├─ Mode:    {cam['mode']}
  ├─ Status:  {cam['status']}
  ├─ FPS:     {cam['fps']}
  └─ Frames:  {cam['frames']}
  
  [📹 VIDEO STREAM HERE]""")
print()

# Worker Statistics
print("👥 WORKER STATISTICS (Office Mode Only)")
print("─" * 80)
for worker in dashboard['worker_stats']:
    print(f"""
  ┌─ {worker['name']} - Score: {worker['effectiveness_score']} [Grade: {worker['grade']}]
  ├─ Sitting:     {worker['sitting_duration']}
  ├─ Activity:    {worker['activity']}
  ├─ Posture:     {worker['posture']}
  ├─ Risk Level:  {worker['risk']}
  └─ 💡 Tip:      {worker['recommendation']}""")
print()

# Alerts
print("🚨 REAL-TIME ALERTS")
print("─" * 80)
for alert in dashboard['alerts']:
    print(f"  {alert['icon']} {alert['timestamp']} - {alert['message']}")
print()

# How to use
print("\n" + "="*80)
print("🎯 HOW TO USE THE DASHBOARD")
print("="*80)
print("""
1️⃣  START WEB SERVER
    ─────────────────
    python3 run_web_server.py
    
    Output:
    * Running on http://localhost:5000
    * Waiting for camera connections...

2️⃣  OPEN BROWSER
    ──────────────
    http://localhost:5000
    
    You will see:
    * Header with mode selector
    * Add camera form
    * Real-time statistics
    * Empty camera grid (waiting for cameras)

3️⃣  SELECT MODE
    ────────────
    Click one of:
    [🎯 General] [🔒 Security] [🏢 Office]
    
    Effects:
    • Form updates for selected mode
    • UI colors change per mode
    • Worker stats shown (office mode only)
    • Camera list persists

4️⃣  ADD CAMERA
    ───────────
    Camera ID:  office-desk-1
    RTSP URL:   rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102
    Mode:       office (auto-selected)
    
    Click: [Add Camera →]

5️⃣  MONITOR LIVE
    ──────────────
    Dashboard shows:
    • Live video stream from camera
    • Real-time FPS counter
    • Sitting duration tracking
    • Effectiveness score (0-100)
    • Activity level
    • Posture detection
    • Automatic alerts
    • Worker statistics

6️⃣  SWITCH MODES
    ──────────────
    No page reload needed!
    Click [🎯] or [🔒] or [🏢]
    
    Dashboard instantly:
    • Changes colors
    • Updates form
    • Resets camera list (new mode)
    • Shows/hides worker stats

""")

print("="*80)
print("🎨 UI/UX FEATURES")
print("="*80)
print("""
✅ REAL-TIME UPDATES
   • WebSocket streaming (instant updates)
   • No page reload required
   • Live statistics update every second
   • Frame-by-frame detection overlay

✅ MULTI-MODE INTERFACE
   • 3 modes in 1 dashboard
   • Easy mode switching
   • Color-coded per mode
   • Persistent camera list per mode

✅ RESPONSIVE DESIGN
   • Desktop: Full grid layout
   • Tablet: Single column
   • Mobile: Stacked layout
   • Touch-friendly controls

✅ PROFESSIONAL STYLING
   • Gradient backgrounds
   • Color-coded alerts
   • Real-time animations
   • Professional fonts & spacing

✅ WORKER PRODUCTIVITY (Office Mode)
   • Effectiveness score visualization
   • Sitting duration alerts
   • Activity level charts
   • Health recommendations
   • Risk level indicators

✅ REAL-TIME ALERTS
   • Color-coded severity
   • Timestamps
   • Auto-clear old alerts
   • Works for all modes

""")

print("="*80)
print("📊 OFFICE MODE - SPECIFIC FEATURES")
print("="*80)
print("""
When you select [🏢 Office] mode:

1. ADD CAMERA FORM UPDATES
   └─ Camera ID: [_____________]
   └─ RTSP URL:  [_________________________________]
   └─ Mode:      [office ▼] (auto-selected)
   └─ [Add Camera →]

2. DASHBOARD COLORS CHANGE
   └─ Primary color: Cyan (#4facfe)
   └─ Secondary color: Bright cyan (#00f2fe)
   └─ Gradient background
   └─ Headers: "🏢 Add Camera [🏢 Office Mode]"

3. WORKER STATISTICS APPEAR
   └─ Show only in office mode
   └─ Auto-hide in other modes
   └─ Worker cards with:
      ├─ Effectiveness score (0-100)
      ├─ Grade (A-F)
      ├─ Sitting duration
      ├─ Activity level
      ├─ Posture
      ├─ Risk level
      └─ Health recommendation

4. CAMERA GRID UPDATES
   └─ Shows live video from camera
   └─ Real-time FPS counter
   └─ Detection overlay:
      ├─ Person bounding boxes
      ├─ Sitting duration text
      ├─ Activity level
      ├─ Effectiveness score
      └─ Posture type

5. ALERTS ARE OFFICE-SPECIFIC
   └─ "Worker #1 sitting 340s - Take break!"
   └─ "Low effectiveness: Worker #0 idle"
   └─ "Posture warning: Worker #1 bending"
   └─ "Health check: Recommend standing"

6. STATISTICS UPDATE REAL-TIME
   └─ 🎥 Active Cameras: 1
   └─ 🔍 Total Detections: 2
   └─ 📊 Average FPS: 18.5
   └─ ⚠️  Active Alerts: 1

""")

print("="*80)
print("💻 EXAMPLE CAMERA SETUP")
print("="*80)
print("""
For Hikvision Cameras:

  Camera 1 (Front Desk):
  ├─ Camera ID: front-desk-1
  ├─ RTSP: rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/101
  └─ Mode: 🏢 Office

  Camera 2 (Reception Area):
  ├─ Camera ID: reception-1
  ├─ RTSP: rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102
  └─ Mode: 🏢 Office

  Camera 3 (Security Gate):
  ├─ Camera ID: gate-security-1
  ├─ RTSP: rtsp://admin:Novarion1@10.0.66.30:554/Streaming/Channels/101
  └─ Mode: 🔒 Security

All cameras can be monitored from same dashboard!

""")

print("="*80)
print("🚀 START TESTING NOW")
print("="*80)
print("""
Command:
  python3 run_web_server.py

Then:
  1. Open: http://localhost:5000
  2. You'll see the dashboard as shown above
  3. Click [🏢 Office] to see office-specific UI
  4. Add your Hikvision camera RTSP URL
  5. Watch real-time detection with sitting duration & effectiveness scores!

The dashboard will show:
  ✓ Live video stream
  ✓ Real-time FPS counter
  ✓ Worker statistics
  ✓ Effectiveness scores
  ✓ Activity levels
  ✓ Posture detection
  ✓ Sitting duration tracking
  ✓ Health recommendations
  ✓ Real-time alerts

Everything updates in real-time without page reload!

""")

print("="*80)
print("✨ SYSTEM READY - START WEB SERVER TO SEE IT IN ACTION!")
print("="*80 + "\n")
