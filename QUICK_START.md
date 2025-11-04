# Quick Start Guide# 🚀 Quick Start Guide



## 🚀 **Setup & Run dalam 3 Langkah**## Setup Cepat



### **Step 1: Activate Environment**### 1. Aktivasi Virtual Environment

```bash```bash

cd /Users/HCMPublic/Kuliah/Project/hikvision_human_detectioncd /Users/HCMPublic/Kuliah/Project/hikvision_human_detection

source venv/bin/activatesource venv/bin/activate

``````



### **Step 2: Test dengan Webcam**### 2. Jalankan dengan Webcam (Testing)

```bash```bash

python src/main.py --webcam./run_webcam.sh

```# atau

python src/main.py --webcam

**Expected output:**```

- Window muncul dengan webcam feed

- Green bounding box di sekitar manusia### 3. Jalankan dengan Kamera Hikvision

- Label: "Person 0.85" (85% confidence)

- FPS counter di pojok#### Opsi A: Edit dan Jalankan Script

1. Edit file `run_hikvision.sh`

**Controls:**2. Ubah konfigurasi:

- Press `q` → Quit   ```bash

- Press `s` → Save screenshot   CAMERA_IP="192.168.1.64"      # IP kamera Anda

- Press `r` → Reset statistics   USERNAME="admin"               # Username kamera

   PASSWORD="admin123"            # Password kamera

### **Step 3: Connect Hikvision Camera**   CHANNEL="102"                  # 101=HD, 102=SD

```bash   ```

python src/main.py --rtsp rtsp://admin:Admin123@192.168.1.64:554/Streaming/Channels/1023. Jalankan:

```   ```bash

   ./run_hikvision.sh

---   ```



## 🎯 **Detection Settings**#### Opsi B: Command Line Langsung

```bash

### **YOLO Configuration:**python src/main.py --rtsp rtsp://admin:password@192.168.1.64:554/Streaming/Channels/102

``````

✅ Model: YOLOv8n (Nano - fastest)

✅ Detection: PERSON ONLY (class 0)## 🎮 Kontrol

✅ Confidence: 50% minimum

✅ Speed: 20+ FPS (Jetson Nano), 60+ FPS (Jetson Xavier)Saat aplikasi berjalan:

```- **`q`** → Keluar

- **`s`** → Screenshot

### **What is Detected:**- **`r`** → Reset statistik

- ✅ **Manusia** (Person)

- ❌ Mobil (Car) - Disabled## 📋 Checklist Sebelum Mulai

- ❌ Kucing (Cat) - Disabled  

- ❌ Anjing (Dog) - Disabled### Untuk Kamera Hikvision:

- ❌ 76 objects lainnya - Disabled- [ ] Kamera terhubung ke network yang sama

- [ ] Cek IP kamera (gunakan SADP Tool atau web interface)

**See `YOLO_CLASSES.md` for full class list.**- [ ] Test RTSP URL dengan VLC Player

- [ ] Username dan password benar

---- [ ] Port 554 tidak diblok firewall



## 📹 **Camera Modes**### Test RTSP dengan VLC:

1. Buka VLC Player

### **1. Webcam (Testing)**2. Media → Open Network Stream

```bash3. Masukkan URL: `rtsp://admin:password@192.168.1.64:554/Streaming/Channels/102`

python src/main.py --webcam4. Play

```

✅ Good for: Development, testing, demoJika VLC bisa play video, maka aplikasi juga akan bisa!



### **2. Single RTSP Camera**## 📁 Struktur File

```bash

# Main stream (1080p - high quality)```

python src/main.py --rtsp rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/101hikvision_human_detection/

├── README.md                 ← Dokumentasi lengkap

# Sub stream (720p - recommended for AI)├── QUICK_START.md           ← File ini

python src/main.py --rtsp rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/102├── requirements.txt         ← Dependencies

```├── run_hikvision.sh         ← Script untuk Hikvision

✅ Good for: Single camera deployment├── run_webcam.sh            ← Script untuk webcam

├── models/

### **3. Multiple Cameras**│   └── yolov8n.pt          ← Model YOLO (sudah didownload)

```bash├── src/

# Edit camera_config.py first│   ├── camera_stream.py    ← Modul kamera

nano camera_config.py│   ├── detector.py         ← Modul deteksi

│   └── main.py            ← Program utama

# Run multi-camera system├── outputs/

./run_multi_camera.sh│   ├── logs/              ← Log files

```│   └── frames/            ← Screenshots

✅ Good for: 4-8 cameras with grid display└── venv/                  ← Virtual environment (sudah setup)

```

### **4. Video File**

```bash## ⚙️ Tips Optimasi

python src/main.py --video path/to/video.mp4

```### Untuk FPS Lebih Tinggi:

✅ Good for: Testing with recorded footage1. Gunakan Sub Stream (Channel 102) bukan Main Stream (101)

2. Turunkan confidence: `--conf 0.4`

---3. Gunakan YOLOv8n (tercepat)



## ⚙️ **Advanced Options**### Untuk Akurasi Lebih Tinggi:

1. Gunakan Main Stream (Channel 101)

### **Adjust Confidence Threshold**2. Naikkan confidence: `--conf 0.6`

```bash3. Gunakan model lebih besar: `--model models/yolov8s.pt` (harus download dulu)

# Lower threshold (detect more, but might have false positives)

python src/main.py --webcam --conf 0.3## 🔧 Troubleshooting Cepat



# Higher threshold (only very confident detections)### "Cannot connect to camera"

python src/main.py --webcam --conf 0.7```bash

# Test ping ke kamera

# Default: 0.5 (balanced)ping 192.168.1.64

python src/main.py --webcam

```# Test dengan VLC Player dulu

# Pastikan RTSP URL format benar

### **Save Video Output**```

```bash

python src/main.py --webcam --save-video### "Model not found"

# Output: outputs/detection_YYYYMMDD_HHMMSS.avi```bash

```# Model sudah ada di models/yolov8n.pt

# Jika tidak ada, jalankan:

### **Custom Model**cd models

```bashpython -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Use larger model (more accurate, slower)```

python src/main.py --webcam --model models/yolov8m.pt

### "Module not found"

# Use nano model (faster, default)```bash

python src/main.py --webcam --model models/yolov8n.pt# Pastikan virtual environment aktif

```source venv/bin/activate



---# Cek dengan:

which python  # Harus menunjuk ke venv/bin/python

## 🔧 **Troubleshooting**```



### **Problem: "ModuleNotFoundError: No module named 'ultralytics'"**## 📸 Contoh Output

```bash

source venv/bin/activate  # Activate environment first!Aplikasi akan menampilkan:

pip install ultralytics opencv-python "numpy<2"- ✅ Real-time video dengan bounding box

```- ✅ Label "Person" + confidence score

- ✅ Info overlay: timestamp, jumlah deteksi, FPS

### **Problem: "Camera not found"**- ✅ Log di terminal dan file

```bash

# Test camera connection first## 📞 Format RTSP URL Hikvision

python test_camera.py  # Edit IP inside first

```

# Or test with VLCrtsp://[username]:[password]@[ip]:[port]/Streaming/Channels/[channel]

vlc rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/102```

```

Contoh:

### **Problem: Low FPS**- Main Stream: `rtsp://admin:admin123@192.168.1.64:554/Streaming/Channels/101`

```bash- Sub Stream: `rtsp://admin:admin123@192.168.1.64:554/Streaming/Channels/102`

# Use sub stream instead of main stream

# Change: /Channels/101 → /Channels/102## ✅ Verifikasi Setup



# Or use smaller modelJalankan test berikut untuk memastikan semuanya OK:

python src/main.py --rtsp <url> --model models/yolov8n.pt

``````bash

# 1. Cek Python

### **Problem: No detection / False positives**python --version  # Output: Python 3.10.x

```bash

# Adjust confidence# 2. Cek virtual environment

python src/main.py --webcam --conf 0.3  # Lower = more sensitivewhich python  # Output: .../venv/bin/python

python src/main.py --webcam --conf 0.7  # Higher = more strict

```# 3. Cek dependencies

pip list | grep ultralytics  # Output: ultralytics 8.3.224

---pip list | grep opencv       # Output: opencv-python 4.12.0.88



## 📊 **Performance Expectations**# 4. Cek model

ls -lh models/yolov8n.pt    # Output: ~6.2MB

### **Mac/Laptop (CPU only)**

```# 5. Test import

Model    | FPS  | Accuracypython -c "from ultralytics import YOLO; import cv2; print('OK')"

---------|------|----------# Output: OK

YOLOv8n  | 5-10 | Good```

YOLOv8s  | 3-5  | Better

YOLOv8m  | 1-3  | BestJika semua test di atas berhasil, aplikasi siap digunakan! 🎉

```

## 🎯 Next Steps

### **Jetson Nano (GPU)**

```1. Test dengan webcam: `./run_webcam.sh`

Model    | FPS     | Cameras2. Test dengan kamera Hikvision: edit `run_hikvision.sh` lalu jalankan

---------|---------|----------3. Baca `README.md` untuk dokumentasi lengkap

YOLOv8n  | 20-25   | 1-44. Eksperimen dengan parameter `--conf`, `--save-video`, dll

YOLOv8s  | 12-15   | 1-2

```Good luck! 🚀


### **Jetson Xavier NX (GPU)**
```
Model    | FPS     | Cameras
---------|---------|----------
YOLOv8n  | 60-80   | 1-8
YOLOv8s  | 40-50   | 1-6
YOLOv8m  | 25-30   | 1-4
```

---

## 🌐 **Hikvision Camera Setup**

### **1. Enable RTSP**
1. Login ke camera web interface: `http://192.168.1.64`
2. Go to: **Configuration → Network → Advanced Settings → RTSP**
3. Check: ✅ Enable RTSP
4. Port: `554` (default)
5. Save

### **2. Get RTSP URL**
```
Main Stream (1080p):
rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101

Sub Stream (720p):
rtsp://admin:password@192.168.1.64:554/Streaming/Channels/102  ← Recommended
```

### **3. Test Connection**
```bash
# Method 1: VLC Media Player
vlc rtsp://admin:password@192.168.1.64:554/Streaming/Channels/102

# Method 2: Python test script
python test_camera.py  # Edit IP inside
```

---

## 📁 **Project Structure**

```
hikvision_human_detection/
├── src/
│   ├── main.py              ← Main entry point (single camera)
│   ├── detector.py          ← YOLO detection (person only)
│   ├── camera_stream.py     ← RTSP stream handler
│   └── multi_camera.py      ← Multi-camera system
├── models/
│   └── yolov8n.pt           ← AI model (6MB)
├── outputs/
│   ├── frames/              ← Screenshots
│   └── logs/                ← Log files
├── camera_config.py         ← Camera configuration
├── run_multi_camera.sh      ← Multi-camera launcher
├── test_camera.py           ← Camera connection tester
└── venv/                    ← Python environment
```

---

## 📚 **Documentation Files**

- `README.md` - Project overview
- `QUICK_START.md` - This file (quick start)
- `MULTI_CAMERA_GUIDE.md` - Multiple cameras setup
- `JETSON_SETUP.md` - Deploy to NVIDIA Jetson
- `ARCHITECTURE.md` - System architecture
- `CAMERA_CONFIG.md` - Camera configuration details
- `YOLO_CLASSES.md` - YOLO detection classes

---

## ✅ **Checklist**

Before running in production:

- [ ] ✅ Virtual environment activated
- [ ] ✅ Model downloaded (yolov8n.pt exists)
- [ ] ✅ Camera IP configured
- [ ] ✅ RTSP enabled on camera
- [ ] ✅ Network connectivity verified
- [ ] ✅ Test with webcam successful
- [ ] ✅ Test with RTSP camera successful
- [ ] ✅ Confidence threshold adjusted (if needed)

---

## 🎯 **Common Commands Cheat Sheet**

```bash
# Activate environment
source venv/bin/activate

# Test webcam
python src/main.py --webcam

# Single camera
python src/main.py --rtsp rtsp://admin:pass@IP:554/Streaming/Channels/102

# Multi-camera
./run_multi_camera.sh

# Test camera connection
python test_camera.py

# Check YOLO settings
cat src/detector.py | grep "classes="

# View logs
tail -f outputs/logs/detection.log
```

---

## 💬 **Need Help?**

1. Check `YOLO_CLASSES.md` - Understanding detection classes
2. Check `CAMERA_CONFIG.md` - Camera setup issues
3. Check `JETSON_SETUP.md` - Jetson deployment
4. Check `MULTI_CAMERA_GUIDE.md` - Multiple cameras

**System ready to use! 🚀**
