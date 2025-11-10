"""
Threaded Camera Stream Module - REAL-TIME OPTIMIZED
Menangani koneksi dan streaming dari kamera Hikvision dengan multithreading
untuk mencapai latency minimal (< 1 detik)
"""

import cv2
import logging
import threading
from datetime import datetime
import time

class ThreadedHikvisionCamera:
    """
    Kelas untuk menangani streaming dari kamera Hikvision dengan thread terpisah
    Thread akan terus membaca frame terbaru di background, sehingga detection
    selalu mendapat frame paling fresh (real-time)
    """
    
    def __init__(self, rtsp_url, camera_name="Hikvision Camera"):
        """
        Inisialisasi koneksi kamera dengan threading
        
        Args:
            rtsp_url (str): URL RTSP kamera
            camera_name (str): Nama kamera untuk logging
        """
        self.rtsp_url = rtsp_url
        self.camera_name = camera_name
        self.cap = None
        self.is_connected = False
        
        # Thread variables
        self.frame = None
        self.grabbed = False
        self.read_thread = None
        self.stopped = False
        self.lock = threading.Lock()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """
        Membuka koneksi ke kamera dan start background thread
        
        Returns:
            bool: True jika berhasil terkoneksi, False jika gagal
        """
        try:
            self.logger.info(f"Mencoba koneksi ke {self.camera_name}...")
            
            # CRITICAL: Use RTSP over TCP with minimal buffering
            rtsp_url_tcp = self.rtsp_url
            if "?" not in self.rtsp_url:
                rtsp_url_tcp += "?tcp"
            
            self.cap = cv2.VideoCapture(rtsp_url_tcp, cv2.CAP_FFMPEG)
            
            # CRITICAL: Minimal buffer for real-time
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            
            if self.cap.isOpened():
                self.is_connected = True
                
                # Get stream info
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                
                self.logger.info(f"Berhasil terkoneksi ke {self.camera_name}")
                self.logger.info(f"Resolusi: {width}x{height}, FPS: {fps}")
                self.logger.info(f"REAL-TIME MODE: Background thread started for zero-latency streaming")
                
                # Start background thread
                self.stopped = False
                self.read_thread = threading.Thread(target=self._update_frame, daemon=True)
                self.read_thread.start()
                
                # Wait for first frame
                time.sleep(0.5)
                
                return True
            else:
                self.logger.error(f"Gagal membuka stream dari {self.camera_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saat koneksi ke kamera: {str(e)}")
            return False
    
    def _update_frame(self):
        """
        Background thread untuk terus membaca frame terbaru
        Thread ini berjalan terus menerus untuk selalu mendapat frame paling fresh
        """
        while not self.stopped:
            if self.cap is not None and self.cap.isOpened():
                # CRITICAL: Grab frame as fast as possible
                grabbed = self.cap.grab()
                
                if grabbed:
                    _, frame = self.cap.retrieve()
                    
                    # Update shared frame with thread lock
                    with self.lock:
                        self.frame = frame
                        self.grabbed = True
                else:
                    with self.lock:
                        self.grabbed = False
                        
            else:
                time.sleep(0.01)
    
    def read_frame(self):
        """
        Membaca frame TERBARU dari background thread
        ZERO LATENCY - frame yang didapat adalah frame paling fresh
        
        Returns:
            tuple: (success, frame) - success adalah boolean, frame adalah numpy array
        """
        if not self.is_connected:
            return False, None
        
        # Get latest frame from background thread
        with self.lock:
            if self.grabbed and self.frame is not None:
                return True, self.frame.copy()
            else:
                return False, None
    
    def reconnect(self):
        """
        Mencoba reconnect ke kamera
        
        Returns:
            bool: True jika berhasil reconnect
        """
        self.logger.info(f"Mencoba reconnect ke {self.camera_name}...")
        self.disconnect()
        return self.connect()
    
    def disconnect(self):
        """
        Menutup koneksi kamera dan stop thread
        """
        self.stopped = True
        
        if self.read_thread is not None:
            self.read_thread.join(timeout=2.0)
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        self.is_connected = False
        self.logger.info(f"Koneksi ke {self.camera_name} ditutup")
    
    def get_frame_info(self):
        """
        Mendapatkan informasi frame (resolution, fps, dll)
        
        Returns:
            dict: Dictionary berisi informasi frame
        """
        if self.cap is None or not self.is_connected:
            return None
        
        try:
            info = {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
                'format': self.cap.get(cv2.CAP_PROP_FORMAT)
            }
            return info
        except Exception as e:
            self.logger.error(f"Error getting frame info: {str(e)}")
            return None
