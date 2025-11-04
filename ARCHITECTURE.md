# Arsitektur System Human Detection

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN DETECTION SYSTEM                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐                           ┌────────────────────┐
│                  │    RTSP Stream (H.264)    │                    │
│   HIKVISION      │◄──────────────────────────│   NETWORK          │
│   DS-2CD2120F-I  │        Port 554           │   (Router/Switch)  │
│                  │                           │                    │
│  ┌────────────┐  │                           └──────────┬─────────┘
│  │ Image      │  │                                      │
│  │ Sensor     │  │                                      │ Ethernet
│  └────────────┘  │                                      │
│        │         │                                      │
│  ┌─────▼──────┐  │                           ┌──────────▼─────────┐
│  │ H.264      │  │                           │                    │
│  │ Encoder    │  │                           │  JETSON NANO/      │
│  └────────────┘  │                           │  XAVIER/ORIN       │
│        │         │                           │                    │
│  ┌─────▼──────┐  │                           │  ┌──────────────┐  │
│  │ RTSP       │  │                           │  │ RTSP Client  │  │
│  │ Server     │  │                           │  │ (OpenCV)     │  │
│  └────────────┘  │                           │  └──────┬───────┘  │
└──────────────────┘                           │         │          │
                                               │  ┌──────▼───────┐  │
    Camera hanya:                              │  │ Video Decode │  │
    ✅ Capture video                           │  │ (NVDEC)      │  │
    ✅ Encode H.264                            │  └──────┬───────┘  │
    ✅ Stream via RTSP                         │         │          │
    ❌ NO AI Processing                        │  ┌──────▼───────┐  │
                                               │  │ YOLOv8       │  │
                                               │  │ AI Model     │  │
                                               │  │ (GPU CUDA)   │  │
                                               │  └──────┬───────┘  │
                                               │         │          │
                                               │  ┌──────▼───────┐  │
                                               │  │ Detection    │  │
                                               │  │ Results      │  │
                                               │  └──────┬───────┘  │
                                               │         │          │
                                               │  ┌──────▼───────┐  │
                                               │  │ Save/Display │  │
                                               │  └──────────────┘  │
                                               └────────────────────┘
                                                    
                                                   Processing semua di sini:
                                                   ✅ Receive RTSP
                                                   ✅ Decode video
                                                   ✅ YOLOv8 inference
                                                   ✅ Detection
                                                   ✅ Save results
```

---

## 🔄 Data Flow

```
Step 1: CAPTURE
┌────────────┐
│ Hikvision  │  → Sensor capture RAW video
│ Camera     │  → Encode to H.264
└──────┬─────┘  → Stream via RTSP
       │
       │ RTSP Protocol
       │ (Real-Time Streaming)
       ▼
Step 2: NETWORK
┌────────────┐
│  Ethernet  │  → TCP/IP packets
│  Network   │  → Port 554
└──────┬─────┘  → Low latency (~200ms)
       │
       ▼
Step 3: RECEIVE
┌────────────┐
│  Jetson    │  → OpenCV VideoCapture
│  (Client)  │  → Decode H.264
└──────┬─────┘  → Get BGR frames
       │
       ▼
Step 4: AI PROCESSING
┌────────────┐
│  YOLOv8    │  → Input: 640x640 RGB
│  Neural    │  → Process: CNN layers
│  Network   │  → Output: Bounding boxes
└──────┬─────┘
       │
       ▼
Step 5: RESULTS
┌────────────┐
│  Output    │  → Draw boxes
│            │  → Save video/images
│            │  → Display window
└────────────┘
```

---

## 💻 Code Flow

```python
# 1. CONNECT TO CAMERA (RTSP)
rtsp_url = "rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/102"
cap = cv2.VideoCapture(rtsp_url)
# ↑ OpenCV handles RTSP protocol automatically!

# 2. LOAD AI MODEL
model = YOLO('models/yolov8n.pt')
# ↑ Loaded once, runs on GPU

# 3. PROCESSING LOOP
while True:
    # 3a. Get frame from RTSP
    ret, frame = cap.read()
    # ↑ This is video frame dari Hikvision!
    
    # 3b. Run AI detection
    results = model(frame)
    # ↑ YOLOv8 detects humans on Jetson GPU
    
    # 3c. Draw results
    for bbox in results:
        cv2.rectangle(frame, bbox, color=(0,255,0))
    
    # 3d. Display
    cv2.imshow('Detection', frame)
```

**Sesimple itu!** Camera hanya kirim video, AI processing di Jetson.

---

## 📊 Component Responsibilities

### Camera (Hikvision DS-2CD2120F-I)
```
Hardware:
├─ Image Sensor (capture light)
├─ ISP (Image Signal Processor)
├─ H.264 Encoder (compress video)
└─ Network Interface (send RTSP)

Software:
├─ Embedded Linux
├─ RTSP Server
└─ Web Interface

Output: RTSP stream H.264
```

### Processing Unit (Jetson Nano/Xavier/Orin)
```
Hardware:
├─ CPU (general processing)
├─ GPU (CUDA cores for AI)
├─ NVDEC (hardware video decode)
└─ Network Interface (receive RTSP)

Software:
├─ Ubuntu Linux + JetPack
├─ OpenCV (RTSP client + video decode)
├─ PyTorch (AI framework)
└─ YOLOv8 (AI model)

Output: Detection results
```

---

## ⚡ Performance Metrics

### Latency Breakdown

```
Camera → Network → Jetson → Display
  50ms     200ms    100ms      16ms
  ────     ─────    ─────      ────
Encode    RTSP     YOLOv8     Render
         Stream   Inference

Total: ~366ms (< 400ms) ✅ Real-time!
```

### Bandwidth Usage

```
Main Stream (1080p):  4-6 Mbps  ← High quality, heavy
Sub Stream (720p):    1-2 Mbps  ← Recommended! ✅
Third Stream (480p):  0.5 Mbps  ← Low quality
```

### Processing Power

```
Jetson Nano (4GB):
├─ YOLOv8n: 15-20 FPS @ 720p
├─ YOLOv8s: 8-12 FPS @ 720p
└─ Power: 5-10W

Jetson Xavier NX:
├─ YOLOv8n: 45-60 FPS @ 720p
├─ YOLOv8s: 30-40 FPS @ 720p
└─ Power: 15-20W

Jetson Orin Nano:
├─ YOLOv8n: 60+ FPS @ 720p
├─ YOLOv8s: 45-60 FPS @ 720p
└─ Power: 15-25W
```

---

## 🎯 Key Points untuk Presentasi

### 1. **Separation of Concerns**
- Camera: Video capture & streaming (hardware)
- Jetson: AI processing (software)
- **Benefit**: Scalable, cost-effective

### 2. **Standard Protocol**
- RTSP: Industry standard (CCTV worldwide)
- OpenCV: Built-in support, easy integration
- **Benefit**: Reliable, well-documented

### 3. **Real-time Performance**
- <400ms total latency
- 15-60 FPS depending on hardware
- **Benefit**: Immediate detection, real-time alerts

### 4. **Cost Efficiency**
```
Traditional Approach:
  Smart Camera with AI = Rp 10-20 juta each
  10 cameras = Rp 100-200 juta ❌

Our Approach:
  Hikvision camera = Rp 2-3 juta
  × 10 cameras = Rp 20-30 juta
  + 1 Jetson Xavier = Rp 3-5 juta
  Total = Rp 23-35 juta ✅
  
  Saving: 60-80%!
```

### 5. **Flexibility**
- Easy to upgrade AI model (just software update)
- Add more cameras without buying new AI hardware
- Change detection algorithm anytime

---

## 📝 Summary

**"Sistem ini memisahkan hardware (camera) dan software (AI). Camera Hikvision hanya streaming video via RTSP, semua AI processing di Jetson. Ini standar industri yang efisien dan scalable."**

**Analogi:**
```
Camera = Camera phone (ambil foto)
Jetson = Instagram filter (processing)

Foto dikirim via internet (RTSP),
Filter diapply di server (Jetson),
Hasil dikembalikan (detection)
```

Sesimple itu! 🎯
