"""
Human Detector Module
Menggunakan YOLOv8 untuk mendeteksi manusia dalam frame video
"""

import cv2
import numpy as np
import logging
from ultralytics import YOLO
from datetime import datetime

class HumanDetector:
    """
    Kelas untuk mendeteksi manusia menggunakan YOLOv8
    """
    
    def __init__(self, model_path="models/yolov8n.pt", conf_threshold=0.5):
        """
        Inisialisasi detector
        
        Args:
            model_path (str): Path ke model YOLOv8
            conf_threshold (float): Confidence threshold untuk deteksi (0-1)
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = None
        
        # Class ID untuk 'person' dalam COCO dataset
        self.person_class_id = 0
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Statistik
        self.total_detections = 0
        self.frame_count = 0
        
    def load_model(self):
        """
        Load model YOLOv8
        
        Returns:
            bool: True jika berhasil load model
        """
        try:
            self.logger.info(f"Loading model dari {self.model_path}...")
            self.model = YOLO(self.model_path)
            self.logger.info("Model berhasil di-load")
            return True
        except Exception as e:
            self.logger.error(f"Error saat loading model: {str(e)}")
            return False
    
    def detect_humans(self, frame):
        """
        Deteksi manusia dalam frame
        
        Args:
            frame: Frame dari video (numpy array)
            
        Returns:
            tuple: (annotated_frame, detections, human_count)
                - annotated_frame: Frame dengan bounding box
                - detections: List of detection dictionaries
                - human_count: Jumlah manusia terdeteksi
        """
        if self.model is None:
            self.logger.error("Model belum di-load!")
            return frame, [], 0
        
        try:
            # Jalankan inference - HANYA DETECT PERSON (class 0)
            results = self.model(frame, conf=self.conf_threshold, classes=[0], verbose=False)
            
            # Dapatkan hasil deteksi
            detections = []
            human_count = 0
            
            # Process hasil
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Ambil class ID
                    class_id = int(box.cls[0])
                    
                    # Filter hanya class 'person' (class_id = 0)
                    if class_id == self.person_class_id:
                        # Dapatkan koordinat bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': conf,
                            'class': 'person'
                        }
                        detections.append(detection)
                        human_count += 1
            
            # Gambar bounding boxes
            annotated_frame = self.draw_detections(frame.copy(), detections)
            
            # Update statistik
            self.frame_count += 1
            self.total_detections += human_count
            
            return annotated_frame, detections, human_count
            
        except Exception as e:
            self.logger.error(f"Error saat deteksi: {str(e)}")
            return frame, [], 0
    
    def draw_detections(self, frame, detections):
        """
        Gambar bounding boxes pada frame
        
        Args:
            frame: Frame video
            detections: List deteksi
            
        Returns:
            Frame dengan bounding boxes
        """
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            
            # Warna untuk bounding box (BGR format) - Hijau
            color = (0, 255, 0)
            thickness = 2
            
            # Gambar rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Tambahkan label
            label = f"Person {conf:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            # Background untuk text
            cv2.rectangle(frame, 
                         (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1),
                         color, -1)
            
            # Text
            cv2.putText(frame, label, 
                       (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 0, 0), 2)
        
        return frame
    
    def add_info_overlay(self, frame, human_count, fps=0):
        """
        Tambahkan overlay informasi pada frame
        
        Args:
            frame: Frame video
            human_count: Jumlah manusia terdeteksi
            fps: Frame per second
            
        Returns:
            Frame dengan overlay
        """
        height, width = frame.shape[:2]
        
        # Background semi-transparan untuk info
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 120), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Informasi
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info_lines = [
            f"Timestamp: {timestamp}",
            f"Humans Detected: {human_count}",
            f"FPS: {fps:.1f}",
            f"Total Frames: {self.frame_count}"
        ]
        
        y_offset = 30
        for line in info_lines:
            cv2.putText(frame, line, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y_offset += 25
        
        return frame
    
    def get_statistics(self):
        """
        Dapatkan statistik deteksi
        
        Returns:
            dict: Statistik deteksi
        """
        avg_detections = self.total_detections / self.frame_count if self.frame_count > 0 else 0
        
        return {
            'total_frames': self.frame_count,
            'total_detections': self.total_detections,
            'average_detections_per_frame': avg_detections
        }
    
    def reset_statistics(self):
        """
        Reset statistik
        """
        self.total_detections = 0
        self.frame_count = 0
        self.logger.info("Statistik di-reset")
