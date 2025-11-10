#!/usr/bin/env python3
"""
Test Office Detection with Laptop Webcam
Gunakan untuk testing sitting duration dan effectiveness score
"""

import cv2
import sys
from src.office_analyzer import OfficeAnalyzer
from src.detector import HumanDetector
import numpy as np
from datetime import datetime

def test_office_detection_webcam():
    """Test office detection dengan laptop webcam"""
    
    print("\n" + "="*70)
    print("🎥 OFFICE DETECTION TEST - LAPTOP WEBCAM")
    print("="*70)
    
    # Initialize detectors
    print("\n📦 Initializing detectors...")
    try:
        human_detector = HumanDetector()
        office_analyzer = OfficeAnalyzer()
        print("✅ Detectors initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing detectors: {e}")
        return
    
    # Open webcam
    print("\n📹 Opening laptop webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Cannot open webcam")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("✅ Webcam opened successfully")
    print("\n" + "="*70)
    print("🎯 INSTRUCTIONS:")
    print("="*70)
    print("1. Position yourself in front of camera")
    print("2. Try SIT in a chair - sitting duration will track")
    print("3. Move around - activity level will change")
    print("4. Press 'q' to quit")
    print("\n📊 Metrics to watch:")
    print("   - Sitting Duration: How long you've been sitting")
    print("   - Activity Level: idle/active/very_active")
    print("   - Effectiveness Score: 0-100 (A-F grade)")
    print("   - Posture: sitting/standing/bending")
    print("="*70 + "\n")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error reading frame")
            break
        
        frame_count += 1
        
        # Flip frame for webcam
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Detect humans
        detections = human_detector.detect_humans(frame)
        
        # Process office detection if humans detected
        stats_text = []
        
        if detections and len(detections) > 0:
            for i, detection in enumerate(detections):
                x1, y1, x2, y2, conf = detection
                
                # Office analysis
                office_stats = office_analyzer.process_frame(frame, detection)
                
                # Draw bounding box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), 
                            (0, 255, 0), 2)
                
                # Get individual stats
                sitting_info = office_analyzer.detect_sitting_duration(detection, frame)
                activity = office_analyzer.detect_activity_level(detection)
                posture = office_analyzer.detect_posture(detection, frame)
                score = office_analyzer.calculate_effectiveness_score(office_stats)
                
                # Create info text
                grade = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'
                
                # Draw stats on frame
                y_offset = int(y1) - 10
                
                # Sitting status
                sitting_status = sitting_info.get('status', 'unknown')
                sitting_color = (0, 255, 0) if sitting_status == 'sitting' else (255, 255, 0) if sitting_status == 'standing' else (255, 0, 0)
                
                cv2.putText(frame, f"Posture: {posture}", (int(x1), y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, sitting_color, 2)
                
                y_offset -= 30
                cv2.putText(frame, f"Activity: {activity}", (int(x1), y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                y_offset -= 30
                cv2.putText(frame, f"Effectiveness: {score:.0f}/100 [{grade}]", (int(x1), y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                
                y_offset -= 30
                sitting_duration = sitting_info.get('duration', 0)
                duration_text = f"{int(sitting_duration)}s"
                cv2.putText(frame, f"Sitting: {duration_text}", (int(x1), y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
                
                # Print to console
                print(f"\n👤 Worker #{i+1}")
                print(f"   Posture:       {posture.upper()}")
                print(f"   Activity:      {activity.upper()}")
                print(f"   Sitting Time:  {int(sitting_duration)}s")
                print(f"   Effectiveness: {score:.1f}/100 [Grade: {grade}]")
                print(f"   Risk Level:    {sitting_info.get('risk', 'unknown')}")
                
                if sitting_info.get('recommendation'):
                    print(f"   💡 Tip:        {sitting_info['recommendation']}")
        
        else:
            cv2.putText(frame, "No person detected", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Draw header
        cv2.putText(frame, f"Frame: {frame_count} | Office Detection Test", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (w - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        # Display frame
        cv2.imshow("Office Detection - Laptop Webcam Test", frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n\n✅ Test completed!")
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("🎉 TEST FINISHED")
    print("="*70)

if __name__ == "__main__":
    test_office_detection_webcam()
