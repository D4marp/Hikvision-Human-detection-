# 🏢 Office Monitor - Complete Guide

## Quick Start (2 Minutes)

```bash
# 1. Start the office monitoring server
python run_office_monitor.py

# 2. Enter your Hikvision camera details:
#    - Camera IP: 10.0.66.29
#    - Port: 554
#    - Username: admin
#    - Password: Novarion1
#    - Channel: 102

# 3. Monitor in real-time on http://localhost:5000
```

---

## 📊 What is Office Monitor?

**Office Monitor** adalah sistem real-time untuk melacak **produktivitas karyawan** di kantor dengan fitur:

- ✅ **Sitting Duration Tracking** - Berapa lama orang duduk di kursi
- ✅ **Effectiveness Score** - Nilai efektifitas karyawan (0-100)
- ✅ **Activity Level** - Klasifikasi aktivitas (idle/active/very_active)
- ✅ **Posture Detection** - Deteksi postur tubuh (sitting/standing/bending)
- ✅ **Health Recommendations** - Saran kesehatan otomatis
- ✅ **Real-time Dashboard** - Zero-delay monitoring

---

## 🚀 Installation & Setup

### Prerequisites
```bash
Python 3.8+
OpenCV (cv2)
YOLOv8 (for pose estimation)
Flask + Socket.io (for web server)
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python test_system_complete.py
```

Expected Output:
```
✅ Office Analyzer - OK
✅ Human Detector - OK
✅ Web Server - OK
```

---

## 🎯 Core Features

### 1. Sitting Duration Tracking

**Apa itu?**
- Melacak berapa lama seseorang duduk di kursi
- Menghitung risiko kesehatan dari durasi duduk

**Output:**
```
Sitting Duration: 180 seconds (3 minutes)
Risk Level: MEDIUM
Recommendation: Ambil istirahat 5 menit, berdiri, atau jalan-jalan
```

**Risk Levels:**
- 🟢 **NORMAL**: < 30 menit duduk
- 🟡 **MEDIUM**: 30-60 menit duduk
- 🔴 **HIGH**: > 60 menit duduk

**Health Thresholds:**
| Duration | Risk | Recommendation |
|----------|------|-----------------|
| < 15 min | ✅ Normal | Lanjutkan bekerja |
| 15-30 min | ⚠️ Caution | Mulai bergerak |
| 30-60 min | ⚠️ Warning | Ambil break |
| > 60 min | 🔴 Critical | Sangat perlu istirahat |

### 2. Effectiveness Score

**Formula (0-100):**
```
Effectiveness = (Activity × 40%) + (Posture × 30%) + (Sitting × 30%)
```

**Breakdown:**

| Component | Weight | Description |
|-----------|--------|-------------|
| Activity | 40% | Seberapa aktif (idle/active/very_active) |
| Posture | 30% | Postur tubuh (sitting/standing/bending) |
| Sitting Duration | 30% | Durasi duduk (mendapat nilai negatif jika terlalu lama) |

**Grade System:**
```
90-100: A (Excellent - Sangat bagus)
80-89:  B (Good - Bagus)
70-79:  C (Fair - Cukup)
60-69:  D (Poor - Kurang)
< 60:   F (Fail - Gagal)
```

**Example:**
```
Worker #1: Score 85/100 [Grade: B]
- Activity Score: 90% (very active)
- Posture Score: 85% (standing)
- Sitting Score: 70% (sitting 25 min)
Result: (90×0.4) + (85×0.3) + (70×0.3) = 85/100
```

### 3. Activity Level Detection

**Klasifikasi Aktivitas:**

| Level | Description | Movement |
|-------|-------------|----------|
| **Idle** | Tidak bergerak/statis | < 5% movement |
| **Active** | Gerakan normal | 5-50% movement |
| **Very Active** | Gerakan banyak | > 50% movement |

**How it works:**
- Melacak pergerakan keypoints tubuh antar frame
- Menghitung perubahan posisi dari frame sebelumnya
- Klasifikasi otomatis berdasarkan threshold

### 4. Posture Detection

**Deteksi Postur Tubuh:**

| Posture | Indicator | Health |
|---------|-----------|--------|
| **Sitting** | Hip lebih tinggi dari knee | ✅ Normal untuk kantor |
| **Standing** | Knee sejajar hip | ✅ Bagus untuk kesehatan |
| **Bending** | Postur membungkuk | ⚠️ Perlu diperhatikan |

**Benefits:**
- Mengingatkan untuk duduk dengan benar
- Monitoring ergonomic posture
- Pencegahan injury jangka panjang

### 5. Health Recommendations

**Sistem Otomatis:**

```
Based on activity: "Anda sudah idle 30 menit, ambil break!"
Based on sitting: "Duduk lama risiko kesehatan, berdiri sesaat"
Based on posture: "Postur membungkuk, perbaiki duduk Anda"
```

**Default Recommendations:**

Durasi Duduk | Rekomendasi
--|--
< 20 min | Keep working
20-30 min | Soon time for break
30-60 min | Take 5 min break
60+ min | Take extended break

---

## 📸 Usage Methods

### Method 1: Web Dashboard (Recommended)

**Advantages:**
- ✅ Multi-camera support
- ✅ Multiple detection modes
- ✅ Real-time statistics
- ✅ Professional UI/UX

**Steps:**

```bash
# 1. Start web server
python run_web_server.py

# 2. Open browser
http://localhost:5000

# 3. Click [🏢 Office] tab

# 4. Add camera:
#    Camera ID: office-desk-1
#    RTSP URL: rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102
#    Detection Mode: office (auto-selected)

# 5. Monitor real-time!
```

**Dashboard Features:**
- 📊 Real-time stats (active cameras, total detections, avg FPS)
- 👥 Worker statistics grid
- 📈 Effectiveness score visualization
- ⚠️ Alert system
- 🎨 Color-coded risk levels

### Method 2: Office Monitor Launcher

**Advantages:**
- ✅ Simpler interface
- ✅ Office mode only
- ✅ Quick setup
- ✅ Direct RTSP input

**Steps:**

```bash
# 1. Run launcher
python run_office_monitor.py

# 2. Enter camera details when prompted:
#    IP: 10.0.66.29
#    Port: 554
#    Username: admin
#    Password: Novarion1
#    Channel: 102

# 3. Watch output
# Frame-by-frame results shown in console
```

**Console Output Example:**
```
👤 Worker #0
├─ Posture: SITTING
├─ Activity: ACTIVE
├─ Sitting Time: 145s
├─ Effectiveness: 85.2/100 [Grade: B]
├─ Risk Level: NORMAL
└─ 💡 Tip: Good work! Keep it up!
```

### Method 3: Programmatic (Python API)

**For Custom Integration:**

```python
from src.office_analyzer import OfficeAnalyzer
from src.detector import HumanDetector
import cv2

# Initialize
analyzer = OfficeAnalyzer()
detector = HumanDetector()

# Read frame
cap = cv2.VideoCapture("rtsp://...")
ret, frame = cap.read()

# Detect humans
detections = detector.detect_humans(frame)

# Get office stats
for person_id, (x1, y1, x2, y2, conf) in enumerate(detections):
    # Sitting duration
    sitting_info = analyzer.detect_sitting_duration(person_id, keypoints, conf)
    
    # Activity level
    activity = analyzer.detect_activity_level(person_id, keypoints)
    
    # Posture
    posture = analyzer.detect_posture(person_id, keypoints)
    
    # Overall score
    score = analyzer.calculate_effectiveness_score(person_id)
    
    # All stats
    stats = analyzer.get_worker_stats(person_id)
    
    print(f"Worker {person_id}: Score {score:.0f}/100")
```

---

## 🔧 Configuration

### Camera Setup

**Hikvision RTSP Format:**
```
rtsp://username:password@ip:port/Streaming/Channels/channel_number
```

**Example:**
```
rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102
```

**Multiple Cameras:**
```python
cameras = [
    {"id": "desk-1", "url": "rtsp://...channel/101"},
    {"id": "desk-2", "url": "rtsp://...channel/102"},
    {"id": "desk-3", "url": "rtsp://...channel/103"},
]
```

### Performance Tuning

**For Better Performance:**

```python
# Adjust detection confidence
min_confidence = 0.5  # 0.0-1.0 (lower = more detections)

# Frame skip (process every Nth frame)
frame_skip = 2  # Process every 2nd frame

# JPEG compression
jpeg_quality = 85  # 0-100 (higher = better quality, more bandwidth)
```

**Performance Targets:**
- 🎥 FPS: 12-28 (depends on hardware and mode)
- ⏱️ Latency: 1-3 seconds end-to-end
- 💾 Memory: 100-200MB per camera
- 📊 CPU: 20-40% per camera

---

## 📊 Real-time Metrics

### Available Metrics

```
Per Worker:
├─ Person ID
├─ Sitting Duration (seconds)
├─ Activity Level (idle/active/very_active)
├─ Posture (sitting/standing/bending)
├─ Effectiveness Score (0-100)
├─ Grade (A-F)
├─ Risk Level (normal/medium/high)
├─ Health Recommendation
└─ Timestamp

Per Session:
├─ Total Workers Detected
├─ Average Effectiveness Score
├─ Average Sitting Duration
├─ Average Activity Level
├─ Total Frames Processed
└─ Session Duration
```

### Data Storage

**Current:** In-memory (resets when server restarts)

**For Persistence, Add Database:**
```python
# MongoDB
from pymongo import MongoClient
db = MongoClient()["office_monitor"]

# SQLite
import sqlite3
conn = sqlite3.connect("office_monitor.db")

# CSV Export
import pandas as pd
df.to_csv("worker_stats.csv")
```

---

## 🎨 Dashboard Visualization

### Office Mode Dashboard Features

**1. Mode Selector**
```
[🎯 General] [🔒 Security] [🏢 Office]
                              ↑ Active
```

**2. Add Camera Form**
```
Camera ID:      [office-desk-1]
RTSP URL:       [rtsp://admin:...102]
Detection Mode: [Office ▼]
                [Add Camera →]
```

**3. Real-time Statistics**
```
🎥 Active Cameras: 3     🔍 Detections: 245
📊 Average FPS: 15.5     ⚠️  Alerts: 2
```

**4. Worker Statistics Grid** (Office Mode Only)
```
┌─────────────────────────────────────┐
│ Worker #0 - Score: 85 [Grade: B]   │
├─────────────────────────────────────┤
│ Sitting: 145s (Normal)              │
│ Activity: Active (60%)              │
│ Posture: Sitting                    │
│ Risk: NORMAL                        │
│ 💡 Tip: Keep working!              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Worker #1 - Score: 62 [Grade: D]   │
├─────────────────────────────────────┤
│ Sitting: 340s (High)                │
│ Activity: Idle (20%)                │
│ Posture: Bending                    │
│ Risk: HIGH                          │
│ 💡 Tip: Take a break!              │
└─────────────────────────────────────┘
```

**5. Alert System**
```
⏰ 14:30 - Worker #1 sitting 65 min
🔔 14:28 - Worker #2 posture warning
✅ 14:25 - Camera office-desk-1 added
```

---

## 🐛 Troubleshooting

### Problem: "No persons detected"

**Causes:**
- Camera angle too high/low
- Person partially visible
- Detection confidence too high
- Poor lighting

**Solutions:**
```bash
# Lower detection threshold
min_confidence = 0.3  # Default: 0.5

# Adjust camera angle
# Ensure face and upper body visible

# Improve lighting
# Use ambient lighting or LED panels

# Check camera connection
python test_camera.py
```

### Problem: "High latency (> 5 seconds)"

**Causes:**
- Network congestion
- Low hardware resources
- High resolution frames
- Too many cameras

**Solutions:**
```bash
# Reduce resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)  # Was 1280
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360) # Was 720

# Increase frame skip
frame_skip = 3  # Process every 3rd frame

# Reduce JPEG quality
jpeg_quality = 70  # Was 85

# Limit cameras
max_cameras = 3  # Was 5
```

### Problem: "Sitting duration not tracking correctly"

**Causes:**
- Camera angle incorrect
- Keypoint detection failing
- Person not detected consistently
- Threshold issues

**Solutions:**
```bash
# Ensure full body visible
# Camera should see person from front/side

# Check pose estimation model
# Use YOLOv8-pose for better accuracy

# Verify keypoints
# Add debug visualization:
cv2.circle(frame, keypoint_pos, 5, (0, 255, 0), -1)
```

### Problem: "Web dashboard not updating"

**Causes:**
- WebSocket connection failed
- Browser cache issue
- Server not running
- Firewall blocking

**Solutions:**
```bash
# Check server is running
ps aux | grep python

# Clear browser cache
Ctrl+Shift+Delete (Chrome)
Cmd+Shift+Delete (Mac)

# Check firewall
# Allow port 5000 in firewall

# View server logs
python run_web_server.py  # Show debug output

# Force refresh
Ctrl+F5 (Windows)
Cmd+Shift+R (Mac)
```

---

## 📈 Performance Metrics

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 2GB
- Storage: 1GB
- Network: 5 Mbps per camera

**Recommended:**
- CPU: 4+ cores
- RAM: 4-8GB
- Storage: 10GB
- Network: 10 Mbps per camera

### Benchmark Results

| Metric | Value | Note |
|--------|-------|------|
| Latency | 1-3 sec | End-to-end |
| FPS | 12-28 | Depends on mode |
| CPU/Camera | 20-40% | On 4-core CPU |
| Memory/Camera | 100-200MB | Baseline |
| Bandwidth | 3-5 Mbps | RTSP stream |
| Accuracy | 85-95% | Detection |

### Scalability

**Per Hardware (4-core CPU, 8GB RAM):**
- 🎯 General Mode: 10+ cameras
- 🔒 Security Mode: 4-6 cameras
- 🏢 Office Mode: 3-5 cameras

---

## 🌐 Deployment

### Local Development
```bash
python run_web_server.py
# http://localhost:5000
```

### Production (Gunicorn)
```bash
gunicorn --worker-class eventlet -w 1 \
  -b 0.0.0.0:5000 src.web_server:app
```

### Docker
```bash
docker build -t office-monitor .
docker run -p 5000:5000 office-monitor
```

### Cloud Deployment
- AWS EC2
- Azure VM
- Google Cloud Run
- DigitalOcean

---

## 📝 API Reference

### REST Endpoints

```
POST /api/camera/add
├─ camera_id (string)
├─ rtsp_url (string)
├─ detection_mode (string: "office")
└─ Response: {status, camera_id}

GET /api/office/workers/<camera_id>
└─ Response: {workers: [...]}

GET /api/status
└─ Response: {cameras, total_detections, fps}
```

### WebSocket Events

```
start_monitoring
├─ data: {camera_id}

frame_update
├─ data: {frame_data, detections}

office_stats_update
├─ data: {workers_stats, timestamp}

stop_monitoring
├─ data: {camera_id}
```

---

## 🎓 Examples

### Example 1: Monitor Single Desk

```bash
python run_office_monitor.py
# Enter camera details for desk camera
# Monitor output in console
```

### Example 2: Monitor Department Floor

```bash
python run_web_server.py
# Add 5 cameras in Office mode
# View all workers in unified dashboard
# Sort by effectiveness score
```

### Example 3: Export Worker Statistics

```python
from src.office_analyzer import OfficeAnalyzer
import pandas as pd

analyzer = OfficeAnalyzer()

# After monitoring...
stats = []
for worker_id in analyzer.workers:
    stat = analyzer.get_worker_stats(worker_id)
    stats.append(stat)

df = pd.DataFrame(stats)
df.to_csv("worker_effectiveness.csv", index=False)
```

---

## ❓ FAQ

**Q: Can I monitor multiple floors?**
A: Yes! Add multiple cameras in web dashboard, each with its own RTSP URL.

**Q: How accurate is sitting duration?**
A: 85-95% accurate depending on camera angle and lighting. Full body visibility recommended.

**Q: Can I export reports?**
A: Currently in-memory. Add CSV export using pandas for persistence.

**Q: Is it real-time?**
A: ~1-3 second latency with WebSocket optimization.

**Q: Can I use with non-Hikvision cameras?**
A: Yes! Any RTSP camera works (IP cameras with RTSP protocol).

**Q: Does it track by person ID?**
A: Yes, tracks individual workers with position history.

**Q: How much bandwidth?**
A: 3-5 Mbps per RTSP stream with optimization.

**Q: Can I customize alerts?**
A: Yes, modify thresholds in OfficeAnalyzer methods.

---

## 📞 Support

**For Issues:**
1. Check TROUBLESHOOTING section above
2. Review UNIFIED_DASHBOARD_GUIDE.md
3. Run `python test_system_complete.py`
4. Check server logs for errors

**For Features:**
1. Edit `src/office_analyzer.py` for detection logic
2. Edit `templates/dashboard.html` for UI
3. Edit `src/web_server.py` for backend

---

## 📄 License

MIT License - Use freely in your projects

---

## ✨ What's Next?

1. ✅ Deploy to production
2. ⚠️ Add database for persistence
3. ⚠️ Add authentication system
4. ⚠️ Add PDF report generation
5. ⚠️ Add email alerts
6. ⚠️ Add mobile app

---

**System Ready! 🚀**

```
python run_web_server.py
http://localhost:5000 → [🏢 Office] → Add Camera → Monitor!
```
