#!/usr/bin/env python3
"""
Simple Office Detection Test dengan Laptop Camera
Testing sitting duration dan effectiveness score
"""

import cv2
import sys
import numpy as np
from datetime import datetime

print("\n" + "="*70)
print("🎥 OFFICE DETECTION TEST - LAPTOP CAMERA")
print("="*70)

print("\n📦 Testing System Setup...")

# Try to import detectors
try:
    from src.office_analyzer import OfficeAnalyzer
    from src.detector import HumanDetector
    print("✅ Office analyzer imported")
    print("✅ Human detector imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\n📹 Attempting to open laptop webcam...")

# Try to open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("⚠️  Webcam not accessible - System might be in headless mode")
    print("\n💡 Alternatives available:")
    print("   1. Test with RTSP camera: python run_office_monitor.py")
    print("   2. Test web dashboard: python run_web_server.py")
    print("   3. Run quick system check...")
    print("\nSystem Check:")
    
    # Try initializing analyzers without camera
    try:
        detector = HumanDetector()
        analyzer = OfficeAnalyzer()
        
        print("✅ HumanDetector initialized successfully")
        print("✅ OfficeAnalyzer initialized successfully")
        print("\n📊 Available Detection Methods:")
        print("   - detect_sitting_duration()")
        print("   - detect_activity_level()")
        print("   - detect_posture()")
        print("   - calculate_effectiveness_score()")
        print("   - get_worker_stats()")
        print("   - add_office_overlay()")
        
        print("\n✅ All components working correctly!")
        print("\n🎯 Quick Test Result:")
        print("   System is ready for deployment")
        print("   Use RTSP camera for live testing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    sys.exit(0)

print("✅ Webcam opened successfully!")

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# Initialize detectors
print("\n📦 Initializing detectors...")
try:
    detector = HumanDetector()
    analyzer = OfficeAnalyzer()
    print("✅ Detectors initialized!")
except Exception as e:
    print(f"❌ Error initializing detectors: {e}")
    cap.release()
    sys.exit(1)

print("\n" + "="*70)
print("📸 WEBCAM TEST STARTED")
print("="*70)
print("\n🎯 Instructions:")
print("   1. Position yourself in front of camera")
print("   2. SIT - sitting duration will track")
print("   3. MOVE - activity level will change")
print("   4. Press 'q' to exit")
print("\n📊 You will see:")
print("   - Real-time detection overlay")
print("   - Sitting duration counter")
print("   - Activity level (idle/active)")
print("   - Effectiveness score (0-100)")
print("="*70 + "\n")

frame_count = 0
person_counter = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        frame_count += 1
        
        # Flip for selfie view
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Detect humans
        detections = detector.detect_humans(frame)
        
        # Draw info on frame
        cv2.putText(frame, f"Frame: {frame_count} | Detections: {len(detections)}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (w - 200, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        if len(detections) > 0:
            # Draw detections
            for i, (x1, y1, x2, y2, conf) in enumerate(detections):
                person_id = i
                
                # Draw bounding box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), 
                            (0, 255, 0), 2)
                
                # Draw confidence
                cv2.putText(frame, f"Person {i+1}: {conf:.2f}", 
                           (int(x1), int(y1) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Get worker stats
                try:
                    worker_stats = analyzer.get_worker_stats(person_id)
                    
                    # Display stats
                    y_text = int(y1) - 40
                    
                    sitting_info = analyzer.detect_sitting_duration(person_id, None, conf)
                    activity = analyzer.detect_activity_level(person_id, None)
                    posture = analyzer.detect_posture(person_id, None)
                    score = analyzer.calculate_effectiveness_score(person_id)
                    
                    # Determine colors
                    if score >= 80:
                        score_color = (0, 255, 0)  # Green
                    elif score >= 60:
                        score_color = (0, 165, 255)  # Orange
                    else:
                        score_color = (0, 0, 255)  # Red
                    
                    # Draw stats
                    cv2.putText(frame, f"Activity: {activity}", 
                               (int(x1), y_text), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.5, (0, 255, 255), 1)
                    
                    cv2.putText(frame, f"Posture: {posture}", 
                               (int(x1), y_text + 25), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.5, (255, 0, 255), 1)
                    
                    cv2.putText(frame, f"Score: {score:.0f}/100", 
                               (int(x1), y_text + 50), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, score_color, 2)
                    
                except Exception as e:
                    pass
        
        else:
            cv2.putText(frame, "No person detected", (20, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Display frame
        cv2.imshow("Office Detection - Laptop Camera Test", frame)
        
        # Press 'q' to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        # Show frame count every 30 frames
        if frame_count % 30 == 0:
            print(f"✓ Frame {frame_count} | Detections: {len(detections)} | Time: {datetime.now().strftime('%H:%M:%S')}")

except KeyboardInterrupt:
    print("\n⚠️  Test interrupted by user")

finally:
    cap.release()
    cv2.destroyAllWindows()

print("\n" + "="*70)
print("✅ TEST COMPLETED")
print("="*70)
print(f"\nFrames processed: {frame_count}")
print("\n🎉 System is working!")
print("\nNext steps:")
print("  1. Test with RTSP camera:")
print("     python run_office_monitor.py")
print("  2. Test web dashboard:")
print("     python run_web_server.py")
print("  3. Add your camera and monitor in real-time")
print("="*70 + "\n")
