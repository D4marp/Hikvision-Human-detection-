"""
Web Server untuk Hikvision Human Detection
Flask + SocketIO untuk real-time monitoring dashboard
"""

import cv2
import logging
import threading
import time
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from pathlib import Path
import base64
from io import BytesIO

# Import detection modules
from src.camera_stream_threaded import ThreadedHikvisionCamera
from src.detector import HumanDetector
from src.advanced_detector import AdvancedDetector

# Setup Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hikvision-detection-secret-key-2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/logs/web_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global detection system
class DetectionSystem:
    def __init__(self):
        self.cameras = {}
        self.detectors = {}
        self.running = False
        self.stats = {
            'total_frames': 0,
            'total_detections': 0,
            'average_fps': 0,
            'active_alerts': []
        }
        self.lock = threading.Lock()
    
    def add_camera(self, camera_id, rtsp_url, mode='simple'):
        """
        Add camera to monitoring
        mode: 'simple' (person only) or 'advanced' (helmet, weapon, etc)
        """
        try:
            camera = ThreadedHikvisionCamera(rtsp_url, f"Camera_{camera_id}")
            
            if mode == 'advanced':
                detector = AdvancedDetector(conf_threshold=0.45)
            else:
                detector = HumanDetector(conf_threshold=0.40)
            
            if not detector.load_model():
                logger.error(f"Failed to load detector for {camera_id}")
                return False
            
            self.cameras[camera_id] = {
                'camera': camera,
                'rtsp_url': rtsp_url,
                'connected': False,
                'frame_count': 0,
                'detection_count': 0,
                'fps': 0,
                'last_frame': None,
                'mode': mode,
                'last_detections': []
            }
            
            self.detectors[camera_id] = detector
            logger.info(f"✅ Camera {camera_id} added (mode: {mode})")
            return True
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {str(e)}")
            return False
    
    def connect_camera(self, camera_id):
        """Connect to camera"""
        if camera_id not in self.cameras:
            return False
        
        try:
            if self.cameras[camera_id]['camera'].connect():
                self.cameras[camera_id]['connected'] = True
                logger.info(f"✅ Connected to camera {camera_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error connecting to camera {camera_id}: {str(e)}")
            return False
    
    def get_frame(self, camera_id):
        """Get current frame from camera"""
        if camera_id not in self.cameras:
            return None
        
        try:
            ret, frame = self.cameras[camera_id]['camera'].read_frame()
            if ret and frame is not None:
                return frame
            return None
        except Exception as e:
            logger.error(f"Error getting frame from {camera_id}: {str(e)}")
            return None
    
    def process_frame(self, camera_id, frame):
        """Process frame with detection"""
        if camera_id not in self.detectors:
            return None
        
        try:
            detector = self.detectors[camera_id]
            mode = self.cameras[camera_id]['mode']
            
            if mode == 'advanced':
                detections, annotated = detector.detect_objects(frame)
                # Add more processing for advanced mode
                violations = detector.detect_helmet_violation(detections)
                crowd = detector.detect_intrusion_crowd(detections)
                has_weapon = detector.detect_weapon_intrusion(detections)
                
                result = {
                    'detections': detections,
                    'frame': annotated,
                    'violations': violations,
                    'crowd': crowd,
                    'weapon': has_weapon
                }
            else:
                annotated, detections, human_count = detector.detect_humans(frame)
                result = {
                    'detections': detections,
                    'frame': annotated,
                    'human_count': human_count,
                    'count': human_count
                }
            
            return result
        except Exception as e:
            logger.error(f"Error processing frame from {camera_id}: {str(e)}")
            return None
    
    def frame_to_base64(self, frame):
        """Convert frame to base64 for sending over web"""
        if frame is None:
            return None
        
        try:
            # Resize frame untuk bandwidth efficiency
            frame = cv2.resize(frame, (640, 360))
            
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            img_str = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{img_str}"
        except Exception as e:
            logger.error(f"Error converting frame to base64: {str(e)}")
            return None

# Initialize detection system
detection_system = DetectionSystem()


# ============================================
# WEB ROUTES
# ============================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        with detection_system.lock:
            return jsonify({
                'running': detection_system.running,
                'cameras': {
                    cam_id: {
                        'connected': cam['connected'],
                        'frame_count': cam['frame_count'],
                        'detection_count': cam['detection_count'],
                        'fps': cam['fps'],
                        'mode': cam['mode']
                    }
                    for cam_id, cam in detection_system.cameras.items()
                },
                'stats': detection_system.stats
            })
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/camera/add', methods=['POST'])
def add_camera():
    """Add new camera"""
    try:
        data = request.json
        camera_id = data.get('camera_id')
        rtsp_url = data.get('rtsp_url')
        mode = data.get('mode', 'simple')
        
        if not camera_id or not rtsp_url:
            return jsonify({'error': 'Missing camera_id or rtsp_url'}), 400
        
        if detection_system.add_camera(camera_id, rtsp_url, mode):
            return jsonify({'status': 'success', 'message': f'Camera {camera_id} added'})
        else:
            return jsonify({'error': 'Failed to add camera'}), 500
    
    except Exception as e:
        logger.error(f"Error adding camera: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/camera/connect/<camera_id>', methods=['POST'])
def connect_camera(camera_id):
    """Connect to camera"""
    try:
        if detection_system.connect_camera(camera_id):
            return jsonify({'status': 'success', 'message': f'Connected to {camera_id}'})
        else:
            return jsonify({'error': 'Failed to connect'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/camera/disconnect/<camera_id>', methods=['POST'])
def disconnect_camera(camera_id):
    """Disconnect from camera"""
    try:
        if camera_id in detection_system.cameras:
            detection_system.cameras[camera_id]['camera'].disconnect()
            detection_system.cameras[camera_id]['connected'] = False
            return jsonify({'status': 'success'})
        return jsonify({'error': 'Camera not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# WEBSOCKET EVENTS
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'data': 'Connected to detection server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """Start monitoring specific camera"""
    try:
        camera_id = data.get('camera_id')
        if not camera_id:
            emit('error', {'message': 'Missing camera_id'})
            return
        
        logger.info(f"Starting monitoring for {camera_id}")
        emit('monitoring_started', {'camera_id': camera_id})
        
        # Start streaming thread
        threading.Thread(
            target=stream_camera,
            args=(camera_id, request.sid),
            daemon=True
        ).start()
    
    except Exception as e:
        logger.error(f"Error starting monitoring: {str(e)}")
        emit('error', {'message': str(e)})


@socketio.on('stop_monitoring')
def handle_stop_monitoring(data):
    """Stop monitoring"""
    camera_id = data.get('camera_id')
    logger.info(f"Stopped monitoring for {camera_id}")
    emit('monitoring_stopped', {'camera_id': camera_id})


# ============================================
# STREAMING FUNCTIONS
# ============================================

def stream_camera(camera_id, session_id):
    """Stream camera frames to client"""
    try:
        # Ensure camera is connected
        if not detection_system.cameras[camera_id]['connected']:
            detection_system.connect_camera(camera_id)
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            try:
                # Get frame
                frame = detection_system.get_frame(camera_id)
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Process frame
                result = detection_system.process_frame(camera_id, frame)
                if result is None:
                    continue
                
                # Convert to base64
                frame_b64 = detection_system.frame_to_base64(result['frame'])
                if frame_b64 is None:
                    continue
                
                # Update stats
                with detection_system.lock:
                    detection_system.cameras[camera_id]['last_frame'] = frame_b64
                    detection_system.cameras[camera_id]['frame_count'] += 1
                    frame_count += 1
                    
                    # Calculate FPS
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        fps = frame_count / elapsed
                        detection_system.cameras[camera_id]['fps'] = fps
                
                # Prepare data for emission
                data = {
                    'camera_id': camera_id,
                    'frame': frame_b64,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Add detection info
                if 'count' in result:
                    data['human_count'] = result['count']
                    detection_system.cameras[camera_id]['detection_count'] = result['count']
                
                if 'crowd' in result:
                    data['crowd_info'] = result['crowd']
                
                if 'weapon' in result:
                    data['weapon_alert'] = result['weapon']
                
                if 'violations' in result:
                    data['violations'] = {
                        'no_helmet': result['violations']['no_helmet'],
                        'no_jacket': result['violations']['no_safety_jacket']
                    }
                
                # Emit frame
                socketio.emit('frame_update', data, room=session_id)
                
                # Rate limiting
                time.sleep(0.03)  # ~30 FPS
            
            except Exception as e:
                logger.error(f"Error in streaming loop: {str(e)}")
                time.sleep(0.5)
    
    except Exception as e:
        logger.error(f"Error in stream_camera: {str(e)}")


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("HIKVISION DETECTION WEB SERVER")
    logger.info("="*60)
    logger.info("Starting Flask + SocketIO server...")
    logger.info("Open browser at: http://localhost:5000")
    logger.info("="*60)
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
