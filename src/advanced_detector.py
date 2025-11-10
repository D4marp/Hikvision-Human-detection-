"""
Advanced Multi-Detection System
Deteksi: Helmet, Jacket, Fall, Smoke, Fight, Weapons, Phone, Climb, Intrusion, Gathering
Menggunakan YOLOv8m untuk deteksi yang lebih akurat dan comprehensive
"""

import cv2
import logging
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import time

class AdvancedDetector:
    """
    Advanced detector untuk multiple objects dan activities
    """
    
    def __init__(self, model_path="models/yolov8m.pt", conf_threshold=0.5):
        """
        Initialize advanced detector
        
        Args:
            model_path (str): Path ke YOLO model
            conf_threshold (float): Confidence threshold (0-1)
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        # Class names untuk deteksi berbeda
        self.SAFETY_CLASSES = {
            'helmet': 0,           # Safety helmet
            'jacket': 1,           # Safety jacket/vest
            'person': 0,           # Person detection
        }
        
        # Activity detection classes (jika menggunakan model action detection)
        self.ACTIVITY_CLASSES = {
            'fall': 'fall',              # Person jatuh
            'smoke': 'smoke',            # Ada asap
            'fight': 'fight',            # Pertarungan
            'call': 'call',              # Sedang menelepon
            'run': 'run',                # Berlari
            'sleep': 'sleep',            # Tidur/tidak bergerak lama
            'climb': 'climb',            # Memanjat
            'intrusion': 'intrusion',    # Intrusi
            'weapon': 'weapon',          # Membawa senjata
            'gather': 'gather',          # Berkumpul
            'wander': 'wander',          # Berjalan tanpa tujuan
        }
        
        # Tracking untuk deteksi aktivitas
        self.frame_history = defaultdict(list)
        self.alert_history = defaultdict(int)
        
    def load_model(self):
        """Load YOLO model"""
        try:
            self.logger.info(f"Loading advanced model dari {self.model_path}...")
            self.model = YOLO(self.model_path)
            self.logger.info("✅ Advanced model berhasil di-load")
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False
    
    def detect_objects(self, frame):
        """
        Deteksi objects (helmet, jacket, weapons, phone, dll)
        
        Args:
            frame: Input frame
            
        Returns:
            tuple: (detections, annotated_frame)
        """
        if self.model is None:
            return [], frame
        
        try:
            results = self.model(frame, conf=self.conf_threshold)
            
            detections = []
            annotated_frame = frame.copy()
            
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Get class name
                    class_name = result.names.get(cls, f"Class_{cls}")
                    
                    # Filter untuk relevant classes
                    if conf >= self.conf_threshold:
                        detections.append({
                            'class': class_name,
                            'confidence': conf,
                            'bbox': (x1, y1, x2, y2),
                            'area': (x2 - x1) * (y2 - y1)
                        })
                        
                        # Draw bounding box
                        color = self._get_color_by_class(class_name)
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Add label
                        label = f"{class_name}: {conf:.2f}"
                        cv2.putText(annotated_frame, label, (x1, y1 - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            return detections, annotated_frame
            
        except Exception as e:
            self.logger.error(f"Error in detection: {str(e)}")
            return [], frame
    
    def detect_activities(self, frame, motion_history=None):
        """
        Deteksi aktivitas manusia (fall, fight, climb, dll)
        Menggunakan motion detection dan frame analysis
        
        Args:
            frame: Current frame
            motion_history: Previous frame untuk comparison
            
        Returns:
            dict: Activity detections
        """
        activities = {}
        
        # Convert to grayscale untuk motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Deteksi smoke (area yang sangat terang/cerah)
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        smoke_area = cv2.countNonZero(binary)
        if smoke_area > (frame.shape[0] * frame.shape[1] * 0.15):  # 15% dari frame
            activities['smoke_detected'] = True
        
        # Deteksi motion (untuk fall detection)
        if motion_history is not None:
            diff = cv2.absdiff(gray_blurred, motion_history)
            _, motion_mask = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
            motion_area = cv2.countNonZero(motion_mask)
            if motion_area > (frame.shape[0] * frame.shape[1] * 0.3):
                activities['high_motion'] = True
        
        return activities
    
    def detect_helmet_violation(self, detections):
        """
        Deteksi pekerja tanpa helmet (safety violation)
        
        Args:
            detections: List of detections from detect_objects
            
        Returns:
            dict: Violation info
        """
        violations = {
            'no_helmet': [],
            'no_safety_jacket': [],
            'unsafe_count': 0
        }
        
        persons = [d for d in detections if 'person' in d['class'].lower()]
        helmets = [d for d in detections if 'helmet' in d['class'].lower()]
        jackets = [d for d in detections if 'jacket' in d['class'].lower() or 'vest' in d['class'].lower()]
        
        # Check if persons have helmets
        for person in persons:
            px1, py1, px2, py2 = person['bbox']
            person_area = person['area']
            
            # Check helmet above person (top 40% of person)
            has_helmet = False
            for helmet in helmets:
                hx1, hy1, hx2, hy2 = helmet['bbox']
                # Helmet should be above person
                if (hy2 > py1 and hy1 < (py1 + (py2 - py1) * 0.4) and
                    hx1 < px2 and hx2 > px1):
                    has_helmet = True
                    break
            
            if not has_helmet:
                violations['no_helmet'].append(person['bbox'])
                violations['unsafe_count'] += 1
        
        return violations
    
    def detect_intrusion_crowd(self, detections):
        """
        Deteksi intrusion (orang yang tidak seharusnya ada) dan crowd gathering
        
        Args:
            detections: List of detections
            
        Returns:
            dict: Crowd info
        """
        persons = [d for d in detections if 'person' in d['class'].lower()]
        
        crowd_info = {
            'person_count': len(persons),
            'crowd_detected': len(persons) > 5,  # >5 orang = crowd
            'crowd_area': None,
            'intrusion_risk': len(persons) > 10
        }
        
        # Calculate center of crowd
        if len(persons) > 0:
            centers = []
            for person in persons:
                x1, y1, x2, y2 = person['bbox']
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                centers.append((cx, cy))
            
            avg_x = sum(c[0] for c in centers) // len(centers)
            avg_y = sum(c[1] for c in centers) // len(centers)
            crowd_info['crowd_area'] = (avg_x, avg_y)
        
        return crowd_info
    
    def detect_weapon_intrusion(self, detections):
        """
        Deteksi pembawa senjata / benda berbahaya
        
        Args:
            detections: List of detections
            
        Returns:
            bool: True jika ada weapon terdeteksi
        """
        weapons = [d for d in detections if 'weapon' in d['class'].lower() or 
                  'knife' in d['class'].lower() or 'gun' in d['class'].lower()]
        
        return len(weapons) > 0
    
    def generate_report(self, detections, activities, violations, crowd, has_weapon):
        """
        Generate comprehensive detection report
        
        Args:
            detections: Object detections
            activities: Activity detections
            violations: Safety violations
            crowd: Crowd info
            has_weapon: Weapon detection flag
            
        Returns:
            dict: Comprehensive report
        """
        report = {
            'timestamp': time.time(),
            'objects_detected': {d['class']: f"{d['confidence']:.2f}" for d in detections},
            'safety_violations': {
                'no_helmet': len(violations['no_helmet']),
                'no_jacket': len(violations['no_safety_jacket']),
            },
            'activities': activities,
            'crowd_status': crowd,
            'weapon_alert': has_weapon,
            'total_persons': crowd['person_count'],
        }
        
        return report
    
    def _get_color_by_class(self, class_name):
        """Get bounding box color by class name"""
        class_name_lower = class_name.lower()
        
        if 'helmet' in class_name_lower:
            return (0, 255, 0)  # Green - safe
        elif 'person' in class_name_lower:
            return (255, 0, 0)  # Blue
        elif 'weapon' in class_name_lower or 'gun' in class_name_lower:
            return (0, 0, 255)  # Red - danger
        elif 'smoke' in class_name_lower:
            return (0, 165, 255)  # Orange
        else:
            return (255, 255, 0)  # Cyan
    
    def add_alert_overlay(self, frame, report):
        """
        Add alert overlay to frame
        
        Args:
            frame: Input frame
            report: Detection report
            
        Returns:
            frame: Annotated frame with alerts
        """
        height, width = frame.shape[:2]
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        
        # Alert background
        alerts = []
        
        if report['safety_violations']['no_helmet'] > 0:
            alerts.append(f"⚠️  NO HELMET: {report['safety_violations']['no_helmet']}")
        
        if report['weapon_alert']:
            alerts.append("🚨 WEAPON DETECTED!")
        
        if report['crowd_status']['crowd_detected']:
            alerts.append(f"👥 CROWD: {report['crowd_status']['person_count']} persons")
        
        if report['crowd_status']['intrusion_risk']:
            alerts.append("🚨 INTRUSION RISK!")
        
        if report['activities'].get('smoke_detected'):
            alerts.append("🔥 SMOKE DETECTED!")
        
        # Draw alerts
        if alerts:
            cv2.rectangle(overlay, (10, 10), (width - 10, 10 + len(alerts) * 25 + 10),
                         (0, 0, 0), -1)
            cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
            
            for i, alert in enumerate(alerts):
                y = 30 + i * 25
                cv2.putText(frame, alert, (20, y),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Add timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (width - 250, height - 10),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def add_info_overlay(self, frame, crowd_info, fps=0):
        """
        Add information overlay
        
        Args:
            frame: Input frame
            crowd_info: Crowd detection info
            fps: Frames per second
            
        Returns:
            frame: Annotated frame
        """
        height, width = frame.shape[:2]
        
        # Info box
        info = [
            f"Persons: {crowd_info['person_count']}",
            f"FPS: {fps:.1f}",
        ]
        
        if crowd_info['crowd_detected']:
            info.append(f"CROWD MODE: {crowd_info['person_count']} detected")
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 10 + len(info) * 25 + 10),
                     (0, 0, 0), -1)
        cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
        
        # Text
        for i, line in enumerate(info):
            y = 30 + i * 25
            cv2.putText(frame, line, (20, y),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        return frame
