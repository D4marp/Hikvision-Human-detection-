"""
Camera Configuration File
Edit file ini untuk add/remove cameras
"""

# ========================================
# CAMERA LIST
# ========================================

CAMERAS = [
    # Camera 1 - Front Door
    {
        'name': 'Front Door',
        'ip': '192.168.1.64',
        'username': 'admin',
        'password': 'Admin123',
        'channel': 102,  # 101=Main(1080p), 102=Sub(720p), 103=Third(480p)
        'port': 554,
        'enabled': True
    },
    
    # Camera 2 - Back Door
    {
        'name': 'Back Door',
        'ip': '192.168.1.65',
        'username': 'admin',
        'password': 'Admin123',
        'channel': 102,
        'port': 554,
        'enabled': True
    },
    
    # Camera 3 - Parking Lot
    {
        'name': 'Parking Lot',
        'ip': '192.168.1.66',
        'username': 'admin',
        'password': 'Admin123',
        'channel': 102,
        'port': 554,
        'enabled': True
    },
    
    # Camera 4 - Lobby
    {
        'name': 'Lobby',
        'ip': '192.168.1.67',
        'username': 'admin',
        'password': 'Admin123',
        'channel': 102,
        'port': 554,
        'enabled': True
    },
    
    # Camera 5 - Storage Room
    {
        'name': 'Storage Room',
        'ip': '192.168.1.68',
        'username': 'admin',
        'password': 'Admin123',
        'channel': 102,
        'port': 554,
        'enabled': False  # Disabled
    },
    
    # Tambahkan camera lain di sini...
    # Copy format di atas dan ganti IP, name, dll
]


# ========================================
# MODEL CONFIGURATION
# ========================================

MODEL_CONFIG = {
    'model_path': 'models/yolov8n.pt',  # yolov8n, yolov8s, yolov8m, yolov8l
    'conf_threshold': 0.5,               # 0.0 - 1.0 (higher = stricter)
    'device': 'cpu',                     # 'cpu' or 'cuda' (untuk Jetson)
    # NOTE: Model sudah di-set untuk HANYA detect PERSON (class 0)
    # Tidak akan detect mobil, kucing, atau object lain dari COCO dataset
}


# ========================================
# DISPLAY CONFIGURATION
# ========================================

DISPLAY_CONFIG = {
    'grid_cell_width': 640,   # Width per camera cell
    'grid_cell_height': 360,  # Height per camera cell
    'show_fps': True,
    'show_detection_count': True,
    'font_scale': 0.5,
    'font_thickness': 1
}


# ========================================
# LOGGING CONFIGURATION
# ========================================

LOGGING_CONFIG = {
    'level': 'INFO',           # DEBUG, INFO, WARNING, ERROR
    'log_file': 'outputs/logs/multi_camera.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}


# ========================================
# HELPER FUNCTIONS
# ========================================

def get_enabled_cameras():
    """Get list of enabled cameras dengan RTSP URL"""
    enabled = []
    
    for cam in CAMERAS:
        if cam['enabled']:
            rtsp_url = build_rtsp_url(cam)
            enabled.append({
                'name': cam['name'],
                'rtsp_url': rtsp_url
            })
    
    return enabled


def build_rtsp_url(camera):
    """Build RTSP URL from camera config"""
    return f"rtsp://{camera['username']}:{camera['password']}@{camera['ip']}:{camera['port']}/Streaming/Channels/{camera['channel']}"


def get_camera_by_name(name):
    """Get camera config by name"""
    for cam in CAMERAS:
        if cam['name'] == name:
            return cam
    return None


def print_camera_list():
    """Print all cameras"""
    print("\n" + "=" * 60)
    print("CAMERA CONFIGURATION")
    print("=" * 60)
    
    for idx, cam in enumerate(CAMERAS, 1):
        status = "✓ Enabled" if cam['enabled'] else "✗ Disabled"
        rtsp = build_rtsp_url(cam)
        
        print(f"\n{idx}. {cam['name']} [{status}]")
        print(f"   IP: {cam['ip']}")
        print(f"   RTSP: {rtsp}")
    
    print("\n" + "=" * 60)
    print(f"Total: {len(CAMERAS)} cameras")
    print(f"Enabled: {len([c for c in CAMERAS if c['enabled']])} cameras")
    print("=" * 60 + "\n")


# ========================================
# VALIDATION
# ========================================

def validate_config():
    """Validate configuration"""
    errors = []
    
    # Check at least 1 camera enabled
    enabled_count = len([c for c in CAMERAS if c['enabled']])
    if enabled_count == 0:
        errors.append("No cameras enabled!")
    
    # Check duplicate names
    names = [c['name'] for c in CAMERAS]
    if len(names) != len(set(names)):
        errors.append("Duplicate camera names found!")
    
    # Check model file
    import os
    if not os.path.exists(MODEL_CONFIG['model_path']):
        errors.append(f"Model file not found: {MODEL_CONFIG['model_path']}")
    
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration validated successfully!")
    return True


# ========================================
# EXAMPLE USAGE
# ========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CAMERA CONFIGURATION TEST")
    print("=" * 60)
    
    # Print camera list
    print_camera_list()
    
    # Validate
    if validate_config():
        # Get enabled cameras
        enabled = get_enabled_cameras()
        
        print("\nEnabled Cameras for Processing:")
        for cam in enabled:
            print(f"  - {cam['name']}")
            print(f"    {cam['rtsp_url']}")
    
    print("\n" + "=" * 60)
    print("To use this config:")
    print("  python src/multi_camera_with_config.py")
    print("=" * 60 + "\n")
