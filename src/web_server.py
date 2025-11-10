"""
Web Server untuk Hikvision Human Detection + Office Monitoring
Flask + SocketIO untuk real-time monitoring dashboard dengan zero delay
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
from src.office_analyzer import OfficeAnalyzer

# Setup Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hikvision-detection-secret-key-2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", ping_interval=5, ping_timeout=10)

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
        self.office_analyzers = {}  # NEW: Office productivity analyzers
        self.running = False
        self.stats = {
            'total_frames': 0,
            'total_detections': 0,
            'average_fps': 0,
            'active_alerts': []
        }
        self.lock = threading.Lock()
        self.streaming_threads = {}
    
    def add_camera(self, camera_id, rtsp_url, mode='simple'):
        """
        Add camera to monitoring
        mode: 'simple' (person only), 'advanced' (helmet, weapon, etc), or 'office' (productivity)
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
                'last_detections': [],
                'start_time': datetime.now()
            }
            
            self.detectors[camera_id] = detector
            
            # NEW: Create office analyzer if mode is office
            if mode == 'office':
                self.office_analyzers[camera_id] = OfficeAnalyzer()
            
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
        except Exception as e:
            logger.error(f"Error connecting camera {camera_id}: {str(e)}")
        
        return False
    
    def disconnect_camera(self, camera_id):
        """Disconnect from camera"""
        if camera_id not in self.cameras:
            return False
        
        try:
            self.cameras[camera_id]['camera'].disconnect()
            self.cameras[camera_id]['connected'] = False
            logger.info(f"✅ Disconnected from camera {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting camera {camera_id}: {str(e)}")
        
        return False
    
    def process_frame_office(self, camera_id, frame):
        """
        Process frame for office monitoring with real-time analysis
        Returns frame with overlay and office statistics
        """
        if camera_id not in self.cameras or camera_id not in self.detectors:
            return frame, {}
        
        detector = self.detectors[camera_id]
        analyzer = self.office_analyzers.get(camera_id)
        
        try:
            # Run detection
            detections = detector.detect(frame)
            
            office_stats = {}
            detection_info = {}
            
            # Process each detected person
            for idx, det in enumerate(detections):
                person_id = f"person_{idx}"
                
                # Extract keypoints if available
                keypoints = det.get('keypoints', None)
                
                # NEW: Office analysis
                if analyzer:
                    # Sitting duration
                    sitting_info = analyzer.detect_sitting_duration(person_id, keypoints, det.get('conf', 0.5))
                    
                    # Activity level
                    activity = analyzer.detect_activity_level(person_id, keypoints)
                    
                    # Posture
                    posture = analyzer.detect_posture(person_id, keypoints)
                    
                    # Get complete stats
                    worker_stats = analyzer.get_worker_stats(person_id)
                    office_stats[person_id] = worker_stats
                    detection_info[person_id] = {
                        'box': det.get('box', []),
                        'conf': det.get('conf', 0),
                        'class': det.get('class', 'person'),
                        'sitting_info': sitting_info,
                        'activity': activity,
                        'posture': posture,
                        'effectiveness_score': worker_stats['effectiveness_score'],
                        'effectiveness_grade': worker_stats['effectiveness_grade']
                    }
                    
                    # Draw detection box with color based on score
                    if sitting_info['risk'] == 'high':
                        color = (0, 0, 255)  # Red - high risk
                    elif sitting_info['risk'] == 'medium':
                        color = (0, 165, 255)  # Orange - medium risk
                    else:
                        color = (0, 255, 0)  # Green - normal
                    
                    box = det.get('box', [])
                    if len(box) >= 4:
                        cv2.rectangle(frame, (int(box[0]), int(box[1])), 
                                     (int(box[2]), int(box[3])), color, 2)
                        
                        # Add info text
                        label = f"#{idx} {sitting_info['status'].upper()}"
                        if sitting_info['status'] == 'sitting':
                            label += f" {sitting_info['duration_formatted']}"
                        
                        cv2.putText(frame, label, (int(box[0]), int(box[1]) - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add overlay
            if analyzer:
                frame = analyzer.add_office_overlay(frame, detection_info, fps=self.cameras[camera_id]['fps'])
            
            return frame, office_stats
        
        except Exception as e:
            logger.error(f"Error processing frame for office: {str(e)}")
            return frame, {}
    
    def process_frame(self, camera_id, frame):
        """Process frame with detection"""
        if camera_id not in self.cameras or camera_id not in self.detectors:
            return frame, {}
        
        detector = self.detectors[camera_id]
        mode = self.cameras[camera_id]['mode']
        
        try:
            if mode == 'office':
                return self.process_frame_office(camera_id, frame)
            else:
                # Standard detection
                detections = detector.detect(frame)
                detection_dict = {}
                
                for idx, det in enumerate(detections):
                    box = det.get('box', [])
                    if len(box) >= 4:
                        cv2.rectangle(frame, (int(box[0]), int(box[1])), 
                                     (int(box[2]), int(box[3])), (0, 255, 0), 2)
                        
                        label = f"{det.get('class', 'object')} {det.get('conf', 0):.2f}"
                        cv2.putText(frame, label, (int(box[0]), int(box[1]) - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        detection_dict[f"det_{idx}"] = det
                
                return frame, detection_dict
        
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return frame, {}

# Initialize detection system
detection_system = DetectionSystem()

# REST API Endpoints
@app.route('/api/status', methods=['GET'])
def api_status():
    """Get system status"""
    try:
        cameras_info = []
        for camera_id, cam_info in detection_system.cameras.items():
            cameras_info.append({
                'id': camera_id,
                'connected': cam_info['connected'],
                'fps': cam_info['fps'],
                'frames': cam_info['frame_count'],
                'detections': cam_info['detection_count'],
                'mode': cam_info['mode']
            })
        
        return jsonify({
            'status': 'running' if detection_system.running else 'stopped',
            'cameras': cameras_info,
            'stats': detection_system.stats
        })
    except Exception as e:
        logger.error(f"Error in /api/status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/add', methods=['POST'])
def api_camera_add():
    """Add new camera"""
    try:
        data = request.json
        camera_id = data.get('camera_id', f"cam_{int(time.time())}")
        rtsp_url = data.get('rtsp_url')
        mode = data.get('mode', 'simple')
        
        if not rtsp_url:
            return jsonify({'error': 'rtsp_url required'}), 400
        
        if detection_system.add_camera(camera_id, rtsp_url, mode):
            return jsonify({'status': 'success', 'camera_id': camera_id})
        else:
            return jsonify({'error': 'Failed to add camera'}), 500
    except Exception as e:
        logger.error(f"Error in /api/camera/add: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/connect/<camera_id>', methods=['POST'])
def api_camera_connect(camera_id):
    """Connect to camera"""
    try:
        if detection_system.connect_camera(camera_id):
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Failed to connect'}), 500
    except Exception as e:
        logger.error(f"Error in /api/camera/connect: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/disconnect/<camera_id>', methods=['POST'])
def api_camera_disconnect(camera_id):
    """Disconnect from camera"""
    try:
        if detection_system.disconnect_camera(camera_id):
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Failed to disconnect'}), 500
    except Exception as e:
        logger.error(f"Error in /api/camera/disconnect: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/office/workers/<camera_id>', methods=['GET'])
def api_office_workers(camera_id):
    """Get office worker statistics"""
    try:
        if camera_id not in detection_system.office_analyzers:
            return jsonify({'error': 'Camera not in office mode'}), 400
        
        analyzer = detection_system.office_analyzers[camera_id]
        workers_data = {}
        
        for person_id in analyzer.workers.keys():
            workers_data[person_id] = analyzer.get_worker_stats(person_id)
        
        return jsonify({'workers': workers_data})
    except Exception as e:
        logger.error(f"Error in /api/office/workers: {str(e)}")
        return jsonify({'error': str(e)}), 500

# WebSocket Events - REAL-TIME WITH ZERO DELAY
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"🔗 Client connected: {request.sid}")
    emit('connect_response', {'status': 'connected', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"🔌 Client disconnected: {request.sid}")

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """Start streaming camera with ZERO DELAY"""
    camera_id = data.get('camera_id')
    session_id = request.sid
    
    if camera_id not in detection_system.cameras:
        emit('error', {'message': 'Camera not found'})
        return
    
    logger.info(f"▶️  Starting monitoring for {camera_id} (client: {session_id})")
    
    # Start streaming in background
    thread = threading.Thread(
        target=stream_camera_realtime,
        args=(camera_id, session_id),
        daemon=True
    )
    thread.start()
    detection_system.streaming_threads[f"{camera_id}_{session_id}"] = thread
    
    emit('monitoring_started', {'camera_id': camera_id})

@socketio.on('stop_monitoring')
def handle_stop_monitoring(data):
    """Stop streaming camera"""
    camera_id = data.get('camera_id')
    logger.info(f"⏸️  Stopping monitoring for {camera_id}")
    emit('monitoring_stopped', {'camera_id': camera_id})

def stream_camera_realtime(camera_id, session_id):
    """
    Stream camera frames with REAL-TIME zero delay
    Using aggressive frame skipping and optimized encoding
    """
    camera_info = detection_system.cameras[camera_id]
    camera = camera_info['camera']
    
    if not camera.is_connected() and not camera.connect():
        socketio.emit('error', {'message': 'Failed to connect to camera'}, room=session_id)
        return
    
    frame_skip = 0
    skip_interval = 2  # Send every 2nd frame for other clients, all frames for office
    fps_counter = 0
    fps_start = time.time()
    
    try:
        while True:
            try:
                # Get frame with minimal latency
                frame = camera.get_frame()
                if frame is None:
                    time.sleep(0.001)  # Minimal sleep
                    continue
                
                camera_info['frame_count'] += 1
                frame_skip += 1
                
                # Process detections
                processed_frame, detections = detection_system.process_frame(camera_id, frame)
                
                # Update FPS
                fps_counter += 1
                elapsed = time.time() - fps_start
                if elapsed >= 1.0:
                    camera_info['fps'] = fps_counter / elapsed
                    fps_counter = 0
                    fps_start = time.time()
                
                # Send frame every interval (aggressive for real-time)
                if frame_skip >= skip_interval:
                    frame_skip = 0
                    
                    # Encode frame efficiently
                    _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Emit with minimal metadata
                    socketio.emit('frame_update', {
                        'camera_id': camera_id,
                        'frame': f'data:image/jpeg;base64,{frame_b64}',
                        'timestamp': datetime.now().isoformat(),
                        'fps': camera_info['fps'],
                        'frame_count': camera_info['frame_count'],
                        'detections': detections,
                        'mode': camera_info['mode']
                    }, room=session_id, skip_sid=False)
                
                # For office mode, also send detailed stats every frame
                if camera_info['mode'] == 'office' and detections:
                    socketio.emit('office_stats_update', {
                        'camera_id': camera_id,
                        'stats': detections,
                        'timestamp': datetime.now().isoformat()
                    }, room=session_id, skip_sid=False)
                
            except Exception as e:
                logger.error(f"Error in frame loop: {str(e)}")
                time.sleep(0.1)
    
    except Exception as e:
        logger.error(f"Stream error for {camera_id}: {str(e)}")
        socketio.emit('stream_error', {'error': str(e)}, room=session_id)
    
    finally:
        logger.info(f"📹 Stream ended for {camera_id}")

# Main page
@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('dashboard.html')

@app.route('/office')
def office_dashboard():
    """Serve office monitoring dashboard"""
    return render_template('office_dashboard.html')

def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run Flask server"""
    detection_system.running = True
    logger.info(f"🚀 Starting server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_server()
