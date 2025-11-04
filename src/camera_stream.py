"""
Camera Stream Module
Menangani koneksi dan streaming dari kamera Hikvision menggunakan RTSP
"""

import cv2
import logging
from datetime import datetime

class HikvisionCamera:
    """
    Kelas untuk menangani streaming dari kamera Hikvision DS-2CD2120F-I
    """
    
    def __init__(self, rtsp_url, camera_name="Hikvision Camera"):
        """
        Inisialisasi koneksi kamera
        
        Args:
            rtsp_url (str): URL RTSP kamera
            camera_name (str): Nama kamera untuk logging
        """
        self.rtsp_url = rtsp_url
        self.camera_name = camera_name
        self.cap = None
        self.is_connected = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """
        Membuka koneksi ke kamera
        
        Returns:
            bool: True jika berhasil terkoneksi, False jika gagal
        """
        try:
            self.logger.info(f"Mencoba koneksi ke {self.camera_name}...")
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            # Set buffer size untuk mengurangi latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if self.cap.isOpened():
                self.is_connected = True
                
                # Dapatkan informasi stream
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                
                self.logger.info(f"Berhasil terkoneksi ke {self.camera_name}")
                self.logger.info(f"Resolusi: {width}x{height}, FPS: {fps}")
                return True
            else:
                self.logger.error(f"Gagal membuka stream dari {self.camera_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saat koneksi ke kamera: {str(e)}")
            return False
    
    def read_frame(self):
        """
        Membaca frame dari stream kamera
        
        Returns:
            tuple: (success, frame) - success adalah boolean, frame adalah numpy array
        """
        if not self.is_connected or self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret:
                self.logger.warning(f"Gagal membaca frame dari {self.camera_name}")
                self.is_connected = False
                return False, None
            
            return True, frame
            
        except Exception as e:
            self.logger.error(f"Error saat membaca frame: {str(e)}")
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
        Menutup koneksi kamera
        """
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected = False
        self.logger.info(f"Koneksi ke {self.camera_name} ditutup")
    
    def get_frame_info(self):
        """
        Mendapatkan informasi frame
        
        Returns:
            dict: Informasi tentang frame (width, height, fps)
        """
        if not self.is_connected or self.cap is None:
            return None
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS))
        }
    
    def save_snapshot(self, frame, output_dir="outputs/frames"):
        """
        Menyimpan snapshot frame
        
        Args:
            frame: Frame yang akan disimpan
            output_dir (str): Directory untuk menyimpan snapshot
            
        Returns:
            str: Path file yang disimpan
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/snapshot_{timestamp}.jpg"
        
        try:
            cv2.imwrite(filename, frame)
            self.logger.info(f"Snapshot disimpan: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Error saat menyimpan snapshot: {str(e)}")
            return None
    
    def __del__(self):
        """
        Destructor - pastikan koneksi ditutup
        """
        self.disconnect()
