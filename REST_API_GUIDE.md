# 🌐 REST API Integration - Complete Guide

## 📋 **Overview**

System **Human Detection** sekarang punya **REST API** yang bisa integrate dengan berbagai platform IoT:

| Platform | Integration Method | Use Case |
|----------|-------------------|----------|
| **Node-RED** | HTTP/SSE/Webhook | Automation, dashboards, alerts |
| **Milesight** | HTTP POST | IoT gateway, sensor data |
| **Home Assistant** | REST Sensor | Smart home automation |
| **Grafana** | HTTP API | Data visualization, monitoring |
| **MQTT Broker** | Via Node-RED | IoT messaging, pub/sub |
| **Telegram Bot** | Via Node-RED | Instant notifications |
| **Any HTTP Client** | REST API | Custom integrations |

---

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
cd /Users/HCMPublic/Kuliah/Project/hikvision_human_detection
source venv/bin/activate
pip install flask flask-cors requests
```

### **2. Start API Server**
```bash
# Option A: Bash script
./run_api_server.sh

# Option B: Python direct
python src/api_server.py
```

**Output:**
```
==========================================
  Human Detection REST API Server
==========================================

📦 Activating virtual environment...
✅ Environment ready

🚀 Starting API Server...
   URL: http://localhost:5000
   Documentation: http://localhost:5000/

📡 Integration endpoints:
   - Node-RED: http://localhost:5000/api/events
   - Milesight: Configure via /api/milesight/configure
   - Webhook: Configure via /api/webhook/configure

Press Ctrl+C to stop server
==========================================

INFO - Starting Human Detection API Server...
INFO - Loading model dari models/yolov8n.pt...
INFO - Model berhasil di-load
INFO - API Server running on http://0.0.0.0:5000
```

### **3. Test API**
```bash
# Browser - open documentation
open http://localhost:5000

# CLI - check status
curl http://localhost:5000/api/status

# Python test client
python test_api_client.py
```

---

## 📡 **API Endpoints Reference**

### **System Management**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/api/status` | GET | System status & info |
| `/api/config` | GET/POST | Get/update configuration |

### **Camera Management**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cameras` | GET | List all cameras |
| `/api/camera/add` | POST | Add new camera |
| `/api/camera/<id>` | DELETE | Remove camera |
| `/api/camera/<id>/detection` | GET | Get detection data (JSON) |
| `/api/camera/<id>/stream` | GET | MJPEG video stream |
| `/api/camera/<id>/snapshot` | GET | Single frame JPEG |

### **Integration**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/webhook/configure` | POST | Configure webhook (Node-RED) |
| `/api/milesight/configure` | POST | Configure Milesight gateway |
| `/api/events` | GET | Server-Sent Events stream |
| `/api/events/latest` | GET | Get last 10 events |

---

## 🔴 **Node-RED Integration**

### **Method 1: HTTP Polling**

**Flow:**
```
[Inject: every 5s] → [HTTP Request: GET /api/camera/front_door/detection]
                                              │
                                              ├→ [JSON Parse]
                                              │
                                              ├→ [Switch: human_count > 0]
                                              │         │
                                              │         ├→ [Telegram Alert]
                                              │         ├→ [Turn on Lights]
                                              │         └→ [Log to Database]
                                              │
                                              └→ [Dashboard Display]
```

**Example Node-RED code:**
```javascript
// HTTP Request node URL
http://localhost:5000/api/camera/front_door/detection

// Function node - Process detection
var count = msg.payload.human_count;
if (count > 0) {
    msg.payload = `🚨 Alert: ${count} orang terdeteksi!`;
    return msg;
}
return null;
```

### **Method 2: Server-Sent Events (Real-time)**

**Flow:**
```
[EventSource: /api/events] → [JSON Parse] → [Process Event]
                                                   │
                                                   ├→ Real-time alerts
                                                   ├→ Dashboard updates
                                                   └→ Database logging
```

**Example:**
```javascript
// EventSource node
const es = new EventSource('http://localhost:5000/api/events');

es.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // data = {
    //   camera_id: "front_door",
    //   human_count: 2,
    //   timestamp: "2025-11-04T10:30:15",
    //   detections: [...],
    //   fps: 25
    // }
    
    if (data.human_count > 0) {
        // Trigger action
        sendAlert(data);
    }
};
```

### **Method 3: Webhook (Push)**

**Step 1: Create Node-RED webhook endpoint**
```
[HTTP In: POST /webhook/human-detection] → [Function: Process]
                                                    │
                                                    ├→ [HTTP Response: 200 OK]
                                                    └→ [Your Actions]
```

**Step 2: Configure API to push**
```bash
curl -X POST http://localhost:5000/api/webhook/configure \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "url": "http://localhost:1880/webhook/human-detection"
  }'
```

**Step 3: Receive data automatically**
```javascript
// Function node in Node-RED
var count = msg.payload.human_count;
var camera = msg.payload.camera_id;

if (count > 0) {
    msg.payload = {
        alert: `${count} orang terdeteksi di ${camera}`,
        action: "turn_on_light",
        timestamp: msg.payload.timestamp
    };
    return msg;
}
return null;
```

### **Method 4: MJPEG Video Display**

**Node-RED Dashboard Template:**
```html
<div>
    <h3>Front Door Camera</h3>
    <img src="http://localhost:5000/api/camera/front_door/stream" 
         style="width:100%; height:auto; border:2px solid #333;">
</div>
```

---

## 🏭 **Milesight Integration**

### **1. Configure API**
```bash
curl -X POST http://localhost:5000/api/milesight/configure \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "url": "http://192.168.1.100:8080/api/data"
  }'
```

### **2. Data Format Sent to Milesight**
```json
{
  "deviceId": "camera_front_door",
  "timestamp": "2025-11-04T10:30:15.123456",
  "data": {
    "human_count": 2,
    "fps": 25
  },
  "type": "human_detection"
}
```

### **3. Milesight Gateway Setup**

1. Login to Milesight web interface
2. Add **HTTP Data Source**
3. Configure:
   - Name: `Human Detection API`
   - URL: `http://<API_IP>:5000/api/camera/<camera_id>/detection`
   - Method: `GET`
   - Interval: `5 seconds`
4. Create widget: Display `data.human_count`

---

## 📊 **Use Case Examples**

### **Use Case 1: Smart Security System**

**Scenario:** Alert security when person detected after hours (18:00-06:00)

**Node-RED Flow:**
```javascript
// Function node
var now = new Date();
var hour = now.getHours();
var count = msg.payload.human_count;
var camera = msg.payload.camera_id;

// Check after hours
if ((hour >= 18 || hour < 6) && count > 0) {
    msg.payload = {
        alert: "🚨 SECURITY ALERT",
        message: `${count} orang terdeteksi di ${camera}`,
        time: now.toLocaleString(),
        priority: "HIGH"
    };
    return msg;
}
return null;
```

**Actions:**
- Send Telegram message
- Turn on all lights
- Sound alarm
- Save snapshot to database
- Log event

---

### **Use Case 2: Smart Lighting**

**Scenario:** Auto turn on lights when person enters

**Node-RED Flow:**
```
[SSE Events] → [Function: Check Human] → [MQTT Publish]
                                               │
                                               └→ Topic: "home/lights/entrance"
                                                  Payload: "ON" or "OFF"
```

**Smart Light receives MQTT:**
```
Topic: home/lights/entrance
Payload: ON  → Light turns on
Payload: OFF → Light turns off
```

---

### **Use Case 3: Visitor Counter**

**Scenario:** Count total visitors per day

**Node-RED Flow:**
```
[Webhook] → [Function: Increment Counter] → [Context Store]
                                                   │
                                                   ├→ [Dashboard Chart]
                                                   └→ [InfluxDB Write]
```

**Function code:**
```javascript
// Get context counter
var counter = context.get('daily_visitors') || 0;

// Increment
counter += msg.payload.human_count;
context.set('daily_visitors', counter);

// Reset at midnight
var now = new Date();
if (now.getHours() === 0 && now.getMinutes() === 0) {
    context.set('daily_visitors', 0);
}

msg.payload = counter;
return msg;
```

---

### **Use Case 4: Access Control**

**Scenario:** Log all entry events with snapshot

**Node-RED Flow:**
```
[Webhook: Detection] → [HTTP: Get Snapshot] → [Base64 Encode]
                                                      │
                                                      ├→ [Database: Save]
                                                      └→ [Email: Send Report]
```

**Data logged:**
- Timestamp
- Camera ID
- Human count
- Snapshot image (base64)
- Duration

---

## 🔌 **Integration with Other Systems**

### **Home Assistant**

**configuration.yaml:**
```yaml
# REST Sensor
sensor:
  - platform: rest
    name: "Front Door Human Count"
    resource: http://localhost:5000/api/camera/front_door/detection
    value_template: "{{ value_json.human_count }}"
    unit_of_measurement: "people"
    scan_interval: 5

# Camera Stream
camera:
  - platform: mjpeg
    name: "Front Door"
    mjpeg_url: http://localhost:5000/api/camera/front_door/stream

# Automation
automation:
  - alias: "Person Detected Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.front_door_human_count
        above: 0
    action:
      - service: notify.telegram
        data:
          message: "Person detected at front door!"
      - service: light.turn_on
        entity_id: light.entrance
```

---

### **Grafana Dashboard**

**Data source:** InfluxDB (via Node-RED)

**Node-RED Flow:**
```
[Webhook] → [Function: Format] → [InfluxDB Write]
```

**Grafana Query:**
```sql
SELECT mean("human_count") 
FROM "detections" 
WHERE time > now() - 6h 
GROUP BY time(5m), "camera_id"
```

**Panels:**
- Line chart: Human count over time
- Bar chart: Total per camera
- Single stat: Current count
- Table: Recent events

---

### **Telegram Bot**

**Node-RED Flow:**
```
[Webhook: Detection] → [Function: Format Message] → [Telegram Sender]
                              │
                              └→ [HTTP: Get Snapshot] → [Telegram Photo]
```

**Message format:**
```
🚨 ALERT: Person Detected

📹 Camera: Front Door
👤 Count: 2 orang
🕐 Time: 2025-11-04 10:30:15
📊 FPS: 25

[Attached: Snapshot image]
```

---

## 🛠️ **Development Tools**

### **1. Python Test Client**
```bash
python test_api_client.py
```

**Features:**
- Test all API endpoints
- Add/remove cameras
- Poll detection data
- Get snapshots
- Configure webhooks
- Interactive menu

### **2. curl Examples**
```bash
# Status
curl http://localhost:5000/api/status

# Add camera
curl -X POST http://localhost:5000/api/camera/add \
  -H "Content-Type: application/json" \
  -d '{"camera_id":"test","rtsp_url":"rtsp://..."}'

# Get detection
curl http://localhost:5000/api/camera/test/detection

# Get snapshot
curl http://localhost:5000/api/camera/test/snapshot -o snapshot.jpg

# List cameras
curl http://localhost:5000/api/cameras
```

### **3. Node-RED Import**
```bash
# Import example flows
cat nodered_flows_examples.json
# Copy content → Node-RED → Import → Paste
```

---

## 📚 **Documentation Files**

| File | Description |
|------|-------------|
| `NODE_RED_INTEGRATION.md` | Detailed Node-RED guide |
| `API_ARCHITECTURE.md` | System architecture diagram |
| `nodered_flows_examples.json` | Ready-to-use flows |
| `test_api_client.py` | Python test client |
| `run_api_server.sh` | Server launcher script |
| `src/api_server.py` | API server implementation |

---

## ✅ **Summary**

**REST API Features:**
- ✅ Multi-camera management
- ✅ Real-time detection data (JSON)
- ✅ MJPEG video streaming
- ✅ Server-Sent Events (SSE)
- ✅ Webhook notifications
- ✅ Node-RED integration (3 methods)
- ✅ Milesight IoT gateway
- ✅ Home Assistant compatible
- ✅ CORS enabled untuk web access
- ✅ Production ready

**Integration Methods:**
1. **HTTP Polling** - Simple, reliable (5s interval)
2. **Server-Sent Events** - Real-time, efficient
3. **Webhook** - Push notifications, event-driven
4. **MJPEG Stream** - Live video display

**Supported Platforms:**
- Node-RED ✅
- Milesight ✅
- Home Assistant ✅
- Grafana ✅
- Telegram Bot ✅
- MQTT Bridge ✅
- Any HTTP client ✅

**Ready untuk production IoT ecosystem! 🚀**

---

## 🎯 **Next Steps**

1. **Start API server:** `./run_api_server.sh`
2. **Test API:** `python test_api_client.py`
3. **Setup Node-RED:** Import flows dari `nodered_flows_examples.json`
4. **Configure integrations:** Webhook/Milesight via API
5. **Build your automation!** 🎉
