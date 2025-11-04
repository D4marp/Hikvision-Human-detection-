"""
REST API Server for Human Detection System
Integration dengan Node-RED, Milesight, dan sistem IoT lainnya
"""

from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
import cv2
import json
import logging
import threading
import time
from datetime import datetime
import requests
from queue import Queue
import base64

from detector import HumanDetector
from camera_stream import HikvisionCamera

app = Flask(__name__)
CORS(app)  # Enable CORS untuk akses dari Node-RED

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
detector = None
cameras = {}  # Dictionary untuk multiple cameras
detection_data = {}  # Store detection data per camera
webhook_url = None  # URL untuk Node-RED webhook
event_queue = Queue()  # Queue untuk events

# Configuration
CONFIG = {
    'model_path': 'models/yolov8n.pt',
    'conf_threshold': 0.5,
    'webhook_enabled': False,
    'webhook_url': None,
    'milesight_enabled': False,
    'milesight_url': None,
    'detection_interval': 1.0,  # Send update setiap 1 detik
}


class CameraStream:
    """Class untuk handle camera streaming dengan detection"""
    
    def __init__(self, camera_id, rtsp_url, detector):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.detector = detector
        self.camera = HikvisionCamera(rtsp_url)
        self.is_running = False
        self.current_frame = None
        self.detection_count = 0
        self.last_detections = []
        self.fps = 0
        self.last_update = time.time()
        self.frame_count = 0
        
    def start(self):
        """Start camera streaming"""
        if self.camera.connect():
            self.is_running = True
            thread = threading.Thread(target=self._process_stream, daemon=True)
            thread.start()
            logger.info(f"Camera {self.camera_id} started")
            return True
        return False
    
    def stop(self):
        """Stop camera streaming"""
        self.is_running = False
        self.camera.disconnect()
        logger.info(f"Camera {self.camera_id} stopped")
    
    def _process_stream(self):
        """Process video stream dengan detection"""
        fps_start = time.time()
        frame_counter = 0
        
        while self.is_running:
            ret, frame = self.camera.read_frame()
            
            if not ret or frame is None:
                time.sleep(0.1)
                continue
            
            # Run detection
            annotated_frame, detections, count = self.detector.detect_humans(frame)
            
            # Update data
            self.current_frame = annotated_frame
            self.detection_count = count
            self.last_detections = detections
            
            # Calculate FPS
            frame_counter += 1
            if time.time() - fps_start >= 1.0:
                self.fps = frame_counter
                frame_counter = 0
                fps_start = time.time()
            
            # Send webhook/event jika ada detection
            if count > 0 and time.time() - self.last_update >= CONFIG['detection_interval']:
                self._send_detection_event(count, detections)
                self.last_update = time.time()
            
            time.sleep(0.03)  # ~30 FPS max
    
    def _send_detection_event(self, count, detections):
        """Send detection event ke webhook/queue"""
        event = {
            'camera_id': self.camera_id,
            'timestamp': datetime.now().isoformat(),
            'human_count': count,
            'detections': detections,
            'fps': self.fps
        }
        
        # Add to event queue
        event_queue.put(event)
        
        # Send to webhook (Node-RED)
        if CONFIG['webhook_enabled'] and CONFIG['webhook_url']:
            try:
                requests.post(CONFIG['webhook_url'], json=event, timeout=2)
            except Exception as e:
                logger.error(f"Webhook error: {e}")
        
        # Send to Milesight
        if CONFIG['milesight_enabled'] and CONFIG['milesight_url']:
            try:
                milesight_data = self._format_milesight_data(event)
                requests.post(CONFIG['milesight_url'], json=milesight_data, timeout=2)
            except Exception as e:
                logger.error(f"Milesight error: {e}")
    
    def _format_milesight_data(self, event):
        """Format data untuk Milesight IoT gateway"""
        return {
            'deviceId': f'camera_{self.camera_id}',
            'timestamp': event['timestamp'],
            'data': {
                'human_count': event['human_count'],
                'fps': event['fps']
            },
            'type': 'human_detection'
        }
    
    def get_frame_jpeg(self):
        """Get current frame sebagai JPEG bytes"""
        if self.current_frame is None:
            return None
        
        ret, buffer = cv2.imencode('.jpg', self.current_frame, 
                                   [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            return buffer.tobytes()
        return None


# ========================================
# API ENDPOINTS
# ========================================

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'name': 'Human Detection API',
        'version': '1.0',
        'description': 'REST API for Hikvision Human Detection System',
        'endpoints': {
            'GET /': 'API documentation',
            'GET /api/status': 'System status',
            'GET /api/cameras': 'List all cameras',
            'POST /api/camera/add': 'Add new camera',
            'DELETE /api/camera/<id>': 'Remove camera',
            'GET /api/camera/<id>/stream': 'MJPEG video stream',
            'GET /api/camera/<id>/detection': 'Detection data',
            'GET /api/camera/<id>/snapshot': 'Single frame JPEG',
            'POST /api/webhook/configure': 'Configure webhook (Node-RED)',
            'POST /api/milesight/configure': 'Configure Milesight',
            'GET /api/events': 'Server-Sent Events stream',
            'GET /api/events/latest': 'Get latest events',
        },
        'integration': {
            'node_red': 'Use /api/events for real-time data',
            'milesight': 'Configure via /api/milesight/configure',
            'webhook': 'Configure via /api/webhook/configure'
        }
    })


@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'cameras': len(cameras),
        'active_cameras': sum(1 for c in cameras.values() if c.is_running),
        'model': CONFIG['model_path'],
        'confidence_threshold': CONFIG['conf_threshold'],
        'webhook_enabled': CONFIG['webhook_enabled'],
        'milesight_enabled': CONFIG['milesight_enabled']
    })


@app.route('/api/cameras')
def list_cameras():
    """List all cameras"""
    camera_list = []
    for cam_id, cam in cameras.items():
        camera_list.append({
            'id': cam_id,
            'url': cam.rtsp_url,
            'running': cam.is_running,
            'human_count': cam.detection_count,
            'fps': cam.fps
        })
    return jsonify({'cameras': camera_list})


@app.route('/api/camera/add', methods=['POST'])
def add_camera():
    """Add new camera
    
    Body: {
        "camera_id": "cam1",
        "rtsp_url": "rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/102"
    }
    """
    data = request.json
    camera_id = data.get('camera_id')
    rtsp_url = data.get('rtsp_url')
    
    if not camera_id or not rtsp_url:
        return jsonify({'error': 'camera_id and rtsp_url required'}), 400
    
    if camera_id in cameras:
        return jsonify({'error': 'camera already exists'}), 400
    
    # Initialize detector if not exists
    global detector
    if detector is None:
        detector = HumanDetector(CONFIG['model_path'], CONFIG['conf_threshold'])
        detector.load_model()
    
    # Create camera stream
    cam_stream = CameraStream(camera_id, rtsp_url, detector)
    
    if cam_stream.start():
        cameras[camera_id] = cam_stream
        return jsonify({
            'message': 'Camera added successfully',
            'camera_id': camera_id
        }), 201
    else:
        return jsonify({'error': 'Failed to connect camera'}), 500


@app.route('/api/camera/<camera_id>', methods=['DELETE'])
def remove_camera(camera_id):
    """Remove camera"""
    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404
    
    cameras[camera_id].stop()
    del cameras[camera_id]
    
    return jsonify({'message': 'Camera removed successfully'})


@app.route('/api/camera/<camera_id>/stream')
def camera_stream(camera_id):
    """MJPEG video stream untuk display di browser/Node-RED"""
    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404
    
    def generate():
        cam = cameras[camera_id]
        while cam.is_running:
            frame_bytes = cam.get_frame_jpeg()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/camera/<camera_id>/detection')
def camera_detection(camera_id):
    """Get detection data untuk camera"""
    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404
    
    cam = cameras[camera_id]
    return jsonify({
        'camera_id': camera_id,
        'timestamp': datetime.now().isoformat(),
        'human_count': cam.detection_count,
        'detections': cam.last_detections,
        'fps': cam.fps
    })


@app.route('/api/camera/<camera_id>/snapshot')
def camera_snapshot(camera_id):
    """Get single frame sebagai JPEG"""
    if camera_id not in cameras:
        return jsonify({'error': 'Camera not found'}), 404
    
    frame_bytes = cameras[camera_id].get_frame_jpeg()
    if frame_bytes:
        return Response(frame_bytes, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'No frame available'}), 503


@app.route('/api/webhook/configure', methods=['POST'])
def configure_webhook():
    """Configure webhook untuk Node-RED
    
    Body: {
        "enabled": true,
        "url": "http://localhost:1880/webhook/human-detection"
    }
    """
    data = request.json
    CONFIG['webhook_enabled'] = data.get('enabled', False)
    CONFIG['webhook_url'] = data.get('url')
    
    return jsonify({
        'message': 'Webhook configured',
        'enabled': CONFIG['webhook_enabled'],
        'url': CONFIG['webhook_url']
    })


@app.route('/api/milesight/configure', methods=['POST'])
def configure_milesight():
    """Configure Milesight IoT gateway
    
    Body: {
        "enabled": true,
        "url": "http://192.168.1.100:8080/api/data"
    }
    """
    data = request.json
    CONFIG['milesight_enabled'] = data.get('enabled', False)
    CONFIG['milesight_url'] = data.get('url')
    
    return jsonify({
        'message': 'Milesight configured',
        'enabled': CONFIG['milesight_enabled'],
        'url': CONFIG['milesight_url']
    })


@app.route('/api/events')
def events():
    """Server-Sent Events (SSE) stream untuk real-time updates
    
    Gunakan ini di Node-RED dengan http-in node
    """
    def generate():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Stream events
        while True:
            if not event_queue.empty():
                event = event_queue.get()
                yield f"data: {json.dumps(event)}\n\n"
            time.sleep(0.1)
    
    return Response(stream_with_context(generate()),
                    mimetype='text/event-stream')


@app.route('/api/events/latest')
def latest_events():
    """Get latest events (last 10)"""
    events = []
    temp_queue = Queue()
    
    # Get up to 10 events
    while not event_queue.empty() and len(events) < 10:
        event = event_queue.get()
        events.append(event)
        temp_queue.put(event)
    
    # Put back to queue
    while not temp_queue.empty():
        event_queue.put(temp_queue.get())
    
    return jsonify({'events': events})


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get/Update configuration"""
    if request.method == 'POST':
        data = request.json
        CONFIG.update(data)
        return jsonify({'message': 'Configuration updated', 'config': CONFIG})
    else:
        return jsonify(CONFIG)


# ========================================
# MAIN
# ========================================

def main():
    """Start API server"""
    logger.info("Starting Human Detection API Server...")
    
    # Load model
    global detector
    detector = HumanDetector(CONFIG['model_path'], CONFIG['conf_threshold'])
    if not detector.load_model():
        logger.error("Failed to load model!")
        return
    
    # Start server
    logger.info("API Server running on http://0.0.0.0:5000")
    logger.info("Access documentation: http://localhost:5000/")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


if __name__ == '__main__':
    main()
