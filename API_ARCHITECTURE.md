# REST API Architecture

## 🌐 **System Architecture dengan REST API**

```
┌──────────────────────────────────────────────────────────────────────┐
│                        IoT ECOSYSTEM                                 │
│                                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  Node-RED  │  │ Milesight  │  │   Home     │  │  Grafana   │   │
│  │ Dashboard  │  │  Gateway   │  │ Assistant  │  │  Dashboard │   │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘   │
│         │                │                │                │         │
│         │  HTTP/SSE      │  HTTP          │  HTTP          │  HTTP  │
│         │                │                │                │         │
└─────────┼────────────────┼────────────────┼────────────────┼─────────┘
          │                │                │                │
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                     │
                                     │
                        ┌────────────▼─────────────┐
                        │   REST API SERVER        │
                        │   (Flask - Port 5000)    │
                        │                          │
                        │  Endpoints:              │
                        │  - /api/status           │
                        │  - /api/cameras          │
                        │  - /api/camera/add       │
                        │  - /api/camera/<id>/...  │
                        │  - /api/events (SSE)     │
                        │  - /api/webhook/...      │
                        │  - /api/milesight/...    │
                        └────────────┬─────────────┘
                                     │
                                     │ Manage
                                     │
                   ┌─────────────────┼─────────────────┐
                   │                 │                 │
                   │                 │                 │
          ┌────────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
          │  Camera Stream  │ │   Camera   │ │  Camera Stream │
          │   Thread #1     │ │  Stream    │ │   Thread #3    │
          │                 │ │  Thread #2 │ │                │
          │  Front Door     │ │            │ │  Parking Lot   │
          │  Camera         │ │  Back Door │ │  Camera        │
          └────────┬────────┘ └─────┬──────┘ └───────┬────────┘
                   │                │                 │
                   │                │                 │
                   └────────────────┼─────────────────┘
                                    │
                                    │ Shared
                                    │
                        ┌───────────▼──────────┐
                        │   YOLOv8 Detector    │
                        │   (Person Only)      │
                        │                      │
                        │   - Load once        │
                        │   - Shared by all    │
                        │   - GPU accelerated  │
                        └──────────────────────┘
                                    │
                                    │ Read frames
                                    │
                   ┌────────────────┼─────────────────┐
                   │                │                 │
          ┌────────▼────────┐ ┌────▼───────┐ ┌──────▼─────────┐
          │  Hikvision      │ │ Hikvision  │ │  Hikvision     │
          │  Camera #1      │ │ Camera #2  │ │  Camera #3     │
          │  192.168.1.64   │ │.168.1.65   │ │  192.168.1.66  │
          │                 │ │            │ │                │
          │  RTSP Stream    │ │ RTSP Stream│ │  RTSP Stream   │
          └─────────────────┘ └────────────┘ └────────────────┘
```

---

## 📡 **Data Flow**

### **1. Camera → API Server**
```
Hikvision Camera (RTSP) → Camera Stream Thread → YOLOv8 Detector
                                                       │
                                                       ├→ Annotated Frame (MJPEG)
                                                       ├→ Detection Data (JSON)
                                                       └→ Events (SSE)
```

### **2. API Server → External Systems**

**A. Polling (Client pulls data)**
```
Node-RED/Client → HTTP GET /api/camera/<id>/detection → JSON Response
```

**B. Server-Sent Events (Server pushes)**
```
API Server → SSE Stream /api/events → Node-RED EventSource → Real-time Data
```

**C. Webhook (Server pushes to endpoint)**
```
Detection Event → API Server → HTTP POST → Node-RED Webhook → Action
```

---

## 🔄 **API Request/Response Examples**

### **1. Add Camera**
```
POST /api/camera/add

Request:
{
  "camera_id": "front_door",
  "rtsp_url": "rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/102"
}

Response (201):
{
  "message": "Camera added successfully",
  "camera_id": "front_door"
}
```

### **2. Get Detection Data**
```
GET /api/camera/front_door/detection

Response (200):
{
  "camera_id": "front_door",
  "timestamp": "2025-11-04T10:30:15",
  "human_count": 2,
  "detections": [
    {
      "bbox": [100, 150, 300, 450],
      "confidence": 0.89,
      "class": "person"
    }
  ],
  "fps": 25
}
```

### **3. Video Stream (MJPEG)**
```
GET /api/camera/front_door/stream

Response:
multipart/x-mixed-replace; boundary=frame

(Continuous JPEG frames untuk display di browser/dashboard)
```

### **4. Real-time Events (SSE)**
```
GET /api/events

Response:
text/event-stream

data: {"camera_id":"front_door","human_count":2,"timestamp":"..."}

data: {"camera_id":"back_door","human_count":1,"timestamp":"..."}

(Continuous event stream)
```

---

## 🔌 **Integration Methods**

### **Method 1: HTTP Polling**
**Use case:** Simple periodic checks

```javascript
// Node-RED: Inject node (every 5s) → HTTP Request node
setInterval(() => {
  fetch('http://localhost:5000/api/camera/front_door/detection')
    .then(res => res.json())
    .then(data => {
      if (data.human_count > 0) {
        console.log(`Alert: ${data.human_count} people detected!`);
      }
    });
}, 5000);
```

**Pros:** Simple, reliable  
**Cons:** Network overhead, not real-time

---

### **Method 2: Server-Sent Events (SSE)**
**Use case:** Real-time notifications

```javascript
// Node-RED: EventSource node
const es = new EventSource('http://localhost:5000/api/events');
es.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Real-time: ${data.human_count} people at ${data.camera_id}`);
};
```

**Pros:** Real-time, one connection  
**Cons:** Client must maintain connection

---

### **Method 3: Webhook (Push)**
**Use case:** Event-driven actions

```bash
# Configure API to push to Node-RED
curl -X POST http://localhost:5000/api/webhook/configure \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"url":"http://localhost:1880/webhook/human-detection"}'

# Node-RED receives POST requests automatically
```

**Pros:** No polling needed, efficient  
**Cons:** Requires Node-RED webhook endpoint

---

### **Method 4: MJPEG Stream**
**Use case:** Live video display

```html
<!-- Display in web browser -->
<img src="http://localhost:5000/api/camera/front_door/stream" />

<!-- Node-RED Dashboard: Template node -->
<img src="http://localhost:5000/api/camera/front_door/stream" 
     style="width:100%; height:auto;">
```

**Pros:** Visual monitoring  
**Cons:** Higher bandwidth

---

## 🏭 **Node-RED Integration Examples**

### **Example 1: Alert System**
```
[Inject: 5s] → [HTTP Request: Get Detection] → [Switch: human_count > 0]
                                                         │
                                                         ├→ [Telegram: Send Alert]
                                                         ├→ [Email: Send Email]
                                                         └→ [MQTT: Publish Event]
```

### **Example 2: Smart Lighting**
```
[SSE: Events] → [Function: Check Count] → [Switch: count > 0]
                                                     │
                                                     ├→ Yes → [MQTT: lights/entrance ON]
                                                     └→ No  → [MQTT: lights/entrance OFF]
```

### **Example 3: Data Logging**
```
[Webhook: /human-detection] → [Function: Format] → [InfluxDB: Write Point]
                                                            │
                                                            └→ [Grafana Dashboard]
```

---

## 📊 **Milesight Integration**

### **Architecture:**
```
Detection API → Format Data → HTTP POST → Milesight Gateway → Cloud
```

### **Configuration:**
```bash
curl -X POST http://localhost:5000/api/milesight/configure \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "url": "http://192.168.1.100:8080/api/data"
  }'
```

### **Data Format Sent:**
```json
{
  "deviceId": "camera_front_door",
  "timestamp": "2025-11-04T10:30:15",
  "data": {
    "human_count": 2,
    "fps": 25
  },
  "type": "human_detection"
}
```

---

## 🔧 **API Configuration**

### **Environment Variables:**
```bash
# API Server
API_HOST=0.0.0.0
API_PORT=5000

# Model
MODEL_PATH=models/yolov8n.pt
CONF_THRESHOLD=0.5

# Webhook
WEBHOOK_ENABLED=false
WEBHOOK_URL=http://localhost:1880/webhook/human-detection

# Milesight
MILESIGHT_ENABLED=false
MILESIGHT_URL=http://192.168.1.100:8080/api/data
```

### **Runtime Configuration (via API):**
```bash
# Get current config
curl http://localhost:5000/api/config

# Update config
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"conf_threshold": 0.6, "detection_interval": 2.0}'
```

---

## 🚀 **Quick Start**

### **1. Start API Server**
```bash
./run_api_server.sh
```

### **2. Test API**
```bash
# Browser
open http://localhost:5000

# CLI test client
python test_api_client.py
```

### **3. Add Camera**
```bash
curl -X POST http://localhost:5000/api/camera/add \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "front_door",
    "rtsp_url": "rtsp://admin:Admin123@192.168.1.64:554/Streaming/Channels/102"
  }'
```

### **4. View Video Stream**
```bash
open http://localhost:5000/api/camera/front_door/stream
```

---

## 📝 **Summary**

**REST API provides:**
- ✅ HTTP/REST endpoints untuk camera management
- ✅ Real-time detection data (JSON)
- ✅ MJPEG video streaming
- ✅ Server-Sent Events (SSE) untuk real-time updates
- ✅ Webhook support untuk push notifications
- ✅ Node-RED integration (polling/SSE/webhook)
- ✅ Milesight IoT gateway integration
- ✅ Multi-camera support
- ✅ Easy to integrate dengan any HTTP client

**Ready untuk IoT ecosystem! 🌐**
