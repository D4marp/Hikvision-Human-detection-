#!/usr/bin/env python3
"""
Advanced Multi-Detection System - Main Script
Deteksi: Helmet, Jacket, Fall, Smoke, Fight, Weapons, Intrusion, Gathering
Real-time dengan YOLOv8m + Threaded Camera Streaming
"""

import cv2
import logging
import time
import argparse
import sys
from pathlib import Path

# Import modules
from src.camera_stream_threaded import ThreadedHikvisionCamera
from src.advanced_detector import AdvancedDetector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/logs/advanced_detection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main advanced detection system"""
    
    parser = argparse.ArgumentParser(description='Advanced Multi-Detection System')
    parser.add_argument('--rtsp', type=str, required=True,
                       help='RTSP URL dari kamera (contoh: rtsp://admin:password@10.0.66.29:554/Streaming/Channels/102)')
    parser.add_argument('--model', type=str, default='models/yolov8m.pt',
                       help='Path ke YOLO model (default: models/yolov8m.pt - comprehensive detection)')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold (0-1, default: 0.5)')
    parser.add_argument('--output', type=str, default=None,
                       help='Save video output (optional)')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("ADVANCED MULTI-DETECTION SYSTEM")
    logger.info("="*60)
    logger.info("Detecting: Helmet, Jacket, Weapons, Smoke, Fall, Fight,")
    logger.info("           Intrusion, Gathering, Activities, and more...")
    logger.info("="*60)
    
    # Initialize detector
    detector = AdvancedDetector(model_path=args.model, conf_threshold=args.conf)
    if not detector.load_model():
        logger.error("Failed to load model. Exiting.")
        return
    
    # Initialize camera
    logger.info(f"Connecting to camera: {args.rtsp}")
    camera = ThreadedHikvisionCamera(args.rtsp, "Advanced Detection Camera")
    if not camera.connect():
        logger.error("Failed to connect to camera. Exiting.")
        return
    
    # Setup video writer if output specified
    video_writer = None
    if args.output:
        info = camera.get_frame_info()
        if info:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                args.output, fourcc, 15,
                (info['width'], info['height'])
            )
            logger.info(f"Output video will be saved to: {args.output}")
    
    # Main detection loop
    logger.info("Starting detection loop. Press 'q' to quit, 's' for screenshot")
    
    fps = 0
    frame_time = time.time()
    frame_count = 0
    prev_frame = None
    
    try:
        while True:
            # Read frame from camera
            ret, frame = camera.read_frame()
            if not ret:
                logger.warning("Failed to read frame")
                time.sleep(0.5)
                continue
            
            # Run advanced detection
            detections, annotated_frame = detector.detect_objects(frame)
            
            # Detect activities
            activities = detector.detect_activities(frame, prev_frame)
            
            # Check for safety violations (helmet, jacket)
            violations = detector.detect_helmet_violation(detections)
            
            # Check for crowd/intrusion
            crowd = detector.detect_intrusion_crowd(detections)
            
            # Check for weapons
            has_weapon = detector.detect_weapon_intrusion(detections)
            
            # Generate report
            report = detector.generate_report(detections, activities, violations, crowd, has_weapon)
            
            # Add alerts overlay
            annotated_frame = detector.add_alert_overlay(annotated_frame, report)
            annotated_frame = detector.add_info_overlay(annotated_frame, crowd, fps)
            
            # Calculate FPS
            current_time = time.time()
            fps = 1 / (current_time - frame_time)
            frame_time = current_time
            frame_count += 1
            
            # Display
            cv2.imshow('Advanced Detection - Hikvision', annotated_frame)
            
            # Save video if enabled
            if video_writer is not None:
                video_writer.write(annotated_frame)
            
            # Log important detections
            if violations['no_helmet'] > 0:
                logger.warning(f"⚠️  HELMET VIOLATION: {violations['no_helmet']} person(s) without helmet!")
            
            if has_weapon:
                logger.warning("🚨 WEAPON DETECTED!")
            
            if crowd['crowd_detected']:
                logger.info(f"👥 Crowd detected: {crowd['person_count']} persons")
            
            if activities.get('smoke_detected'):
                logger.warning("🔥 SMOKE DETECTED!")
            
            # Save screenshot on 's' key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"outputs/screenshots/advanced_detection_{int(time.time())}.png"
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(filename, annotated_frame)
                logger.info(f"Screenshot saved: {filename}")
            
            prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            prev_frame = cv2.GaussianBlur(prev_frame, (21, 21), 0)
    
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    
    finally:
        logger.info("="*60)
        logger.info("STATISTICS")
        logger.info(f"Total frames processed: {frame_count}")
        logger.info(f"Average FPS: {frame_count / (time.time() - (frame_time - 1/fps)) if fps > 0 else 0:.1f}")
        logger.info("="*60)
        
        cv2.destroyAllWindows()
        camera.disconnect()
        
        if video_writer is not None:
            video_writer.release()
        
        logger.info("Program finished")


if __name__ == "__main__":
    main()
