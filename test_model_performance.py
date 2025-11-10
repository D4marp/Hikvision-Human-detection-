"""
Test Performance YOLO Models
Compare speed dan resource usage untuk berbagai model
"""

import cv2
import time
import psutil
import os
from src.detector import HumanDetector
from src.detector_optimized import OptimizedHumanDetector

# Camera RTSP URL
RTSP_URL = "rtsp://admin:Novarion1@10.0.66.29:554/Streaming/Channels/102"

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_detector(detector, name, frames_to_test=30):
    """
    Test detector performance
    
    Args:
        detector: Detector object
        name: Model name
        frames_to_test: Number of frames to test
        
    Returns:
        dict: Performance metrics
    """
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    # Connect to camera
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("❌ Failed to connect to camera")
        return None
    
    print("✅ Connected to camera")
    
    # Warm up (skip first few frames)
    for _ in range(5):
        cap.read()
    
    # Measure initial memory
    mem_start = get_memory_usage()
    print(f"📊 Initial Memory: {mem_start:.1f} MB")
    
    # Test detection
    detection_times = []
    human_counts = []
    
    print(f"\n🔍 Testing {frames_to_test} frames...")
    
    for i in range(frames_to_test):
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️  Failed to read frame {i+1}")
            continue
        
        # Measure detection time
        start_time = time.time()
        count, detections, annotated = detector.detect_humans(frame)
        end_time = time.time()
        
        detection_time = (end_time - start_time) * 1000  # ms
        detection_times.append(detection_time)
        human_counts.append(count)
        
        # Progress indicator
        if (i+1) % 10 == 0:
            avg_time = sum(detection_times[-10:]) / 10
            print(f"  Frame {i+1}/{frames_to_test}: {avg_time:.1f}ms avg")
    
    # Measure final memory
    mem_end = get_memory_usage()
    mem_used = mem_end - mem_start
    
    # Calculate statistics
    avg_time = sum(detection_times) / len(detection_times)
    min_time = min(detection_times)
    max_time = max(detection_times)
    fps = 1000 / avg_time
    
    avg_humans = sum(human_counts) / len(human_counts)
    
    # Cleanup
    cap.release()
    
    # Print results
    print(f"\n📈 RESULTS:")
    print(f"  Average Detection Time: {avg_time:.1f}ms")
    print(f"  Min/Max Time: {min_time:.1f}ms / {max_time:.1f}ms")
    print(f"  FPS: {fps:.1f}")
    print(f"  Memory Used: {mem_used:.1f} MB")
    print(f"  Average Humans: {avg_humans:.1f}")
    
    return {
        'name': name,
        'avg_time_ms': avg_time,
        'min_time_ms': min_time,
        'max_time_ms': max_time,
        'fps': fps,
        'memory_mb': mem_used,
        'avg_humans': avg_humans
    }

def main():
    """Main test function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         YOLO MODEL PERFORMANCE COMPARISON TEST               ║
║         Testing speed & resource usage                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    results = []
    
    # Test 1: Current YOLOv8n (default size 640)
    print("\n[1/3] Testing YOLOv8n - Default (640px)")
    detector1 = HumanDetector(model_path="models/yolov8n.pt", conf_threshold=0.40)
    result1 = test_detector(detector1, "YOLOv8n-640", frames_to_test=30)
    if result1:
        results.append(result1)
    del detector1
    
    # Test 2: Optimized YOLOv8n (size 480 - faster)
    print("\n[2/3] Testing YOLOv8n - Optimized (480px)")
    detector2 = OptimizedHumanDetector(
        model_path="models/yolov8n.pt", 
        conf_threshold=0.40,
        img_size=480
    )
    result2 = test_detector(detector2, "YOLOv8n-480-Optimized", frames_to_test=30)
    if result2:
        results.append(result2)
    del detector2
    
    # Test 3: Ultra Optimized (size 320 - ultra fast)
    print("\n[3/3] Testing YOLOv8n - Ultra Fast (320px)")
    detector3 = OptimizedHumanDetector(
        model_path="models/yolov8n.pt", 
        conf_threshold=0.40,
        img_size=320
    )
    result3 = test_detector(detector3, "YOLOv8n-320-UltraFast", frames_to_test=30)
    if result3:
        results.append(result3)
    del detector3
    
    # Print comparison table
    print(f"\n{'='*80}")
    print(f"PERFORMANCE COMPARISON SUMMARY")
    print(f"{'='*80}")
    print(f"{'Model':<30} {'Speed':<15} {'FPS':<10} {'Memory':<15} {'Humans'}")
    print(f"{'-'*80}")
    
    for r in results:
        print(f"{r['name']:<30} {r['avg_time_ms']:>6.1f}ms      "
              f"{r['fps']:>5.1f}     {r['memory_mb']:>6.1f}MB      "
              f"{r['avg_humans']:>4.1f}")
    
    print(f"{'='*80}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("="*80)
    
    if len(results) >= 2:
        fastest = min(results, key=lambda x: x['avg_time_ms'])
        lightest = min(results, key=lambda x: x['memory_mb'])
        
        print(f"⚡ FASTEST: {fastest['name']} ({fastest['avg_time_ms']:.1f}ms, {fastest['fps']:.1f} FPS)")
        print(f"💾 LIGHTEST: {lightest['name']} ({lightest['memory_mb']:.1f} MB)")
        
        print("\n📋 Use Case Recommendations:")
        print("  • 1-2 cameras (8MP):    YOLOv8n-640 (best accuracy)")
        print("  • 3-4 cameras (8MP):    YOLOv8n-480 (balanced)")
        print("  • 5-8 cameras (2-4MP):  YOLOv8n-320 (ultra fast)")
        print("  • 8+ cameras (2MP):     Consider YOLOv5n (even lighter)")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
