#!/bin/bash
# Script untuk menjalankan Human Detection dengan Webcam (untuk testing)

echo "Mengaktifkan virtual environment..."
source venv/bin/activate

echo "Memulai Human Detection System dengan Webcam..."
echo "Tekan 'q' untuk keluar, 's' untuk screenshot, 'r' untuk reset stats"
echo ""

python src/main.py --webcam --conf 0.5
