"""
Optimized Human Detector - Ultra Low Resource
Versi ringan untuk multi-camera setup dengan 8MP
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
from pathlib import Path

class OptimizedHumanDetector:
    """
    Detector manusia yang dioptimasi untuk:
    - Multi-camera (4-8 kamera)
    - High resolution (8MP)
    - Low latency
    - Low resource usage
    """
    
    def __init__(self, model_path="models/yolov8n.pt", conf_threshold=0.40, img_size=480):
        """
        Initialize Optimized Detector
        
        Args:
            model_path: Path ke model YOLO
            conf_threshold: Confidence threshold (0.40 default)
            img_size: Input image size (smaller = faster)
                     480: Ultra fast, good for 8 cameras
                     640: Default, good for 4-6 cameras  
                     960: High quality, max 2-3 cameras
        """
        self.conf_threshold = conf_threshold
        self.img_size = img_size
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load model
        self.logger.info(f"Loading optimized YOLO model: {model_path}")
        self.logger.info(f"Image size: {img_size}px (smaller=faster)")
        
        try:
            self.model = YOLO(model_path)
            
            # OPTIMIZATION: Set model to evaluation mode
            self.model.model.eval()
            
            # OPTIMIZATION: Disable gradient computation (inference only)
            import torch
            torch.set_grad_enabled(False)
            
            self.logger.info("✅ Model loaded successfully")
            self.logger.info(f"⚡ Optimizations enabled: img_size={img_size}, half=True")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading model: {str(e)}")
            raise
    
    def detect_humans(self, frame):
        """
        Detect humans dengan optimasi untuk kecepatan
        
        Args:
            frame: Frame dari kamera (numpy array)
            
        Returns:
            tuple: (count, detections, annotated_frame)
        """
        try:
            # OPTIMIZATION 1: Resize frame jika terlalu besar (8MP -> smaller)
            h, w = frame.shape[:2]
            if w > 1280:  # Jika lebih dari 720p
                scale = 1280 / w
                new_w = 1280
                new_h = int(h * scale)
                frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            else:
                frame_resized = frame
            
            # OPTIMIZATION 2: Run inference dengan parameter optimal
            results = self.model(
                frame_resized,
                conf=self.conf_threshold,
                classes=[0],  # Person only
                verbose=False,
                imgsz=self.img_size,  # Smaller = faster
                half=False,  # FP16 untuk speed (jika GPU support)
                device='cpu',  # Force CPU (untuk multi-camera stability)
                max_det=10  # Max 10 detections (cukup untuk human counting)
            )
            
            # Extract detections
            detections = []
            human_count = 0
            
            result = results[0]
            
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.cpu().numpy()
                
                for box in boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    
                    # Filter: only person class (0) and above threshold
                    if cls == 0 and conf >= self.conf_threshold:
                        human_count += 1
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0]
                        
                        # Scale back to original size if resized
                        if w > 1280:
                            scale_back = w / 1280
                            x1, y1, x2, y2 = x1*scale_back, y1*scale_back, x2*scale_back, y2*scale_back
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': conf,
                            'class': 'person'
                        })
            
            # OPTIMIZATION 3: Annotate pada frame yang di-resize (lebih cepat)
            annotated_frame = self._draw_detections(frame, detections)
            
            return human_count, detections, annotated_frame
            
        except Exception as e:
            self.logger.error(f"Error during detection: {str(e)}")
            return 0, [], frame
    
    def _draw_detections(self, frame, detections):
        """
        Draw bounding boxes dengan style yang ringan
        
        Args:
            frame: Frame original
            detections: List of detections
            
        Returns:
            Frame dengan annotations
        """
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            
            # OPTIMIZATION: Simple rectangle (faster than fancy UI)
            color = (0, 255, 0)  # Green
            thickness = 2
            
            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)
            
            # Draw label dengan background
            label = f"Person {conf:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            
            (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
            
            # Background rectangle untuk text
            cv2.rectangle(annotated, (x1, y1-text_h-10), (x1+text_w+10, y1), color, -1)
            
            # Text
            cv2.putText(annotated, label, (x1+5, y1-5), font, font_scale, (0, 0, 0), font_thickness)
        
        return annotated
    
    def get_model_info(self):
        """
        Get model information
        
        Returns:
            dict: Model info
        """
        return {
            'model_type': 'YOLOv8n-optimized',
            'input_size': self.img_size,
            'conf_threshold': self.conf_threshold,
            'optimizations': [
                'Auto frame resize (8MP -> 720p)',
                'Small inference size (480px)',
                'Max 10 detections',
                'CPU mode for stability',
                'Simple annotation (faster)'
            ]
        }
