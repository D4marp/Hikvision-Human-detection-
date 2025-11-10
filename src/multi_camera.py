"""
Multi-Camera Human Detection System
Menangani multiple CCTV Hikvision secara bersamaan dengan multi-threading
REAL-TIME optimized with threaded camera streams
"""

import cv2
import numpy as np
import logging
import time
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue

# Import modul lokal dengan absolute import
import sys
sys.path.append(str(Path(__file__).parent))

from detector import HumanDetector
from camera_stream_threaded import ThreadedHikvisionCamera

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(threadName)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/logs/multi_camera.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CameraProcessor:
    """
    Processor untuk 1 camera stream
    Dijalankan di thread terpisah
    """
    
    def __init__(self, camera_config, detector, display_queue=None):
        """
        Args:
            camera_config (dict): Konfigurasi camera
            detector (HumanDetector): Shared detector instance
            display_queue (Queue): Queue untuk hasil display (optional)
        """
        self.config = camera_config
        self.camera_name = camera_config['name']
        self.rtsp_url = camera_config['rtsp_url']
        self.detector = detector
        self.display_queue = display_queue
        
        # Use threaded camera for real-time streaming
        self.camera = ThreadedHikvisionCamera(self.rtsp_url, self.camera_name)
        self.is_running = False
        self.frame_count = 0
        self.detection_count = 0
        
        # Statistics
        self.fps = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        
        logger.info(f"Initialized processor for {self.camera_name}")
    
    def connect(self):
        """Connect to camera using threaded stream"""
        try:
            logger.info(f"{self.camera_name}: Connecting to {self.rtsp_url}")
            return self.camera.connect()
        except Exception as e:
            logger.error(f"{self.camera_name}: Connection error: {str(e)}")
            return False
    
    def process_frame(self):
        """Process single frame from threaded camera"""
        ret, frame = self.camera.read_frame()
        
        if not ret:
            logger.warning(f"{self.camera_name}: Failed to read frame")
            return None
        
        # Run detection
        annotated_frame, detections, human_count = self.detector.detect_humans(frame)
        
        # Update statistics
        self.frame_count += 1
        if human_count > 0:
            self.detection_count += 1
        
        # Calculate FPS
        self.fps_counter += 1
        if self.fps_counter >= 30:
            elapsed = time.time() - self.fps_start_time
            self.fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = time.time()
        
        # Add camera info overlay
        self._add_overlay(annotated_frame, human_count)
        
        # Log detection
        if human_count > 0:
            logger.info(f"{self.camera_name}: Detected {human_count} person(s)")
        
        return annotated_frame
    
    def _add_overlay(self, frame, human_count):
        """Add camera info overlay"""
        height, width = frame.shape[:2]
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (350, 100), (0, 0, 0), -1)
        cv2.addWeighted(frame, 0.6, overlay, 0.4, 0, frame)
        
        # Text
        info = [
            f"Camera: {self.camera_name}",
            f"Humans: {human_count}",
            f"FPS: {self.fps:.1f}",
            f"Frames: {self.frame_count}"
        ]
        
        y = 30
        for line in info:
            cv2.putText(frame, line, (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y += 20
    
    def run(self):
        """Main processing loop"""
        if not self.connect():
            return
        
        self.is_running = True
        logger.info(f"{self.camera_name}: Starting processing loop")
        
        try:
            while self.is_running:
                frame = self.process_frame()
                
                if frame is None:
                    logger.warning(f"{self.camera_name}: Reconnecting...")
                    time.sleep(2)
                    if not self.connect():
                        break
                    continue
                
                # Send to display queue
                if self.display_queue:
                    try:
                        self.display_queue.put((self.camera_name, frame), block=False)
                    except:
                        pass  # Queue full, skip frame
                
        except Exception as e:
            logger.error(f"{self.camera_name}: Error in processing loop: {str(e)}")
        
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop processing"""
        logger.info(f"{self.camera_name}: Stopping...")
        self.is_running = False
    
    def cleanup(self):
        """Cleanup resources"""
        self.camera.disconnect()
        
        logger.info(f"{self.camera_name}: Cleanup complete")
        logger.info(f"{self.camera_name}: Total frames: {self.frame_count}, Detections: {self.detection_count}")
    
    def get_stats(self):
        """Get statistics"""
        return {
            'name': self.camera_name,
            'frames': self.frame_count,
            'detections': self.detection_count,
            'fps': self.fps
        }


class MultiCameraSystem:
    """
    System untuk manage multiple cameras
    """
    
    def __init__(self, cameras_config, model_path='models/yolov8n.pt', conf_threshold=0.5):
        """
        Args:
            cameras_config (list): List of camera configurations
            model_path (str): Path to YOLOv8 model
            conf_threshold (float): Detection confidence threshold
        """
        self.cameras_config = cameras_config
        self.processors = []
        self.threads = []
        self.display_queue = Queue(maxsize=100)
        
        # Shared detector (efisien, model loaded sekali saja)
        logger.info("Loading YOLOv8 model...")
        self.detector = HumanDetector(model_path, conf_threshold)
        if not self.detector.load_model():
            raise Exception("Failed to load model!")
        
        logger.info(f"Initialized multi-camera system with {len(cameras_config)} cameras")
    
    def start(self):
        """Start all camera processors"""
        logger.info("Starting all cameras...")
        
        for cam_config in self.cameras_config:
            processor = CameraProcessor(cam_config, self.detector, self.display_queue)
            thread = threading.Thread(target=processor.run, name=cam_config['name'])
            thread.daemon = True
            
            self.processors.append(processor)
            self.threads.append(thread)
            thread.start()
        
        logger.info("All cameras started")
    
    def display_grid(self):
        """Display cameras in grid layout"""
        num_cameras = len(self.processors)
        
        # Calculate grid size
        if num_cameras <= 1:
            grid_cols, grid_rows = 1, 1
        elif num_cameras <= 4:
            grid_cols, grid_rows = 2, 2
        elif num_cameras <= 6:
            grid_cols, grid_rows = 3, 2
        elif num_cameras <= 9:
            grid_cols, grid_rows = 3, 3
        else:
            grid_cols, grid_rows = 4, 3
        
        cell_width, cell_height = 640, 360  # Size per cell
        grid_width = cell_width * grid_cols
        grid_height = cell_height * grid_rows
        
        # Frame buffer for each camera
        frames_buffer = {}
        
        logger.info(f"Display grid: {grid_cols}x{grid_rows}")
        logger.info("Press 'q' to quit, 's' for statistics")
        
        try:
            while True:
                # Get latest frames from queue
                while not self.display_queue.empty():
                    camera_name, frame = self.display_queue.get()
                    
                    # Resize frame
                    frame_resized = cv2.resize(frame, (cell_width, cell_height))
                    frames_buffer[camera_name] = frame_resized
                
                # Create grid
                grid = self._create_grid(frames_buffer, grid_rows, grid_cols, cell_width, cell_height)
                
                # Display
                cv2.imshow('Multi-Camera Human Detection', grid)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._print_statistics()
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        finally:
            cv2.destroyAllWindows()
    
    def _create_grid(self, frames_buffer, rows, cols, cell_width, cell_height):
        """Create grid from frames"""
        grid_height = cell_height * rows
        grid_width = cell_width * cols
        grid = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)
        
        for idx, (camera_name, frame) in enumerate(frames_buffer.items()):
            if idx >= rows * cols:
                break
            
            row = idx // cols
            col = idx % cols
            
            y1 = row * cell_height
            y2 = y1 + cell_height
            x1 = col * cell_width
            x2 = x1 + cell_width
            
            grid[y1:y2, x1:x2] = frame
        
        return grid
    
    def _print_statistics(self):
        """Print statistics for all cameras"""
        logger.info("=" * 60)
        logger.info("CAMERA STATISTICS")
        logger.info("=" * 60)
        
        for processor in self.processors:
            stats = processor.get_stats()
            logger.info(f"\n{stats['name']}:")
            logger.info(f"  Frames: {stats['frames']}")
            logger.info(f"  Detections: {stats['detections']}")
            logger.info(f"  FPS: {stats['fps']:.1f}")
        
        logger.info("=" * 60)
    
    def stop(self):
        """Stop all cameras"""
        logger.info("Stopping all cameras...")
        
        for processor in self.processors:
            processor.stop()
        
        for thread in self.threads:
            thread.join(timeout=5)
        
        logger.info("All cameras stopped")
        self._print_statistics()


def main():
    """Main function"""
    # ========================================
    # KONFIGURASI CAMERAS
    # Edit sesuai setup Anda!
    # ========================================
    cameras = [
        {
            'name': 'Front Door',
            'rtsp_url': 'rtsp://admin:Admin123@192.168.1.64:554/Streaming/Channels/102'
        },
        {
            'name': 'Back Door',
            'rtsp_url': 'rtsp://admin:Admin123@192.168.1.65:554/Streaming/Channels/102'
        },
        {
            'name': 'Parking Lot',
            'rtsp_url': 'rtsp://admin:Admin123@192.168.1.66:554/Streaming/Channels/102'
        },
        {
            'name': 'Lobby',
            'rtsp_url': 'rtsp://admin:Admin123@192.168.1.67:554/Streaming/Channels/102'
        },
        # Tambahkan camera lain di sini...
    ]
    
    # Untuk testing dengan webcam, uncomment ini:
    # cameras = [
    #     {'name': 'Webcam 1', 'rtsp_url': 0},
    #     {'name': 'Webcam 2', 'rtsp_url': 0},
    # ]
    
    logger.info("=" * 60)
    logger.info("MULTI-CAMERA HUMAN DETECTION SYSTEM")
    logger.info("=" * 60)
    logger.info(f"Total cameras: {len(cameras)}")
    
    try:
        # Initialize system
        system = MultiCameraSystem(
            cameras_config=cameras,
            model_path='models/yolov8n.pt',
            conf_threshold=0.5
        )
        
        # Start all cameras
        system.start()
        
        # Wait for cameras to initialize
        time.sleep(3)
        
        # Display grid
        system.display_grid()
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
    
    finally:
        system.stop()
        logger.info("System shutdown complete")


if __name__ == "__main__":
    main()
