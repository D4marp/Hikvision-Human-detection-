"""
Example Python Client untuk Human Detection API
Testing dan demonstrasi penggunaan API
"""

import requests
import time
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:5000"
CAMERA_ID = "test_camera"
RTSP_URL = "rtsp://admin:Admin123@192.168.1.64:554/Streaming/Channels/102"


def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_api_status():
    """Test 1: Get API status"""
    print_section("Test 1: API Status")
    
    response = requests.get(f"{API_BASE_URL}/api/status")
    if response.status_code == 200:
        data = response.json()
        print("✅ API is running")
        print(f"   Status: {data['status']}")
        print(f"   Cameras: {data['cameras']}")
        print(f"   Model: {data['model']}")
        print(f"   Confidence: {data['conf_threshold']}")
    else:
        print(f"❌ API error: {response.status_code}")
    
    return response.status_code == 200


def test_add_camera():
    """Test 2: Add camera"""
    print_section("Test 2: Add Camera")
    
    payload = {
        "camera_id": CAMERA_ID,
        "rtsp_url": RTSP_URL
    }
    
    response = requests.post(f"{API_BASE_URL}/api/camera/add", json=payload)
    
    if response.status_code == 201:
        print(f"✅ Camera '{CAMERA_ID}' added successfully")
        print(f"   RTSP: {RTSP_URL}")
    else:
        data = response.json()
        print(f"⚠️  {data.get('error', 'Unknown error')}")
    
    return response.status_code == 201


def test_list_cameras():
    """Test 3: List cameras"""
    print_section("Test 3: List Cameras")
    
    response = requests.get(f"{API_BASE_URL}/api/cameras")
    
    if response.status_code == 200:
        data = response.json()
        cameras = data['cameras']
        
        if cameras:
            print(f"✅ Found {len(cameras)} camera(s):")
            for cam in cameras:
                status = "🟢 Running" if cam['running'] else "🔴 Stopped"
                print(f"\n   Camera: {cam['id']}")
                print(f"   Status: {status}")
                print(f"   URL: {cam['url']}")
                print(f"   Humans: {cam['human_count']}")
                print(f"   FPS: {cam['fps']}")
        else:
            print("⚠️  No cameras found")
    else:
        print(f"❌ Error: {response.status_code}")


def test_get_detection():
    """Test 4: Get detection data"""
    print_section("Test 4: Get Detection Data")
    
    print("Polling detection data for 10 seconds...")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        for i in range(10):
            response = requests.get(f"{API_BASE_URL}/api/camera/{CAMERA_ID}/detection")
            
            if response.status_code == 200:
                data = response.json()
                count = data['human_count']
                fps = data['fps']
                timestamp = datetime.fromisoformat(data['timestamp']).strftime('%H:%M:%S')
                
                if count > 0:
                    print(f"[{timestamp}] 🚨 {count} orang terdeteksi | FPS: {fps}")
                    
                    # Show detection details
                    for idx, det in enumerate(data['detections'], 1):
                        conf = det['confidence']
                        bbox = det['bbox']
                        print(f"           Person {idx}: Confidence {conf:.2f} at {bbox}")
                else:
                    print(f"[{timestamp}] ✓ No detection | FPS: {fps}")
            else:
                print(f"❌ Error: {response.status_code}")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Polling stopped by user")


def test_get_snapshot():
    """Test 5: Get snapshot"""
    print_section("Test 5: Get Snapshot")
    
    response = requests.get(f"{API_BASE_URL}/api/camera/{CAMERA_ID}/snapshot")
    
    if response.status_code == 200:
        # Save snapshot
        filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Snapshot saved: {filename}")
        print(f"   Size: {len(response.content)} bytes")
    else:
        print(f"❌ Error: {response.status_code}")


def test_configure_webhook():
    """Test 6: Configure webhook"""
    print_section("Test 6: Configure Webhook")
    
    payload = {
        "enabled": True,
        "url": "http://localhost:1880/webhook/human-detection"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/webhook/configure", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Webhook configured")
        print(f"   Enabled: {data['enabled']}")
        print(f"   URL: {data['url']}")
    else:
        print(f"❌ Error: {response.status_code}")


def test_configure_milesight():
    """Test 7: Configure Milesight"""
    print_section("Test 7: Configure Milesight")
    
    payload = {
        "enabled": True,
        "url": "http://192.168.1.100:8080/api/data"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/milesight/configure", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Milesight configured")
        print(f"   Enabled: {data['enabled']}")
        print(f"   URL: {data['url']}")
    else:
        print(f"❌ Error: {response.status_code}")


def test_remove_camera():
    """Test 8: Remove camera"""
    print_section("Test 8: Remove Camera")
    
    response = requests.delete(f"{API_BASE_URL}/api/camera/{CAMERA_ID}")
    
    if response.status_code == 200:
        print(f"✅ Camera '{CAMERA_ID}' removed successfully")
    else:
        data = response.json()
        print(f"❌ Error: {data.get('error', 'Unknown error')}")


def print_menu():
    """Print test menu"""
    print("\n" + "="*60)
    print("  Human Detection API - Test Client")
    print("="*60)
    print("\nAvailable Tests:")
    print("  1. API Status")
    print("  2. Add Camera")
    print("  3. List Cameras")
    print("  4. Get Detection Data (10s polling)")
    print("  5. Get Snapshot")
    print("  6. Configure Webhook (Node-RED)")
    print("  7. Configure Milesight")
    print("  8. Remove Camera")
    print("  9. Run All Tests")
    print("  0. Exit")
    print("="*60)


def run_all_tests():
    """Run all tests in sequence"""
    tests = [
        ("API Status", test_api_status),
        ("Add Camera", test_add_camera),
        ("List Cameras", test_list_cameras),
        ("Get Detection", test_get_detection),
        ("Get Snapshot", test_get_snapshot),
        ("Configure Webhook", test_configure_webhook),
        ("Configure Milesight", test_configure_milesight),
        ("List Cameras", test_list_cameras),
        ("Remove Camera", test_remove_camera),
    ]
    
    print("\n" + "="*60)
    print("  Running All Tests")
    print("="*60)
    
    for name, test_func in tests:
        try:
            test_func()
            time.sleep(1)  # Delay between tests
        except Exception as e:
            print(f"\n❌ Test '{name}' failed: {e}")
    
    print("\n" + "="*60)
    print("  All Tests Completed")
    print("="*60)


def main():
    """Main function"""
    
    # Check if API is reachable
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        if response.status_code != 200:
            print("\n❌ API server is not running!")
            print(f"   Please start: python src/api_server.py")
            print(f"   Or run: ./run_api_server.sh\n")
            return
    except requests.exceptions.RequestException:
        print("\n❌ Cannot connect to API server!")
        print(f"   URL: {API_BASE_URL}")
        print(f"   Please start: python src/api_server.py")
        print(f"   Or run: ./run_api_server.sh\n")
        return
    
    # Menu loop
    while True:
        print_menu()
        choice = input("\nSelect test (0-9): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!\n")
            break
        elif choice == '1':
            test_api_status()
        elif choice == '2':
            test_add_camera()
        elif choice == '3':
            test_list_cameras()
        elif choice == '4':
            test_get_detection()
        elif choice == '5':
            test_get_snapshot()
        elif choice == '6':
            test_configure_webhook()
        elif choice == '7':
            test_configure_milesight()
        elif choice == '8':
            test_remove_camera()
        elif choice == '9':
            run_all_tests()
        else:
            print("\n❌ Invalid choice. Please select 0-9.")
        
        input("\nPress Enter to continue...")


if __name__ == '__main__':
    main()
