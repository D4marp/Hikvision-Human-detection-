# 🌐 How to Start Web Dashboard Locally (Testing with Your Computer)

## ⚡ Quick Start (On Your Local Machine)

### Step 1: Install Dependencies
```bash
# Open Terminal/Command Prompt on your computer

# If you have Python 3 installed:
pip3 install opencv-python flask flask-cors python-socketio

# Or if you use pip:
pip install opencv-python flask flask-cors python-socketio
```

### Step 2: Clone/Get the Project
```bash
# Navigate to project folder
cd /Users/HCMPublic/Kuliah/Project/hikvision_human_detection

# Or download from GitHub
git clone https://github.com/D4marp/Hikvision-Human-detection-.git
cd Hikvision-Human-detection-
git checkout New
```

### Step 3: Start Web Server
```bash
# On your computer, run:
python3 run_web_server.py

# You should see:
# Running on http://localhost:5000
# Press CTRL+C to quit
```

### Step 4: Open Dashboard
```
Open your browser and go to:
http://localhost:5000

You will see:
✓ Header with mode selector buttons
✓ Add camera form
✓ Real-time statistics
✓ Empty camera grid (waiting for cameras)
```

### Step 5: Select Office Mode
```
Click: [🏢 Office]

Dashboard will:
1. Change colors to cyan/bright cyan
2. Update form header to "Add Camera [🏢 Office Mode]"
3. Show worker statistics section
4. Reset camera list
```

### Step 6: Add Your Hikvision Camera

**Fill the form:**
```
Camera ID:    office-desk-1
RTSP URL:     rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102
Mode:         office (auto-selected)

Click: [Add Camera →]
```

### Step 7: Monitor!

**What you'll see:**
- ✅ Live video stream from your camera
- ✅ Real-time FPS counter
- ✅ Person detection bounding boxes
- ✅ Sitting duration counter
- ✅ Activity level (idle/active/very_active)
- ✅ Effectiveness score (0-100)
- ✅ Posture (sitting/standing/bending)
- ✅ Worker statistics cards
- ✅ Real-time alerts
- ✅ Health recommendations

---

## 🎯 Dashboard Features When Running

### Top Section
```
📹 Hikvision Monitoring System  [🎯] [🔒] [🏢]
                                        ↑ Click to switch modes
```

### Add Camera Section
```
➕ Add Camera [🏢 Office Mode]
┌─────────────────────────────┐
│ Camera ID:  [office-desk-1] │
│ RTSP URL:   [rtsp://...]    │
│ Mode:       [office ▼]      │
│             [Add Camera →]  │
└─────────────────────────────┘
```

### Statistics Panel
```
🎥 Active Cameras: 1    |    🔍 Total Detections: 2
📊 Average FPS: 22.5    |    ⚠️  Active Alerts: 1
```

### Camera Grid
```
┌─────────────────────────────┐
│ 📹 Office Desk 1            │
│ 🏢 Office | 🟢 Connected   │
│                             │
│  [LIVE VIDEO STREAM]        │
│  (with detection overlay)   │
│                             │
│ FPS: 22 | Frames: 1850     │
└─────────────────────────────┘
```

### Worker Statistics (Office Mode Only)
```
┌──────────────────────────┐
│ Worker #0 - Score 85 [B] │
├──────────────────────────┤
│ Sitting: 145s (Normal)  │
│ Activity: Active (60%)   │
│ Posture: Sitting        │
│ Risk: 🟢 NORMAL         │
│ 💡 Keep working!        │
└──────────────────────────┘

┌──────────────────────────┐
│ Worker #1 - Score 62 [D] │
├──────────────────────────┤
│ Sitting: 340s (High)    │
│ Activity: Idle (20%)    │
│ Posture: Bending       │
│ Risk: 🔴 HIGH          │
│ 💡 Take a break!       │
└──────────────────────────┘
```

### Alerts Section
```
🚨 Real-time Alerts

⏰ 14:32 - Worker #1 sitting 340s - Take a break!
⚠️  14:31 - Low activity detected for Worker #0
✅ 14:30 - Camera office-desk-1 connected
```

---

## 🔄 Real-Time Updates

**Everything Updates Automatically:**

- 🎥 **Video Stream**: Refreshes ~every 50-100ms
- 📊 **Statistics**: Updates every 1 second
- 👥 **Worker Stats**: Updates every frame detection
- ⚠️ **Alerts**: Appear instantly
- 📈 **FPS Counter**: Real-time

**No Page Reload Needed!**
- Click mode buttons → Dashboard updates instantly
- Add camera → Video appears automatically
- Alerts appear in real-time

---

## 🎨 Mode Switching

### General Mode (🎯 Blue)
```
[🎯 General] ← Click to activate

Changes:
• Header turns blue/purple
• Form: "Add Camera [🎯 General Mode]"
• No worker stats
• Shows: Person detection only
```

### Security Mode (🔒 Pink/Red)
```
[🔒 Security] ← Click to activate

Changes:
• Header turns pink/red
• Form: "Add Camera [🔒 Security Mode]"
• No worker stats
• Shows: Helmet, weapon, smoke detection
```

### Office Mode (🏢 Cyan)
```
[🏢 Office] ← Click to activate

Changes:
• Header turns cyan/bright cyan
• Form: "Add Camera [🏢 Office Mode]"
• Worker stats section appears
• Shows: Sitting duration, effectiveness score, activity, posture
```

---

## 📱 Responsive Design

**On Different Screen Sizes:**

### Desktop (1200px+)
```
┌─────────────────────────────────────┐
│ Header with mode selector           │
├─────────────────────────────────────┤
│ Add Camera Form                     │
├─────────────────────────────────────┤
│ Statistics Bar                      │
├─────────────────────────────────────┤
│ Camera 1    │ Camera 2   │ Camera 3 │
├─────────────────────────────────────┤
│ Worker 1    │ Worker 2   │ Worker 3 │
├─────────────────────────────────────┤
│ Alerts                              │
└─────────────────────────────────────┘
```

### Tablet (768px+)
```
┌──────────────────────────┐
│ Header                   │
├──────────────────────────┤
│ Add Camera Form          │
├──────────────────────────┤
│ Statistics               │
├──────────────────────────┤
│ Camera 1                 │
├──────────────────────────┤
│ Camera 2                 │
├──────────────────────────┤
│ Worker Stats             │
├──────────────────────────┤
│ Alerts                   │
└──────────────────────────┘
```

### Mobile (<768px)
```
┌──────────────┐
│ Header       │
├──────────────┤
│ Form         │
├──────────────┤
│ Stats        │
├──────────────┤
│ Camera       │
├──────────────┤
│ Worker 1     │
├──────────────┤
│ Worker 2     │
├──────────────┤
│ Alerts       │
└──────────────┘
```

---

## 🎓 Example Workflow

### Scenario: Monitor Office Desk

**1. Start Server (Terminal)**
```bash
python3 run_web_server.py
```

**2. Open Browser**
```
http://localhost:5000
```

**3. Click Office Mode**
```
[🏢 Office] ← Current: General
```

**4. Fill Camera Details**
```
Camera ID:    office-desk-1
RTSP URL:     rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102
```

**5. Click Add Camera**
```
[Add Camera →]
```

**6. Watch Real-Time Monitoring**
```
✓ Live video appears
✓ Person detected
✓ Sitting duration: 0s → 1s → 2s...
✓ Activity level detected
✓ Effectiveness score calculated
✓ Worker stats show in cards
✓ Alerts appear when needed
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'cv2'"

**Solution:**
```bash
pip3 install opencv-python
# or
pip install opencv-python
```

### Problem: "Connection refused - Port 5000"

**Solution:**
```bash
# Port might be in use, try different port
# Edit run_web_server.py and change port from 5000 to 5001
```

### Problem: "Camera not connecting"

**Solution:**
```bash
# Check RTSP URL is correct:
rtsp://username:password@ip:port/path

# Test with test_camera.py:
python3 test_camera.py

# Verify camera details:
IP: 10.0.66.29 (or yours)
Port: 554 (Hikvision default)
Username: admin
Password: your_password
Channel: 102 (or your channel)
```

### Problem: "No video in dashboard"

**Solution:**
```bash
# 1. Check server console for errors
# 2. Check browser console (F12 → Console tab)
# 3. Ensure camera RTSP URL is correct
# 4. Try simple test first:
python3 test_camera.py
```

### Problem: "Sitting duration not tracking"

**Solution:**
```bash
# 1. Ensure full body visible in camera
# 2. Camera angle should be front/side
# 3. Check pose estimation working:
# Look for "Posture: SITTING" in detection overlay
```

---

## ⚙️ Advanced Configuration

### Multiple Cameras

**In Dashboard:**
```
1. Add Camera 1
   Camera ID: office-desk-1
   RTSP: rtsp://...102
   Click: [Add Camera →]

2. Add Camera 2
   Camera ID: office-desk-2
   RTSP: rtsp://...103
   Click: [Add Camera →]

3. Add Camera 3
   Camera ID: conference-room
   RTSP: rtsp://...104
   Click: [Add Camera →]

Result: All 3 cameras shown in grid!
```

### Custom Settings

**Edit src/web_server.py:**
```python
# Detection confidence
MIN_CONFIDENCE = 0.5  # 0.0-1.0

# JPEG quality
JPEG_QUALITY = 85  # 0-100

# Frame skip
FRAME_SKIP = 2  # Process every Nth frame

# Max cameras
MAX_CAMERAS = 5  # Per mode
```

---

## 📊 What Each Metric Means

### Sitting Duration
- **0-20 min**: ✅ Normal
- **20-30 min**: ⚠️ Soon break needed
- **30-60 min**: 🟡 Take break
- **60+ min**: 🔴 Critical

### Effectiveness Score (0-100)
- **90-100**: ⭐ Excellent (Grade A)
- **80-89**: ✅ Good (Grade B)
- **70-79**: 😐 Fair (Grade C)
- **60-69**: ⚠️ Poor (Grade D)
- **< 60**: ❌ Fail (Grade F)

### Activity Level
- **Idle**: Sitting still, not moving
- **Active**: Normal movement
- **Very Active**: Lots of movement

### Posture
- **Sitting**: Normal office position
- **Standing**: Good for health
- **Bending**: Watch for back issues

---

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip3 install gunicorn

# Run server (production)
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 src.web_server:app

# Access from any device:
http://your_computer_ip:5000
```

### Using Docker

```bash
# Build image
docker build -t office-monitor .

# Run container
docker run -p 5000:5000 office-monitor

# Access:
http://localhost:5000
```

---

## 💡 Tips & Tricks

### Tip 1: Multiple Modes
- Add General mode camera for entrance
- Add Security mode camera for warehouse
- Add Office mode for desk monitoring
- All in same dashboard!

### Tip 2: Real-Time Monitoring
- Dashboard updates without refresh
- Alerts appear instantly
- No delay in video streaming
- Professional real-time experience

### Tip 3: Worker Statistics
- Only visible in Office mode
- Shows effectiveness score
- Tracks sitting duration
- Recommends breaks automatically

### Tip 4: Mobile Access
- Access from tablet/phone
- Responsive design adapts
- Works on any device
- Same features on all screens

### Tip 5: Performance
- Use Office mode for 3-5 cameras
- Use General mode for 10+ cameras
- Monitor CPU usage
- Adjust frame skip if needed

---

## 📞 Need Help?

**Check These Files:**
1. `UNIFIED_DASHBOARD_GUIDE.md` - Complete dashboard guide
2. `OFFICE_MONITOR_GUIDE.md` - Office features guide
3. `README.md` - Project overview
4. Run `python3 test_system_complete.py` - Verify everything works

---

## ✨ You're Ready!

```bash
# 1. Install dependencies
pip3 install opencv-python flask flask-cors python-socketio

# 2. Start web server
python3 run_web_server.py

# 3. Open browser
http://localhost:5000

# 4. Select mode and add camera
[🏢 Office] → Add Camera → Monitor!

🎉 Enjoy real-time office detection!
```
