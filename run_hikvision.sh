#!/bin/bash
# Script untuk menjalankan Human Detection dengan Hikvision Camera
# Edit konfigurasi di bawah sesuai dengan setup kamera Anda

# ==================== KONFIGURASI ====================

# Konfigurasi Kamera Hikvision
CAMERA_IP="192.168.1.64"
CAMERA_PORT="554"
USERNAME="admin"
PASSWORD="admin123"
CHANNEL="101"  # 101 = Main Stream (HD), 102 = Sub Stream (SD)

# RTSP URL
RTSP_URL="rtsp://${USERNAME}:${PASSWORD}@${CAMERA_IP}:${CAMERA_PORT}/Streaming/Channels/${CHANNEL}"

# Konfigurasi Deteksi
CONFIDENCE_THRESHOLD="0.5"  # 0.0 - 1.0
MODEL_PATH="models/yolov8n.pt"

# Opsi Output
SAVE_VIDEO="false"  # true atau false
OUTPUT_PATH="outputs/detection_output.avi"

# ==================== END KONFIGURASI ====================

# Aktivasi virtual environment
echo "Mengaktifkan virtual environment..."
source venv/bin/activate

# Jalankan program
echo "Memulai Human Detection System..."
echo "Kamera: ${CAMERA_IP}"
echo "Channel: ${CHANNEL}"
echo "Tekan 'q' untuk keluar, 's' untuk screenshot, 'r' untuk reset stats"
echo ""

if [ "$SAVE_VIDEO" = "true" ]; then
    python src/main.py --rtsp "$RTSP_URL" \
                       --model "$MODEL_PATH" \
                       --conf "$CONFIDENCE_THRESHOLD" \
                       --save-video \
                       --output "$OUTPUT_PATH"
else
    python src/main.py --rtsp "$RTSP_URL" \
                       --model "$MODEL_PATH" \
                       --conf "$CONFIDENCE_THRESHOLD"
fi
