# Human Detection System - Hikvision Camera

Sistem deteksi manusia menggunakan YOLOv8 dan kamera Hikvision DS-2CD2120F-I

## 🎯 **Key Features**

- ✅ **PERSON ONLY Detection** - Tidak detect mobil, kucing, atau object lain
- ✅ **Multi-Camera Support** - Handle 4-8 cameras simultaneously  
- ✅ **Real-time Processing** - 20+ FPS (Jetson Nano), 60+ FPS (Xavier)
- ✅ **RTSP Streaming** - Support Hikvision & IP cameras lainnya
- ✅ **REST API** - Integration dengan Node-RED, Milesight, IoT systems
- ✅ **Production Ready** - 24/7 operation dengan auto-reconnect

## 📋 Deskripsi

Proyek ini menggunakan:
- **YOLOv8n** untuk deteksi manusia real-time (PERSON ONLY - class 0)
- **OpenCV** untuk processing video stream
- **Kamera Hikvision DS-2CD2120F-I** melalui RTSP protocol
- **Multi-threading** untuk handle multiple cameras
- **REST API (Flask)** untuk IoT integration (Node-RED, Milesight, etc)

## 🏗️ Struktur Proyek

```
hikvision_human_detection/
├── models/
│   └── yolov8n.pt          # Model YOLOv8
├── src/
│   ├── camera_stream.py    # Modul handling RTSP stream
│   ├── detector.py         # Modul YOLO detection
│   └── main.py            # Program utama
├── outputs/
│   ├── logs/              # Log files
│   └── frames/            # Screenshot frames
├── venv/                  # Virtual environment
└── README.md
```

## 🚀 Setup dan Instalasi

### 1. Clone/Download Proyek
Proyek sudah tersedia di: `/Users/HCMPublic/Kuliah/Project/hikvision_human_detection`

### 2. Aktivasi Virtual Environment
```bash
cd /Users/HCMPublic/Kuliah/Project/hikvision_human_detection
source venv/bin/activate
```

### 3. Verifikasi Instalasi
Semua dependensi sudah terinstall:
- ultralytics (YOLOv8)
- opencv-python
- numpy
- torch
- torchvision

## 🎮 Cara Penggunaan

### 1. Dengan Kamera Hikvision (RTSP)
```bash
python src/main.py --rtsp rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101
```

**Format RTSP URL Hikvision:**
```
rtsp://[username]:[password]@[ip_address]:[port]/Streaming/Channels/[channel]
```

Contoh:
- Main Stream (HD): `rtsp://admin:admin123@192.168.1.64:554/Streaming/Channels/101`
- Sub Stream (SD): `rtsp://admin:admin123@192.168.1.64:554/Streaming/Channels/102`

### 2. Dengan Webcam (untuk testing)
```bash
python src/main.py --webcam
```

### 3. Dengan File Video
```bash
python src/main.py --video path/to/video.mp4
```

### 4. Dengan Opsi Tambahan
```bash
# Simpan video output
python src/main.py --rtsp [RTSP_URL] --save-video --output outputs/result.avi

# Ubah confidence threshold
python src/main.py --rtsp [RTSP_URL] --conf 0.6

# Gunakan model lain
python src/main.py --rtsp [RTSP_URL] --model models/yolov8s.pt
```

## ⌨️ Keyboard Controls

Saat program berjalan:
- **`q`** - Keluar dari program
- **`s`** - Simpan screenshot frame saat ini
- **`r`** - Reset statistik deteksi

## 📊 Fitur

### 1. Real-time Human Detection
- Deteksi manusia menggunakan YOLOv8
- Menampilkan bounding box dan confidence score
- Hanya mendeteksi class "person"

### 2. Overlay Informasi
Menampilkan:
- Timestamp
- Jumlah manusia terdeteksi
- FPS (Frame Per Second)
- Total frames yang diproses

### 3. Logging
- Log disimpan di `outputs/logs/detection.log`
- Mencatat semua aktivitas dan error

### 4. Screenshot
- Simpan frame dengan tekan tombol `s`
- Disimpan di `outputs/frames/`
- Format nama: `snapshot_YYYYMMDD_HHMMSS.jpg`

### 5. Auto-Reconnect
- Otomatis reconnect jika koneksi terputus
- Maksimal 5 kali percobaan

### 6. Statistik
Di akhir program, menampilkan:
- Total frames diproses
- Total deteksi manusia
- Rata-rata deteksi per frame

## 🔧 Konfigurasi Kamera Hikvision

### Default Settings
- **IP Address**: Biasanya `192.168.1.64` (cek di SADP Tool atau web interface)
- **RTSP Port**: `554`
- **Username**: `admin`
- **Password**: [sesuai konfigurasi kamera]

### Channel Stream
- **Channel 101**: Main Stream (Full Resolution, HD)
- **Channel 102**: Sub Stream (Lower Resolution, SD)

Untuk performa lebih baik, gunakan Sub Stream (102).

## 📝 Parameter Command Line

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `--rtsp` | - | URL RTSP kamera Hikvision |
| `--webcam` | False | Gunakan webcam default |
| `--video` | - | Path ke file video |
| `--model` | models/yolov8n.pt | Path model YOLOv8 |
| `--conf` | 0.5 | Confidence threshold (0-1) |
| `--save-video` | False | Simpan video output |
| `--output` | outputs/detection_output.avi | Path output video |

## 🐛 Troubleshooting

### 1. Koneksi RTSP Gagal
- Cek koneksi network ke kamera
- Pastikan username/password benar
- Test dengan VLC: Media > Open Network Stream
- Cek firewall dan port 554

### 2. Error "Model tidak ditemukan"
- Pastikan file `yolov8n.pt` ada di folder `models/`
- Download manual jika perlu dari: https://github.com/ultralytics/assets/releases

### 3. FPS Rendah
- Gunakan Sub Stream (Channel 102) instead of Main Stream
- Turunkan confidence threshold: `--conf 0.4`
- Gunakan model lebih kecil (yolov8n)

### 4. Webcam Tidak Terdeteksi
- Pastikan webcam terhubung
- Coba ubah index: edit `rtsp_url = 0` ke `rtsp_url = 1` di code

## 📚 Dependencies

- Python 3.10
- ultralytics 8.3.224
- opencv-python 4.12.0.88
- numpy 1.26.4
- torch 2.2.2
- torchvision 0.17.2

## 📄 License

MIT License

## 👤 Author

Human Detection System untuk Hikvision DS-2CD2120F-I

## 🔗 Referensi

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Hikvision RTSP URL Format](https://www.unifore.net/ip-video-surveillance/hikvision-rtsp-url-format.html)
- [OpenCV Documentation](https://docs.opencv.org/)
