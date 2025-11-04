"""
Main Program - Human Detection System
Program utama untuk menjalankan human detection dari kamera Hikvision
"""

import cv2
import logging
import time
import argparse
import sys
from pathlib import Path

# Import modul lokal
from camera_stream import HikvisionCamera
from detector import HumanDetector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/logs/detection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Human Detection System menggunakan YOLOv8 dan Hikvision Camera')
    
    parser.add_argument('--rtsp', type=str,
                       help='RTSP URL dari kamera Hikvision (format: rtsp://username:password@ip:port/Streaming/Channels/101)')
    
    parser.add_argument('--model', type=str, default='models/yolov8n.pt',
                       help='Path ke model YOLOv8 (default: models/yolov8n.pt)')
    
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold untuk deteksi (0-1, default: 0.5)')
    
    parser.add_argument('--save-video', action='store_true',
                       help='Simpan video output ke file')
    
    parser.add_argument('--output', type=str, default='outputs/detection_output.avi',
                       help='Path output video (default: outputs/detection_output.avi)')
    
    parser.add_argument('--webcam', action='store_true',
                       help='Gunakan webcam default (untuk testing tanpa kamera Hikvision)')
    
    parser.add_argument('--video', type=str,
                       help='Path ke file video untuk testing')
    
    return parser.parse_args()


def main():
    """
    Fungsi utama
    """
    # Parse arguments
    args = parse_arguments()
    
    logger.info("="*50)
    logger.info("Human Detection System Starting...")
    logger.info("="*50)
    
    # Inisialisasi detector
    detector = HumanDetector(model_path=args.model, conf_threshold=args.conf)
    
    if not detector.load_model():
        logger.error("Gagal load model. Program dihentikan.")
        return
    
    # Inisialisasi camera/video source
    camera = None
    
    if args.video:
        # Gunakan file video
        logger.info(f"Menggunakan video file: {args.video}")
        rtsp_url = args.video
        camera = HikvisionCamera(rtsp_url, camera_name="Video File")
    elif args.webcam:
        # Gunakan webcam
        logger.info("Menggunakan webcam default")
        rtsp_url = 0  # 0 untuk webcam default
        camera = HikvisionCamera(rtsp_url, camera_name="Webcam")
    elif args.rtsp:
        # Gunakan RTSP stream dari Hikvision
        logger.info(f"Menggunakan RTSP stream dari kamera Hikvision")
        camera = HikvisionCamera(args.rtsp, camera_name="Hikvision DS-2CD2120F-I")
    else:
        # Default: gunakan contoh RTSP URL
        logger.warning("Tidak ada video source yang dipilih!")
        logger.info("Contoh penggunaan:")
        logger.info("  1. Dengan kamera Hikvision:")
        logger.info("     python src/main.py --rtsp rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101")
        logger.info("  2. Dengan webcam:")
        logger.info("     python src/main.py --webcam")
        logger.info("  3. Dengan file video:")
        logger.info("     python src/main.py --video path/to/video.mp4")
        return
    
    # Koneksi ke camera
    if not camera.connect():
        logger.error("Gagal terkoneksi ke camera. Program dihentikan.")
        return
    
    # Setup video writer jika diperlukan
    video_writer = None
    if args.save_video:
        frame_info = camera.get_frame_info()
        if frame_info:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(
                args.output,
                fourcc,
                frame_info['fps'],
                (frame_info['width'], frame_info['height'])
            )
            logger.info(f"Video akan disimpan ke: {args.output}")
    
    # Main loop
    logger.info("Memulai detection loop. Tekan 'q' untuk keluar, 's' untuk screenshot")
    
    fps = 0
    frame_time = time.time()
    reconnect_attempts = 0
    max_reconnect_attempts = 5
    
    try:
        while True:
            # Baca frame
            ret, frame = camera.read_frame()
            
            if not ret:
                logger.warning("Gagal membaca frame dari kamera")
                
                # Coba reconnect
                reconnect_attempts += 1
                if reconnect_attempts <= max_reconnect_attempts:
                    logger.info(f"Mencoba reconnect ({reconnect_attempts}/{max_reconnect_attempts})...")
                    if camera.reconnect():
                        reconnect_attempts = 0
                        continue
                    time.sleep(2)
                else:
                    logger.error("Maksimal reconnect attempts tercapai. Program dihentikan.")
                    break
                continue
            
            # Reset reconnect counter jika berhasil baca frame
            reconnect_attempts = 0
            
            # Deteksi manusia
            annotated_frame, detections, human_count = detector.detect_humans(frame)
            
            # Tambahkan info overlay
            annotated_frame = detector.add_info_overlay(annotated_frame, human_count, fps)
            
            # Hitung FPS
            current_time = time.time()
            fps = 1 / (current_time - frame_time)
            frame_time = current_time
            
            # Tampilkan frame
            cv2.imshow('Human Detection - Hikvision Camera', annotated_frame)
            
            # Simpan video jika diaktifkan
            if video_writer is not None:
                video_writer.write(annotated_frame)
            
            # Log deteksi jika ada manusia terdeteksi
            if human_count > 0:
                logger.info(f"Terdeteksi {human_count} orang dengan confidence: " + 
                           ", ".join([f"{d['confidence']:.2f}" for d in detections]))
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                # Quit
                logger.info("Program dihentikan oleh user")
                break
            elif key == ord('s'):
                # Save snapshot
                snapshot_path = camera.save_snapshot(annotated_frame)
                if snapshot_path:
                    logger.info(f"Snapshot disimpan: {snapshot_path}")
            elif key == ord('r'):
                # Reset statistics
                detector.reset_statistics()
                logger.info("Statistik di-reset")
    
    except KeyboardInterrupt:
        logger.info("Program dihentikan dengan Ctrl+C")
    
    except Exception as e:
        logger.error(f"Error tidak terduga: {str(e)}", exc_info=True)
    
    finally:
        # Cleanup
        logger.info("Membersihkan resources...")
        
        # Tampilkan statistik akhir
        stats = detector.get_statistics()
        logger.info("="*50)
        logger.info("Statistik Deteksi:")
        logger.info(f"  Total Frames: {stats['total_frames']}")
        logger.info(f"  Total Deteksi: {stats['total_detections']}")
        logger.info(f"  Rata-rata deteksi per frame: {stats['average_detections_per_frame']:.2f}")
        logger.info("="*50)
        
        # Release resources
        if video_writer is not None:
            video_writer.release()
            logger.info("Video output disimpan")
        
        camera.disconnect()
        cv2.destroyAllWindows()
        
        logger.info("Program selesai")


if __name__ == "__main__":
    main()
