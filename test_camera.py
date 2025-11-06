"""
Test RTSP Connection ke Hikvision Camera
Jalankan ini untuk verify camera setup sudah benar
"""

import cv2
import sys

# ============================================
# EDIT SESUAI CAMERA ANDA:
# ============================================
CAMERA_IP = "10.0.66.29"  # Updated IP
USERNAME = "admin"
PASSWORD = "Novarion1"  # Updated password
CHANNEL = 102  # 101=Main(1080p), 102=Sub(720p), 103=Third(480p)

# Build RTSP URL
rtsp_url = f"rtsp://{USERNAME}:{PASSWORD}@{CAMERA_IP}:554/Streaming/Channels/{CHANNEL}"

print("=" * 50)
print("HIKVISION CAMERA CONNECTION TEST")
print("=" * 50)
print(f"Camera IP: {CAMERA_IP}")
print(f"Channel: {CHANNEL}")
print(f"RTSP URL: rtsp://{USERNAME}:***@{CAMERA_IP}:554/Streaming/Channels/{CHANNEL}")
print("-" * 50)

# Test connection
print("\n[1/3] Connecting to camera...")
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ FAILED: Cannot connect to camera!")
    print("\nTroubleshooting:")
    print("1. Check camera IP address")
    print("2. Check username/password")
    print("3. Verify camera is powered on")
    print("4. Test ping: ping", CAMERA_IP)
    print("5. Test RTSP port: nc -zv", CAMERA_IP, "554")
    sys.exit(1)

print("✅ Connected successfully!")

# Get stream info
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

print(f"\n[2/3] Stream Information:")
print(f"  Resolution: {width}x{height}")
print(f"  FPS: {fps}")

# Read test frame
print("\n[3/3] Reading test frame...")
ret, frame = cap.read()

if not ret:
    print("❌ FAILED: Cannot read frame from camera!")
    cap.release()
    sys.exit(1)

print("✅ Frame received successfully!")
print(f"  Frame shape: {frame.shape}")

# Save test image
test_image = "outputs/frames/camera_test.jpg"
cv2.imwrite(test_image, frame)
print(f"  Test image saved: {test_image}")

# Display frame
print("\n[INFO] Displaying video stream...")
print("       Press 'q' to quit")

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("⚠️  Lost connection to camera!")
            break
        
        # Add text overlay
        cv2.putText(frame, f"Hikvision {CAMERA_IP}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Resolution: {width}x{height}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Hikvision Camera Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n\n[INFO] Interrupted by user")

finally:
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 50)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nCamera is ready for human detection!")
    print("\nRun main application:")
    print(f"  python src/main.py --rtsp {rtsp_url}")
    print("=" * 50)
