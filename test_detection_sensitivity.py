#!/usr/bin/env python3
"""
Test Human Detection dengan Confidence Threshold Rendah
Untuk deteksi jarak jauh
"""

import cv2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detector import HumanDetector
from src.camera_stream import HikvisionCamera

# ============================================
# CAMERA CONFIG
# ============================================
CAMERA_IP = "10.0.66.29"
USERNAME = "admin"
PASSWORD = "Novarion1"
CHANNEL = 102  # Sub stream (720p) - lebih cepat

# Build RTSP URL
rtsp_url = f"rtsp://{USERNAME}:{PASSWORD}@{CAMERA_IP}:554/Streaming/Channels/{CHANNEL}"

print("=" * 70)
print("HUMAN DETECTION TEST - LOW THRESHOLD (Deteksi Jarak Jauh)")
print("=" * 70)
print(f"Camera: {CAMERA_IP}")
print(f"RTSP URL: rtsp://{USERNAME}:***@{CAMERA_IP}:554/Streaming/Channels/{CHANNEL}")
print("-" * 70)

# Test beberapa threshold values
THRESHOLDS = [0.15, 0.20, 0.25, 0.30]

for threshold in THRESHOLDS:
    print(f"\n{'='*70}")
    print(f"Testing dengan CONFIDENCE THRESHOLD: {threshold} ({int(threshold*100)}%)")
    print(f"{'='*70}")
    
    # Initialize detector dengan threshold rendah
    detector = HumanDetector(model_path="models/yolov8n.pt", conf_threshold=threshold)
    
    print(f"[1/3] Loading YOLOv8 model...")
    if not detector.load_model():
        print("❌ Failed to load model!")
        continue
    
    print(f"✅ Model loaded with confidence threshold: {threshold}")
    
    # Connect camera
    print(f"\n[2/3] Connecting to camera...")
    camera = HikvisionCamera(rtsp_url)
    
    if not camera.connect():
        print("❌ Cannot connect to camera!")
        print("\nCheck:")
        print(f"  1. Camera IP: {CAMERA_IP}")
        print(f"  2. Username: {USERNAME}")
        print(f"  3. Password: {'*' * len(PASSWORD)}")
        print(f"  4. RTSP enabled: Login ke http://{CAMERA_IP}")
        continue
    
    print("✅ Camera connected!")
    
    # Test detection
    print(f"\n[3/3] Testing detection untuk 10 frames...")
    print(f"Threshold: {threshold} - Semakin rendah, semakin sensitif")
    print("-" * 70)
    
    detection_count = 0
    for i in range(10):
        ret, frame = camera.read_frame()
        
        if not ret or frame is None:
            print(f"Frame {i+1}: ❌ Failed to read")
            continue
        
        # Run detection
        annotated_frame, detections, human_count = detector.detect_humans(frame)
        
        if human_count > 0:
            detection_count += 1
            print(f"Frame {i+1}: ✅ {human_count} orang terdeteksi!")
            
            # Show confidence for each detection
            for idx, det in enumerate(detections, 1):
                conf = det['confidence']
                bbox = det['bbox']
                print(f"         Person {idx}: Confidence {conf:.2%} at {bbox}")
        else:
            print(f"Frame {i+1}: ⚪ No detection")
    
    print(f"\n{'='*70}")
    print(f"SUMMARY: {detection_count}/10 frames ada detection dengan threshold {threshold}")
    print(f"{'='*70}")
    
    camera.disconnect()
    
    # Jika sudah ada detection, break
    if detection_count > 0:
        print(f"\n✅ RECOMMENDATION: Gunakan threshold {threshold} untuk deteksi optimal")
        print(f"\nUntuk apply:")
        print(f"  1. Edit camera_config.py")
        print(f"  2. Set: 'conf_threshold': {threshold}")
        break

print("\n" + "=" * 70)
print("TIPS UNTUK DETEKSI JARAK JAUH:")
print("=" * 70)
print("""
1. THRESHOLD RENDAH (0.15-0.30):
   - Detect jarak jauh (manusia kecil di frame)
   - Lebih sensitif, bisa ada false positive
   
2. THRESHOLD MEDIUM (0.40-0.60):
   - Balanced detection
   - Good untuk jarak dekat-medium
   
3. THRESHOLD TINGGI (0.70-0.90):
   - Only very confident detection
   - Good untuk jarak sangat dekat

4. RESOLUSI CAMERA:
   - Main stream (1080p): Lebih detail, tapi lambat
   - Sub stream (720p): Balance speed & quality ← RECOMMENDED
   - Third stream (480p): Fast tapi kurang detail

5. POSISI CAMERA:
   - Height: 2.5-3 meter dari ground
   - Angle: 15-30 derajat ke bawah
   - Hindari backlight (cahaya dari belakang)

6. LIGHTING:
   - Cukup cahaya (minimal 50 lux)
   - Hindari extreme contrast
   - Use IR night vision jika gelap

7. UPGRADE MODEL (Optional):
   - yolov8n.pt: Fastest (current)
   - yolov8s.pt: Better accuracy
   - yolov8m.pt: Even better, but slower
   - yolov8l.pt: Best, but very slow
""")

print("\n" + "=" * 70)
print("Test selesai!")
print("=" * 70)
