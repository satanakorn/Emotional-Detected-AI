#!/usr/bin/env python3

import cv2
import numpy as np
import time
import os
import sys
from datetime import datetime
import subprocess
import threading
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from collections import deque
import queue

# ค่าคงที่สำหรับการปรับแต่งประสิทธิภาพ
FRAME_SKIP = 2  # ข้ามเฟรมทุก 2 เฟรม
EMOTION_CACHE_SIZE = 5  # จำนวนเฟรมที่เก็บแคช
EXCEL_SAVE_INTERVAL = 10  # บันทึก Excel ทุก 10 ครั้ง
MAX_QUEUE_SIZE = 100  # ขนาดสูงสุดของคิวสำหรับการบันทึกข้อมูล

try:
    from picamera2 import Picamera2
    from libcamera import controls
    PICAMERA2_AVAILABLE = True
    print("✅ PiCamera2 library loaded successfully")
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("⚠️ PiCamera2 not available, falling back to OpenCV")

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    print("✅ DeepFace library loaded successfully")
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not installed. Using simple face detection only.")
    print("Install with: pip install deepface tensorflow")

class RaspberryPi4CameraDetector:
    def __init__(self):
        self.cap = None
        self.picam2 = None
        self.camera_method = None
        self.face_cascade = None
        self.emotion_history = deque(maxlen=100)  # ใช้ deque แทน list
        self.is_running = False
        self.frame_buffer = None
        self.buffer_lock = threading.Lock()
        self.color_mode = "color"
        self.auto_exposure = True
        self.brightness = 0.0
        self.contrast = 1.0
        self.camera_type = None
        self.excel_file = "emotion_data.xlsx"
        
        # เพิ่มตัวแปรสำหรับการปรับแต่งประสิทธิภาพ
        self.frame_count = 0
        self.last_emotion_time = 0
        self.emotion_cache = {}  # แคชผลการตรวจจับอารมณ์
        self.data_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        self.excel_save_counter = 0
        
        # เริ่มเธรดสำหรับการบันทึกข้อมูล
        self.save_thread = threading.Thread(target=self._save_data_worker, daemon=True)
        self.save_thread.start()
        
        self.load_face_cascade()
        self.initialize_excel()

    def _save_data_worker(self):
        """เธรดสำหรับการบันทึกข้อมูลลง Excel"""
        while self.is_running:
            try:
                data = self.data_queue.get(timeout=1)
                if data:
                    self._save_to_excel_internal(*data)
                    self.excel_save_counter += 1
                    
                    # บันทึกไฟล์ Excel ทุกๆ EXCEL_SAVE_INTERVAL ครั้ง
                    if self.excel_save_counter >= EXCEL_SAVE_INTERVAL:
                        self._save_excel_file()
                        self.excel_save_counter = 0
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")

    def _save_excel_file(self):
        """บันทึกไฟล์ Excel"""
        try:
            if hasattr(self, '_wb'):
                self._wb.save(self.excel_file)
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการบันทึกไฟล์ Excel: {e}")

    def initialize_excel(self):
        """สร้างไฟล์ Excel ใหม่ถ้ายังไม่มี"""
        try:
            if not os.path.exists(self.excel_file):
                self._wb = Workbook()
                ws = self._wb.active
                ws.title = "ข้อมูลอารมณ์"
                
                headers = [
                    "วันที่", "เวลา", "อารมณ์", "ความมั่นใจ (%)", 
                    "ระดับความพึงพอใจ", "คะแนน", "วิธีการกล้อง"
                ]
                
                header_font = Font(bold=True, size=12)
                header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
                
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col)
                    cell.value = header
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal='center')
                
                for col in range(1, len(headers) + 1):
                    ws.column_dimensions[chr(64 + col)].width = 15
                
                self._wb.save(self.excel_file)
                print(f"✅ สร้างไฟล์ Excel ใหม่: {self.excel_file}")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการสร้างไฟล์ Excel: {e}")

    def save_to_excel(self, emotion, confidence, satisfaction_level, satisfaction_text):
        """เพิ่มข้อมูลลงในคิวสำหรับการบันทึก"""
        try:
            now = datetime.now()
            data = (
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                emotion,
                f"{confidence:.2f}",
                satisfaction_level,
                satisfaction_text,
                self.camera_method
            )
            self.data_queue.put(data, block=False)
        except queue.Full:
            print("⚠️ คิวข้อมูลเต็ม กำลังข้ามการบันทึกข้อมูล")

    def _save_to_excel_internal(self, date, time, emotion, confidence, satisfaction_level, satisfaction_text, camera_method):
        """บันทึกข้อมูลลงในไฟล์ Excel"""
        try:
            if not hasattr(self, '_wb'):
                self._wb = openpyxl.load_workbook(self.excel_file)
            ws = self._wb.active
            
            next_row = ws.max_row + 1
            data = [date, time, emotion, confidence, satisfaction_level, satisfaction_text, camera_method]
            
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=next_row, column=col)
                cell.value = value
                cell.alignment = Alignment(horizontal='center')
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการบันทึกข้อมูลลง Excel: {e}")

    def load_face_cascade(self):
        """แก้ปัญหา cv2.data ใน Raspberry Pi 4"""
        try:
            # ลองหา cascade files ในตำแหน่งต่างๆ   
            possible_paths = [
                '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
                '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
                '/home/pi/.local/lib/python3.*/site-packages/cv2/data/haarcascade_frontalface_default.xml'
            ]
            
            # ลองใช้ cv2.data ก่อน
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if os.path.exists(cascade_path):
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    print("✅ Face cascade loaded from cv2.data")
                    return
            except AttributeError:
                pass
            
            # ถ้าไม่ได้ ให้ลองจากตำแหน่งอื่น
            for path in possible_paths:
                if os.path.exists(path):
                    self.face_cascade = cv2.CascadeClassifier(path)
                    print(f"✅ Face cascade loaded from {path}")
                    return
            
            # ดาวน์โหลดถ้าไม่เจอ
            print("📥 Downloading Haar cascade file...")
            import urllib.request
            url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
            cascade_path = "haarcascade_frontalface_default.xml"
            urllib.request.urlretrieve(url, cascade_path)
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            print("✅ Face cascade downloaded and loaded")
            
        except Exception as e:
            print(f"❌ Error loading face cascade: {e}")
            self.face_cascade = None
    
    def check_camera_hardware(self):
        """ตรวจสอบฮาร์ดแวร์กล้องใน Raspberry Pi 4"""
        print("🔍 Enhanced camera status check...")
        print("=" * 50)
        
        # ตรวจสอบ libcamera
        try:
            result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ libcamera tools available")
                print("📷 Available cameras:")
                print(result.stdout)
            else:
                print("⚠️ libcamera available but no cameras detected")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ libcamera tools not found")
        
        # ตรวจสอบ video devices
        print("\n📹 Video devices:")
        os.system("ls -la /dev/video* 2>/dev/null || echo '⚠️ No video devices found'")
        
        # ตรวจสอบ vcgencmd
        print("\n⚙️ Camera configuration:")
        os.system("vcgencmd get_camera 2>/dev/null || echo '⚠️ Cannot get camera status'")
        
        # ตรวจสอบ config.txt
        print("\n📝 Config.txt camera settings:")
        os.system("grep -E '(camera|start_x|gpu_mem)' /boot/config.txt 2>/dev/null || echo '⚠️ No camera settings found'")
        
        print("=" * 50)
    
    def setup_picamera2(self):
        """ตั้งค่า PiCamera2 สำหรับ Raspberry Pi 4 พร้อมจัดการสี"""
        try:
            if not PICAMERA2_AVAILABLE:
                return False
            
            print("🔄 Trying PiCamera2 method...")
            
            self.picam2 = Picamera2()
            
            # กำหนดค่า preview config สำหรับสีที่ถูกต้อง
            if self.color_mode == "grayscale":
                config = self.picam2.create_preview_configuration(
                    main={"size": (640, 480), "format": "YUV420"},
                    controls={"FrameRate": 30}
                )
            else:
                config = self.picam2.create_preview_configuration(
                    main={"size": (640, 480), "format": "RGB888"},
                    controls={"FrameRate": 30}
                )
            
            self.picam2.configure(config)
            
            # ตั้งค่า controls สำหรับการปรับแสงและสี
            control_settings = {
                "AeEnable": self.auto_exposure,
                "AwbEnable": True,  # Auto White Balance
                "AwbMode": controls.AwbModeEnum.Auto,
                "Brightness": self.brightness,
                "Contrast": self.contrast,
                "Saturation": 1.0,
                "Sharpness": 1.0
            }
            
            self.picam2.set_controls(control_settings)
            
            self.picam2.start()
            time.sleep(2)  # รอให้กล้องเริ่มต้นและปรับแสง
            
            # ทดสอบการจับภาพ
            frame = self.picam2.capture_array()
            if frame is not None and frame.size > 0:
                print(f"✅ PiCamera2 method successful - Format: {frame.shape}")
                print(f"📷 Color mode: {self.color_mode}")
                self.camera_method = "picamera2"
                self.start_frame_capture_thread()
                return True
            else:
                self.picam2.stop()
                return False
                
        except Exception as e:
            print(f"   PiCamera2 error: {e}")
            if self.picam2:
                try:
                    self.picam2.stop()
                except:
                    pass
            return False
    
    def start_frame_capture_thread(self):
        """เริ่มเธรดสำหรับจับภาพอย่างต่อเนื่อง"""
        def capture_frames():
            while self.is_running:
                try:
                    if self.picam2:
                        frame = self.picam2.capture_array()
                        with self.buffer_lock:
                            self.frame_buffer = frame.copy()
                    time.sleep(0.03)  # ~30 FPS
                except Exception as e:
                    print(f"Frame capture error: {e}")
                    break
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=capture_frames, daemon=True)
        self.capture_thread.start()
    
    def setup_opencv_camera(self):
        """ตั้งค่ากล้องด้วย OpenCV สำหรับ Raspberry Pi 4 พร้อมจัดการสี"""
        try:
            print("🔄 Trying OpenCV with V4L2...")
            
            # ลองใช้ GStreamer pipeline ก่อน
            if self.color_mode == "grayscale":
                gst_pipeline = (
                    "libcamerasrc ! "
                    "video/x-raw,width=640,height=480,framerate=30/1,format=GRAY8 ! "
                    "videoconvert ! appsink"
                )
            else:
                gst_pipeline = (
                    "libcamerasrc ! "
                    "video/x-raw,width=640,height=480,framerate=30/1 ! "
                    "videoconvert ! appsink"
                )
            
            self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
            
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"✅ GStreamer pipeline successful - Shape: {frame.shape}")
                    self.camera_method = "gstreamer"
                    return True
                self.cap.release()
            
            # ถ้า GStreamer ไม่ได้ ลอง V4L2
            print("🔄 Trying V4L2 direct access...")
            
            # เปิดใช้งาน bcm2835-v4l2 module
            os.system("sudo modprobe bcm2835-v4l2 2>/dev/null")
            time.sleep(2)
            
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
            
            if self.cap.isOpened():
                # ตั้งค่าความละเอียดและ FPS
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # ตั้งค่าสี
                self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
                self.cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
                self.cap.set(cv2.CAP_PROP_SATURATION, 0.5)
                self.cap.set(cv2.CAP_PROP_AUTO_WB, 1.0)
                
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"✅ V4L2 method successful - Shape: {frame.shape}")
                    self.camera_method = "v4l2"
                    return True
                self.cap.release()
            
            # ลองกล้อง USB
            print("🔄 Trying USB cameras...")
            for i in range(4):
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        print(f"✅ USB camera found at index {i} - Shape: {frame.shape}")
                        self.camera_method = f"usb_{i}"
                        return True
                    self.cap.release()
            
            return False
            
        except Exception as e:
            print(f"   OpenCV camera error: {e}")
            if self.cap:
                self.cap.release()
            return False
    
    def setup_laptop_camera(self):
        """ตั้งค่ากล้องโน๊ตบุ๊ค"""
        try:
            print("🔄 กำลังตั้งค่ากล้องเว็บแคม...")
            self.cap = cv2.VideoCapture(0)  # ใช้กล้องแรกที่เจอ
            
            if self.cap.isOpened():
                # ตั้งค่าความละเอียดและ FPS
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"✅ ตั้งค่ากล้องเว็บแคมสำเร็จ - ขนาดภาพ: {frame.shape}")
                    self.camera_method = "laptop_webcam"
                    return True
                self.cap.release()
            
            return False
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการตั้งค่ากล้องเว็บแคม: {e}")
            if self.cap:
                self.cap.release()
            return False
    
    def setup_camera(self):
        """ตั้งค่ากล้องตามประเภทที่เลือก"""
        print("🔍 Camera setup...")
        
        if self.camera_type == "laptop":
            return self.setup_laptop_camera()
        elif self.camera_type == "pi":
            # ลอง PiCamera2 ก่อน (แนะนำสำหรับ RPi 4)
            if self.setup_picamera2():
                return True
            
            # ถ้าไม่ได้ ลอง OpenCV
            if self.setup_opencv_camera():
                return True
        
        print("❌ No camera found. Troubleshooting steps:")
        print("   1. Check camera cable connection")
        print("   2. Enable camera: sudo raspi-config")
        print("   3. Add to /boot/config.txt: camera_auto_detect=1")
        print("   4. Increase GPU memory: gpu_mem=128")
        print("   5. Reboot system")
        return False
    
    def get_frame(self):
        """รับเฟรมจากกล้องและจัดการสี"""
        frame = None
        
        if self.camera_method == "picamera2":
            with self.buffer_lock:
                if self.frame_buffer is not None:
                    frame = self.frame_buffer.copy()
        elif self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                frame = None
        
        if frame is None:
            return None
        
        # จัดการการแปลงสีตามโหมดที่เลือก
        if self.color_mode == "grayscale":
            if len(frame.shape) == 3:
                if self.camera_method == "picamera2":
                    # PiCamera2 RGB to Grayscale
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                else:
                    # OpenCV BGR to Grayscale
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # แปลงกลับเป็น 3 channels สำหรับการแสดงผล
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        elif self.color_mode == "color":
            # ตรวจสอบให้แน่ใจว่าเป็น BGR สำหรับ OpenCV
            if self.camera_method == "picamera2" and len(frame.shape) == 3:
                # แปลงจาก RGB เป็น BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        return frame
    
    def detect_emotion_deepface(self, frame):
        """ตรวจจับอารมณ์ด้วย DeepFace พร้อมแคชชิ่ง"""
        try:
            if not DEEPFACE_AVAILABLE:
                return self.detect_faces_simple(frame)
            
            # ตรวจสอบแคช
            frame_hash = hash(frame.tobytes())
            if frame_hash in self.emotion_cache:
                return self.emotion_cache[frame_hash]
            
            # ข้ามการตรวจจับถ้าเร็วเกินไป
            current_time = time.time()
            if current_time - self.last_emotion_time < 0.1:  # 100ms
                return None
            
            self.last_emotion_time = current_time
            
            if self.camera_method == "picamera2":
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                else:
                    frame_bgr = frame
            else:
                frame_bgr = frame
                
            result = DeepFace.analyze(
                frame_bgr, 
                actions=['emotion'], 
                enforce_detection=False,
                silent=True
            )
            
            if isinstance(result, list) and len(result) > 0:
                emotion_map = {
                    'angry': 'Angry',
                    'disgust': 'Disgust',
                    'fear': 'Fear',
                    'happy': 'Happy',
                    'sad': 'Sad',
                    'surprise': 'Surprise',
                    'neutral': 'Neutral'
                }
                
                emotion = result[0]['dominant_emotion']
                confidence = result[0]['emotion'][emotion]
                satisfaction_level = min(5, max(1, int(confidence / 20) + 1))
                satisfaction_text = "★" * satisfaction_level
                
                result = (
                    emotion_map.get(emotion, emotion),
                    confidence,
                    satisfaction_level,
                    satisfaction_text
                )
                
                # เก็บผลลัพธ์ในแคช
                self.emotion_cache[frame_hash] = result
                if len(self.emotion_cache) > EMOTION_CACHE_SIZE:
                    self.emotion_cache.pop(next(iter(self.emotion_cache)))
                
                # บันทึกข้อมูล
                self.save_to_excel(*result)
                
                return result
            else:
                return "No Face", 0.0, 0, ""
                
        except Exception as e:
            print(f"DeepFace error: {e}")
            return self.detect_faces_simple(frame)
    
    def detect_faces_simple(self, frame):
        """ตรวจจับใบหน้าแบบง่าย พร้อมจัดการสี"""
        try:
            if self.face_cascade is None:
                return "no_cascade", 0.0
            
            # แปลงเป็น grayscale สำหรับ face detection
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
                
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            # วาดกรอบรอบใบหน้าที่ตรวจพบ
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    # เพิ่มป้ายกำกับ
                    cv2.putText(frame, "Face", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            return "face_detected", len(faces) if len(faces) > 0 else 0.0
                
        except Exception as e:
            print(f"Face detection error: {e}")
            return "error", 0.0
    
    def add_overlay_info(self, frame, emotion, confidence, satisfaction_level, satisfaction_text):
        """เพิ่มข้อมูลลงบนเฟรม พร้อมจัดการสี"""
        if frame is None:
            return frame
        
        height, width = frame.shape[:2]
        
        # วาดกรอบข้อมูลพื้นหลังโปร่งใส
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (width-10, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # กรอบขอบ
        cv2.rectangle(frame, (10, 10), (width-10, 200), (255, 255, 255), 2)
        
        # ข้อความอารมณ์ (สีเขียวสดใส)
        emotion_text = f"Emotion: {emotion}"
        cv2.putText(frame, emotion_text, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # ความมั่นใจ (สีเหลือง)
        if isinstance(confidence, (int, float)) and confidence > 0:
            conf_text = f"Confidence: {confidence:.2f}%"
            cv2.putText(frame, conf_text, (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # ระดับความพึงพอใจ (สีฟ้า)
        satisfaction_level_text = f"Satisfaction: {satisfaction_level}/5"
        cv2.putText(frame, satisfaction_level_text, (20, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # ดาวแสดงความพึงพอใจ (สีเหลือง)
        stars_text = f"Score: {satisfaction_text}"
        cv2.putText(frame, stars_text, (20, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # วิธีการกล้อง (สีขาว)
        camera_text = f"Camera: {self.camera_method}"
        cv2.putText(frame, camera_text, (20, 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # โหมดสี (สีม่วง)
        color_text = f"Mode: {self.color_mode}"
        cv2.putText(frame, color_text, (20, 180), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        # เวลา (สีฟ้า)
        time_text = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, time_text, (width-150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return frame
    
    def save_emotion_data(self, emotion, confidence):
        """บันทึกข้อมูลอารมณ์"""
        timestamp = datetime.now().isoformat()
        data = {
            'timestamp': timestamp,
            'emotion': emotion,
            'confidence': confidence,
            'camera_method': self.camera_method
        }
        self.emotion_history.append(data)
        
        if len(self.emotion_history) > 100:
            self.emotion_history.pop(0)
    
    def run(self):
        """เริ่มการทำงานหลัก"""
        print("🎭 เริ่มการตรวจจับอารมณ์ด้วยกล้อง")
        print("=" * 60)
        
        if not self.setup_camera():
            return
        
        print(f"📷 เริ่มต้นกล้องสำเร็จ: {self.camera_method}")
        print("🎯 เริ่มการตรวจจับอารมณ์...")
        print("📋 คำสั่งควบคุม:")
        print("   - กด 'q' เพื่อออก")
        print("   - กด 's' หรือ SPACE เพื่อบันทึกรูปภาพ")
        print("   - กด 'i' เพื่อดูข้อมูลกล้อง")
        print("   - กด 'c' เพื่อสลับโหมดสี")
        print("   - กด 'b'/'v' เพื่อปรับความสว่าง (+/-)")
        print("   - กด 'n'/'m' เพื่อปรับคอนทราสต์ (+/-)")
        print("=" * 60)
        
        self.is_running = True
        frame_count = 0
        fps_start_time = time.time()
        last_fps_update = time.time()
        fps = 0
        
        try:
            while True:
                frame = self.get_frame()
                
                if frame is None:
                    print("❌ Error: Can't receive frame")
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # ข้ามเฟรมเพื่อเพิ่มประสิทธิภาพ
                if frame_count % FRAME_SKIP != 0:
                    continue
                
                # ตรวจจับอารมณ์
                result = self.detect_emotion_deepface(frame)
                if result:
                    emotion, confidence, satisfaction_level, satisfaction_text = result
                    display_frame = self.add_overlay_info(
                        frame, emotion, confidence, satisfaction_level, satisfaction_text
                    )
                    
                    if display_frame is not None:
                        cv2.imshow('Emotion Detection', display_frame)
                
                # อัพเดท FPS ทุก 1 วินาที
                current_time = time.time()
                if current_time - last_fps_update >= 1.0:
                    fps = frame_count / (current_time - fps_start_time)
                    frame_count = 0
                    fps_start_time = current_time
                    last_fps_update = current_time
                    print(f"📊 FPS: {fps:.1f}")
                
                # จัดการ key input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') or key == 32:
                    filename = f"emotion_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"📸 Screenshot saved: {filename}")
                elif key == ord('i'):
                    self.show_camera_info()
                elif key == ord('c'):
                    self.toggle_color_mode()
                elif key == ord('b'):
                    self.adjust_brightness(0.1)
                elif key == ord('v'):
                    self.adjust_brightness(-0.1)
                elif key == ord('n'):
                    self.adjust_contrast(0.1)
                elif key == ord('m'):
                    self.adjust_contrast(-0.1)
                
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            self.cleanup()
    
    def toggle_color_mode(self):
        """สลับโหมดสี"""
        if self.color_mode == "color":
            self.color_mode = "grayscale"
            print("🎨 Switched to grayscale mode")
        else:
            self.color_mode = "color"
            print("🎨 Switched to color mode")
    
    def adjust_brightness(self, delta):
        """ปรับความสว่าง"""
        self.brightness = max(-1.0, min(1.0, self.brightness + delta))
        print(f"💡 Brightness: {self.brightness:.1f}")
        
        if self.picam2:
            try:
                self.picam2.set_controls({"Brightness": self.brightness})
            except:
                pass
    
    def adjust_contrast(self, delta):
        """ปรับคอนทราสต์"""
        self.contrast = max(0.0, min(2.0, self.contrast + delta))
        print(f"🔆 Contrast: {self.contrast:.1f}")
        
        if self.picam2:
            try:
                self.picam2.set_controls({"Contrast": self.contrast})
            except:
                pass
        """แสดงข้อมูลกล้อง"""
        print("\n📷 Camera Information:")
        print(f"   Method: {self.camera_method}")
        print(f"   Emotion history: {len(self.emotion_history)} records")
        print(f"   DeepFace available: {DEEPFACE_AVAILABLE}")
        print(f"   PiCamera2 available: {PICAMERA2_AVAILABLE}")
        
        if self.cap:
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            print(f"   Resolution: {int(width)}x{int(height)}")
            print(f"   FPS Setting: {fps}")
    
    def cleanup(self):
        """ทำความสะอาดและบันทึกข้อมูลสุดท้าย"""
        print("🧹 Cleaning up...")
        
        self.is_running = False
        
        if self.picam2:
            try:
                self.picam2.stop()
            except:
                pass
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        # บันทึกข้อมูลที่เหลือในคิว
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                self._save_to_excel_internal(*data)
            self._save_excel_file()
        except:
            pass
        
        if self.emotion_history:
            print(f"📊 Total emotions detected: {len(self.emotion_history)}")
            
            emotions = [record['emotion'] for record in self.emotion_history]
            unique_emotions = set(emotions)
            print("📈 Emotion statistics:")
            for emotion in unique_emotions:
                count = emotions.count(emotion)
                percentage = (count / len(emotions)) * 100
                print(f"   {emotion}: {count} times ({percentage:.1f}%)")
        
        print("✅ Cleanup completed")

def main():
    print("🎭 ระบบตรวจจับอารมณ์ด้วยกล้อง")
    print("🎨 เวอร์ชัน 2.2 - เลือกกล้องและปรับแต่งการแสดงผล")
    print("=" * 70)
    
    # เลือกประเภทกล้อง
    print("\n🔧 เลือกประเภทกล้อง:")
    print("1. กล้องเว็บแคม (โน๊ตบุ๊ค)")
    print("2. กล้อง Raspberry Pi")
    
    while True:
        try:
            choice = input("เลือกประเภทกล้อง (1-2): ").strip()
            if choice == "1":
                camera_type = "laptop"
                break
            elif choice == "2":
                camera_type = "pi"
                break
            else:
                print("❌ ตัวเลือกไม่ถูกต้อง กรุณาเลือก 1 หรือ 2")
        except:
            print("❌ การป้อนข้อมูลไม่ถูกต้อง กรุณาลองใหม่")
    
    # เลือกโหมดสี
    print("\n🔧 เลือกโหมดการแสดงผล:")
    print("1. โหมดสี (ค่าเริ่มต้น)")
    print("2. โหมดขาวดำ")
    
    try:
        choice = input("เลือกโหมด (1-2, กด Enter สำหรับค่าเริ่มต้น): ").strip()
        color_mode = "grayscale" if choice == "2" else "color"
    except:
        color_mode = "color"
    
    detector = RaspberryPi4CameraDetector()
    detector.camera_type = camera_type
    detector.color_mode = color_mode
    detector.check_camera_hardware()
    detector.run()

if __name__ == "__main__":
    main()