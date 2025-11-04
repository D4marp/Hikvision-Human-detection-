"""
Multi-Camera System dengan Config File
Lebih mudah untuk manage banyak cameras
"""

import sys
sys.path.append('.')

from src.multi_camera import MultiCameraSystem
from camera_config import get_enabled_cameras, MODEL_CONFIG, validate_config, print_camera_list
import logging

logger = logging.getLogger(__name__)


def main():
    print("\n" + "=" * 60)
    print("MULTI-CAMERA HUMAN DETECTION SYSTEM")
    print("=" * 60)
    
    # Print camera list
    print_camera_list()
    
    # Validate config
    if not validate_config():
        print("\n❌ Please fix configuration errors in camera_config.py")
        return
    
    # Get enabled cameras
    cameras = get_enabled_cameras()
    
    if not cameras:
        print("\n❌ No cameras enabled! Edit camera_config.py to enable cameras.")
        return
    
    print(f"\n✅ Starting system with {len(cameras)} camera(s)...")
    
    try:
        # Initialize system
        system = MultiCameraSystem(
            cameras_config=cameras,
            model_path=MODEL_CONFIG['model_path'],
            conf_threshold=MODEL_CONFIG['conf_threshold']
        )
        
        # Start all cameras
        system.start()
        
        # Wait for initialization
        import time
        time.sleep(3)
        
        print("\n" + "=" * 60)
        print("CONTROLS:")
        print("  q - Quit")
        print("  s - Show statistics")
        print("=" * 60 + "\n")
        
        # Display grid
        system.display_grid()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
    
    finally:
        print("\n🛑 Stopping system...")
        system.stop()
        print("✅ System stopped")


if __name__ == "__main__":
    main()
