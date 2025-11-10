# 🌐 Hikvision Detection Web Dashboard

Professional real-time monitoring interface untuk sistem deteksi manusia Hikvision.

## ✨ Features

### 📊 Dashboard
- **Real-time Monitoring**: Live video stream dari multiple kamera
- **Live Statistics**: FPS, frame count, detection count
- **Alert System**: Real-time alerts untuk violation
- **Responsive Design**: Desktop, tablet, mobile friendly

### 🎥 Multi-Camera Support
- Add/remove kamera dinamis
- Multiple stream bersamaan
- Independent monitoring per camera
- Per-camera statistics

### 🔍 Detection Modes
- **Simple Mode**: Person detection only
- **Advanced Mode**: Helmet, weapon, smoke, crowd detection

### 📌 Embed-Ready
- HTML5 embed code untuk integration ke website lain
- Iframe support
- CORS enabled untuk cross-origin access

### 🚨 Alert System
- Helmet violation alert
- Weapon detection alert
- Crowd detection alert
- Real-time notification
- Alert timestamp dan history

---

## 🚀 Quick Start

### 1. Start Web Server
```bash
cd hikvision_human_detection
source venv/bin/activate
python run_web_server.py
```

Server akan start di: **http://localhost:5000**

### 2. Access Dashboard
Buka browser dan buka: `http://localhost:5000`

### 3. Add Camera
1. Isi Camera ID (e.g., "cam-1")
2. Masukkan RTSP URL dari kamera Hikvision
3. Pilih detection mode (simple atau advanced)
4. Klik "Add Camera"

Contoh RTSP URL:
```
rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102
```

### 4. Monitoring
- Video stream akan tampil otomatis setelah camera terhubung
- Lihat real-time statistics
- Alert akan tampil di section "Active Alerts"

---

## 🔌 API Reference

### REST Endpoints

#### Get Status
```
GET /api/status
```
Response:
```json
{
  "running": true,
  "cameras": {
    "cam-1": {
      "connected": true,
      "frame_count": 1234,
      "detection_count": 45,
      "fps": 28.5,
      "mode": "simple"
    }
  },
  "stats": {
    "total_frames": 2000,
    "total_detections": 100,
    "average_fps": 27.0,
    "active_alerts": []
  }
}
```

#### Add Camera
```
POST /api/camera/add
Content-Type: application/json

{
  "camera_id": "cam-1",
  "rtsp_url": "rtsp://admin:password@10.0.66.29:554/Streaming/Channels/102",
  "mode": "simple"  // atau "advanced"
}
```

#### Connect Camera
```
POST /api/camera/connect/{camera_id}
```

#### Disconnect Camera
```
POST /api/camera/disconnect/{camera_id}
```

---

## 🔌 WebSocket Events

### Client → Server

#### start_monitoring
```javascript
socket.emit('start_monitoring', {
  camera_id: 'cam-1'
});
```

#### stop_monitoring
```javascript
socket.emit('stop_monitoring', {
  camera_id: 'cam-1'
});
```

### Server → Client

#### frame_update
```javascript
socket.on('frame_update', (data) => {
  console.log(data);
  // {
  //   camera_id: 'cam-1',
  //   frame: 'data:image/jpeg;base64,...',
  //   human_count: 2,
  //   fps: 28.5,
  //   violations: {
  //     no_helmet: 1,
  //     no_jacket: 0
  //   },
  //   weapon_alert: false,
  //   crowd_info: {
  //     person_count: 2,
  //     crowd_detected: false,
  //     intrusion_risk: false
  //   },
  //   timestamp: '2025-11-10T10:30:45.123Z'
  // }
});
```

#### monitoring_started / monitoring_stopped
```javascript
socket.on('monitoring_started', (data) => {
  console.log('Monitoring started for:', data.camera_id);
});

socket.on('monitoring_stopped', (data) => {
  console.log('Monitoring stopped for:', data.camera_id);
});
```

---

## 📌 Embedding ke Website Lain

### Method 1: Iframe
```html
<iframe 
  src="http://your-server:5000?camera_id=cam-1" 
  width="100%" 
  height="600" 
  frameborder="0"
  allow="autoplay">
</iframe>
```

### Method 2: Direct Integration
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
  <div id="stream-container"></div>

  <script>
    const socket = io('http://your-server:5000');
    
    socket.on('connect', () => {
      socket.emit('start_monitoring', { camera_id: 'cam-1' });
    });
    
    socket.on('frame_update', (data) => {
      const img = document.getElementById('stream-img') || document.createElement('img');
      img.id = 'stream-img';
      img.src = data.frame;
      img.style.maxWidth = '100%';
      document.getElementById('stream-container').appendChild(img);
    });
  </script>
</body>
</html>
```

### Method 3: Stream URL
Dapatkan stream URL:
```
http://your-server:5000/stream/{camera_id}
```

---

## 🎨 UI Components

### Camera Card
- Live video stream
- Real-time statistics
- Status indicator
- Detection mode badge

### Alert Section
- Color-coded alerts (helmet, weapon, crowd)
- Timestamp untuk setiap alert
- Auto-hiding jika tidak ada alert
- Alert history

### Control Panel
- Camera ID input
- RTSP URL input
- Detection mode selector
- Add camera button

### Stats Bar
- Human count
- FPS display
- Frame counter
- Current time

---

## ⚙️ Configuration

### Environment Variables
```bash
# Server settings
export FLASK_ENV=production
export FLASK_DEBUG=False
export SERVER_PORT=5000
export SERVER_HOST=0.0.0.0

# Detection settings
export CONFIDENCE_THRESHOLD=0.45
export MIN_CROWD_SIZE=5
export MAX_STREAMING_FPS=30
```

### Advanced Settings (di src/web_server.py)
```python
# Frame size untuk bandwidth efficiency
frame_size = (640, 360)  # Default

# JPEG quality (1-100)
jpeg_quality = 80  # Default

# Streaming FPS
stream_fps = 30  # Default

# Buffer size
buffer_size = 1  # Default (real-time)
```

---

## 🔒 Security

### Access Control
1. **Development**: Accessible tanpa authentication
2. **Production**: Tambahkan authentication:

```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'admin' and password == 'secret'

@app.route('/api/status')
@auth.login_required
def get_status():
    # Protected endpoint
    pass
```

### HTTPS
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with HTTPS
socketio.run(app, host='0.0.0.0', port=5000, 
             certfile='cert.pem', keyfile='key.pem')
```

---

## 📊 Performance Tips

### Optimize untuk Low Bandwidth
```python
# Reduce frame size
frame_size = (320, 180)  # HD Ready

# Reduce JPEG quality
jpeg_quality = 60  # More compression

# Reduce FPS
max_fps = 15  # Lower FPS
```

### Optimize untuk High Performance
```python
# Higher resolution
frame_size = (1280, 720)  # HD

# Higher quality
jpeg_quality = 95  # Better quality

# Higher FPS
max_fps = 30  # Smooth video
```

---

## 🐛 Troubleshooting

### Camera tidak terkoneksi
- Cek RTSP URL format
- Cek network connectivity ke kamera
- Cek firewall settings

### Stream lambat/delay
- Reduce frame resolution
- Reduce JPEG quality
- Disable advanced detection
- Check network bandwidth

### High CPU usage
- Reduce frame resolution
- Use simple detection mode
- Reduce number of cameras
- Check system resources

### WebSocket connection error
- Check firewall untuk port 5000
- Check CORS settings
- Restart server

---

## 📚 Integration Examples

### Dengan NMS atau VMS
```python
# Export events ke NMS
def send_alert_to_nms(alert):
    requests.post('http://nms-server:8080/api/alerts', 
                  json=alert)
```

### Dengan Mobile App
```javascript
// React Native
import io from 'socket.io-client';

const socket = io('http://your-server:5000');

socket.on('frame_update', (data) => {
  setStreamImage(data.frame);
});
```

### Dengan Database (PostgreSQL)
```python
# Store alerts dan detections
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost/hikvision')

def save_detection(camera_id, detection):
    # Insert ke database
    pass
```

---

## 📝 Logs

### Log Location
```
outputs/logs/web_server.log
```

### View Logs Real-time
```bash
tail -f outputs/logs/web_server.log
```

---

## 🚀 Deployment

### Local Development
```bash
python run_web_server.py
```

### Docker
```dockerfile
FROM python:3.9

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "run_web_server.py"]
```

```bash
# Build
docker build -t hikvision-detection .

# Run
docker run -p 5000:5000 hikvision-detection
```

### Production (Gunicorn)
```bash
pip install gunicorn

gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 src.web_server:app
```

---

## 📞 Support

Untuk pertanyaan atau issues:
1. Check logs di `outputs/logs/web_server.log`
2. Check browser console untuk JavaScript errors
3. Test API endpoints dengan curl/Postman

---

**Version**: 1.0  
**Last Updated**: 2025-11-10  
**Status**: ✅ Production Ready
