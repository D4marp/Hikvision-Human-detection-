# Node-RED & Milesight Integration Guide

## 🌐 **REST API untuk IoT Integration**

System ini sekarang punya **REST API** yang bisa integrate dengan:
- ✅ **Node-RED** - Low-code automation platform
- ✅ **Milesight** - IoT gateway & sensors
- ✅ **Home Assistant** - Smart home platform
- ✅ **Grafana** - Data visualization
- ✅ **MQTT Broker** - IoT messaging
- ✅ **Any HTTP client**

---

## 🚀 **Quick Start API Server**

### **1. Install Dependencies**
```bash
pip install flask flask-cors requests
```

### **2. Start API Server**
```bash
cd /Users/HCMPublic/Kuliah/Project/hikvision_human_detection
source venv/bin/activate
python src/api_server.py
```

**Output:**
```
INFO - Starting Human Detection API Server...
INFO - Loading model dari models/yolov8n.pt...
INFO - Model berhasil di-load
INFO - API Server running on http://0.0.0.0:5000
INFO - Access documentation: http://localhost:5000/
```

### **3. Test API**
```bash
# Browser
open http://localhost:5000

# curl
curl http://localhost:5000/api/status
```

---

## 📡 **API Endpoints**

### **1. System Status**
```bash
GET http://localhost:5000/api/status
```

**Response:**
```json
{
  "status": "running",
  "timestamp": "2025-11-04T10:30:00",
  "cameras": 2,
  "active_cameras": 2,
  "model": "models/yolov8n.pt",
  "confidence_threshold": 0.5,
  "webhook_enabled": true,
  "milesight_enabled": false
}
```

### **2. Add Camera**
```bash
POST http://localhost:5000/api/camera/add
Content-Type: application/json

{
  "camera_id": "front_door",
  "rtsp_url": "rtsp://admin:Admin123@192.168.1.64:554/Streaming/Channels/102"
}
```

**Response:**
```json
{
  "message": "Camera added successfully",
  "camera_id": "front_door"
}
```

### **3. Get Detection Data**
```bash
GET http://localhost:5000/api/camera/front_door/detection
```

**Response:**
```json
{
  "camera_id": "front_door",
  "timestamp": "2025-11-04T10:30:15",
  "human_count": 2,
  "detections": [
    {
      "bbox": [100, 150, 300, 450],
      "confidence": 0.89,
      "class": "person"
    },
    {
      "bbox": [400, 180, 550, 480],
      "confidence": 0.92,
      "class": "person"
    }
  ],
  "fps": 25
}
```

### **4. Video Stream (MJPEG)**
```bash
GET http://localhost:5000/api/camera/front_door/stream
```
Returns MJPEG stream (bisa display di browser atau Node-RED dashboard)

### **5. Snapshot (Single Frame)**
```bash
GET http://localhost:5000/api/camera/front_door/snapshot
```
Returns JPEG image

### **6. Real-time Events (SSE)**
```bash
GET http://localhost:5000/api/events
```
Server-Sent Events stream untuk real-time notifications

---

## 🔴 **Node-RED Integration**

### **Architecture:**
```
┌─────────────────┐      HTTP/SSE      ┌─────────────────┐
│  Human Detection│ ──────────────────> │    Node-RED     │
│   API Server    │                     │   (localhost:   │
│  (port 5000)    │ <────────────────── │     1880)       │
└─────────────────┘      Webhook        └────────┬────────┘
                                                  │
                                                  │ MQTT/HTTP
                                                  │
                                    ┌─────────────▼──────────────┐
                                    │   External Systems:        │
                                    │   - Milesight Gateway      │
                                    │   - Smart Lights           │
                                    │   - Telegram Bot           │
                                    │   - Email Alerts           │
                                    │   - Database (InfluxDB)    │
                                    └────────────────────────────┘
```

### **Method 1: HTTP Request Node**

**Node-RED Flow:**
```javascript
[
  {
    "id": "inject1",
    "type": "inject",
    "name": "Poll Every 5s",
    "props": [{"p": "payload"}],
    "repeat": "5",  // Poll every 5 seconds
    "topic": "",
    "payload": "",
    "payloadType": "date",
    "x": 150,
    "y": 100
  },
  {
    "id": "http1",
    "type": "http request",
    "name": "Get Detection Data",
    "method": "GET",
    "url": "http://localhost:5000/api/camera/front_door/detection",
    "x": 350,
    "y": 100
  },
  {
    "id": "json1",
    "type": "json",
    "name": "Parse JSON",
    "x": 550,
    "y": 100
  },
  {
    "id": "switch1",
    "type": "switch",
    "name": "Check Human Count",
    "property": "payload.human_count",
    "rules": [
      {"t": "gt", "v": "0"}  // Greater than 0
    ],
    "x": 750,
    "y": 100
  },
  {
    "id": "debug1",
    "type": "debug",
    "name": "Alert: Human Detected!",
    "x": 950,
    "y": 100
  }
]
```

**Import to Node-RED:**
1. Copy flow JSON above
2. Node-RED → Menu → Import → Paste
3. Deploy

### **Method 2: Server-Sent Events (Real-time)**

**Node-RED Flow:**
```javascript
[
  {
    "id": "sse1",
    "type": "eventsource",
    "name": "Detection Events Stream",
    "url": "http://localhost:5000/api/events",
    "x": 150,
    "y": 200
  },
  {
    "id": "json2",
    "type": "json",
    "name": "Parse Event",
    "x": 350,
    "y": 200
  },
  {
    "id": "function1",
    "type": "function",
    "name": "Format Message",
    "func": "msg.payload = `${msg.payload.human_count} orang terdeteksi di ${msg.payload.camera_id}`;\\nreturn msg;",
    "x": 550,
    "y": 200
  },
  {
    "id": "telegram1",
    "type": "telegram sender",
    "name": "Send to Telegram",
    "x": 750,
    "y": 200
  }
]
```

### **Method 3: Webhook (Push dari API)**

**1. Configure Node-RED Webhook Endpoint:**

Create flow dengan `http in` node:
```javascript
[
  {
    "id": "httpin1",
    "type": "http in",
    "name": "Webhook Listener",
    "url": "/webhook/human-detection",
    "method": "post",
    "x": 150,
    "y": 300
  },
  {
    "id": "function2",
    "type": "function",
    "name": "Process Detection",
    "func": "// msg.payload contains detection data\\nvar count = msg.payload.human_count;\\nvar camera = msg.payload.camera_id;\\n\\nif (count > 0) {\\n    msg.payload = `Alert: ${count} orang di ${camera}`;\\n    return msg;\\n}\\nreturn null;",
    "x": 350,
    "y": 300
  },
  {
    "id": "httpresponse1",
    "type": "http response",
    "name": "Send OK",
    "statusCode": "200",
    "x": 550,
    "y": 300
  }
]
```

**2. Configure API to send webhook:**
```bash
curl -X POST http://localhost:5000/api/webhook/configure \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "url": "http://localhost:1880/webhook/human-detection"
  }'
```

---

## 🏭 **Milesight IoT Gateway Integration**

### **Architecture:**
```
Hikvision Camera → Detection API → Milesight Gateway → Cloud/Dashboard
```

### **1. Configure Milesight URL**
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
  "timestamp": "2025-11-04T10:30:15",
  "data": {
    "human_count": 2,
    "fps": 25
  },
  "type": "human_detection"
}
```

### **3. Milesight Dashboard Setup**

1. Login to Milesight Gateway web interface
2. Add "HTTP Data Source"
3. Configure endpoint: `http://<API_SERVER_IP>:5000/api/camera/<camera_id>/detection`
4. Set polling interval: 5 seconds
5. Create widget to display `human_count`

---

## 📊 **Example Use Cases**

### **Use Case 1: Smart Lighting**

**Scenario:** Turn on lights when person detected

**Node-RED Flow:**
```
Detection API → Check human_count > 0 → Send MQTT → Smart Light ON
```

**Implementation:**
```javascript
// Function node code
if (msg.payload.human_count > 0) {
    return {
        payload: "ON",
        topic: "home/entrance/light"
    };
}
return null;
```

### **Use Case 2: Access Control**

**Scenario:** Log entry events to database

**Node-RED Flow:**
```
Detection Events → Format Data → InfluxDB Write → Grafana Display
```

**Data saved:**
- Timestamp
- Camera ID
- Human count
- Duration
- Snapshot (base64)

### **Use Case 3: Security Alert**

**Scenario:** Send Telegram alert when person detected after hours

**Node-RED Flow:**
```javascript
// Function node
var now = new Date();
var hour = now.getHours();

// After hours (18:00 - 06:00)
if ((hour >= 18 || hour < 6) && msg.payload.human_count > 0) {
    msg.payload = `🚨 ALERT: ${msg.payload.human_count} orang terdeteksi di ${msg.payload.camera_id} pada ${now.toLocaleString()}`;
    return msg;
}
return null;
```

### **Use Case 4: People Counting**

**Scenario:** Count total people throughout the day

**Node-RED Flow:**
```
Detection Events → Aggregate Count → Context Store → Dashboard Chart
```

---

## 🔧 **Advanced Integration**

### **1. MQTT Bridge**

Publish detection data ke MQTT broker:

**Node-RED Flow:**
```javascript
// HTTP Request node → Get detection
// Function node:
msg.topic = `camera/${msg.payload.camera_id}/human_count`;
msg.payload = msg.payload.human_count;
return msg;

// MQTT Out node → Publish to broker
```

**Subscribe in other systems:**
```bash
mosquitto_sub -h localhost -t "camera/+/human_count"
```

### **2. Home Assistant Integration**

**configuration.yaml:**
```yaml
sensor:
  - platform: rest
    name: "Front Door Human Count"
    resource: http://localhost:5000/api/camera/front_door/detection
    value_template: "{{ value_json.human_count }}"
    unit_of_measurement: "people"
    scan_interval: 5

camera:
  - platform: mjpeg
    name: "Front Door Camera"
    mjpeg_url: http://localhost:5000/api/camera/front_door/stream
```

**Automation:**
```yaml
automation:
  - alias: "Alert on Person Detection"
    trigger:
      - platform: numeric_state
        entity_id: sensor.front_door_human_count
        above: 0
    action:
      - service: notify.telegram
        data:
          message: "Person detected at front door!"
```

### **3. Grafana Dashboard**

**InfluxDB Integration:**

Node-RED flow:
```
Detection Events → Format for InfluxDB → Write Point
```

**Grafana Query:**
```sql
SELECT mean("human_count") 
FROM "detections" 
WHERE time > now() - 1h 
GROUP BY time(1m), "camera_id"
```

---

## 🌐 **Full API Reference**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/api/status` | GET | System status |
| `/api/cameras` | GET | List cameras |
| `/api/camera/add` | POST | Add camera |
| `/api/camera/<id>` | DELETE | Remove camera |
| `/api/camera/<id>/stream` | GET | MJPEG stream |
| `/api/camera/<id>/detection` | GET | Detection data |
| `/api/camera/<id>/snapshot` | GET | JPEG snapshot |
| `/api/webhook/configure` | POST | Configure webhook |
| `/api/milesight/configure` | POST | Configure Milesight |
| `/api/events` | GET | SSE stream |
| `/api/events/latest` | GET | Last 10 events |
| `/api/config` | GET/POST | Configuration |

---

## 📝 **Example Scripts**

### **Python Client:**
```python
import requests
import time

API_URL = "http://localhost:5000"

# Add camera
requests.post(f"{API_URL}/api/camera/add", json={
    "camera_id": "front_door",
    "rtsp_url": "rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/102"
})

# Poll detection data
while True:
    response = requests.get(f"{API_URL}/api/camera/front_door/detection")
    data = response.json()
    
    if data['human_count'] > 0:
        print(f"🚨 {data['human_count']} orang terdeteksi!")
    
    time.sleep(2)
```

### **JavaScript/Node.js:**
```javascript
const axios = require('axios');

const API_URL = 'http://localhost:5000';

// Add camera
await axios.post(`${API_URL}/api/camera/add`, {
  camera_id: 'front_door',
  rtsp_url: 'rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/102'
});

// Real-time events (SSE)
const EventSource = require('eventsource');
const es = new EventSource(`${API_URL}/api/events`);

es.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`${data.human_count} orang di ${data.camera_id}`);
};
```

---

## 🔒 **Security Notes**

1. **API Authentication:** Add API key/JWT for production
2. **HTTPS:** Use reverse proxy (nginx) with SSL
3. **Firewall:** Only expose API to trusted networks
4. **Rate Limiting:** Add rate limiting for public APIs
5. **CORS:** Configure CORS properly for web access

---

## ✅ **Summary**

**REST API ini support:**
- ✅ Multiple cameras via HTTP
- ✅ Real-time detection events (SSE)
- ✅ MJPEG video streaming
- ✅ Webhook notifications (push)
- ✅ Node-RED integration (http/sse/webhook)
- ✅ Milesight IoT gateway
- ✅ Home Assistant
- ✅ MQTT bridge via Node-RED
- ✅ Grafana dashboards
- ✅ Telegram/Email alerts

**Ready untuk IoT ecosystem! 🚀**
