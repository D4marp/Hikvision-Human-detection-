"""
Simple RTSP Connection Demo
Untuk menunjukkan betapa mudahnya connect ke Hikvision camera
"""

import cv2

# RTSP URL dari Hikvision camera
rtsp_url = "rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101"

# Connect ke camera (OpenCV built-in support RTSP!)
cap = cv2.VideoCapture(rtsp_url)

print("Connecting to Hikvision camera...")

if cap.isOpened():
    print("✅ Connected successfully!")
    
    # Read frame
    ret, frame = cap.read()
    
    if ret:
        print(f"✅ Frame received: {frame.shape}")
        print("✅ Ready for YOLOv8 processing!")
    
    cap.release()
else:
    print("❌ Failed to connect")

"""
Output:
  Connecting to Hikvision camera...
  ✅ Connected successfully!
  ✅ Frame received: (720, 1280, 3)
  ✅ Ready for YOLOv8 processing!

Sesederhana ini! Hanya 3 baris code:
  1. cv2.VideoCapture(rtsp_url)  ← Connect
  2. cap.read()                   ← Get frame
  3. detector.detect(frame)       ← AI processing
"""
