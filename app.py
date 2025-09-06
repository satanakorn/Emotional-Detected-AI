#!/usr/bin/env python3

import cv2
import numpy as np
import time
import os
import sys
from datetime import datetime

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    print("✅ DeepFace library loaded successfully")
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not installed. Using simple face detection only.")
    print("Install with: pip install deepface tensorflow")

class PiCameraEmotionDetector:
    def __init__(self):
        self.cap = None
        self.camera_method = None
        self.face_cascade = None
        self.emotion_history = []
        self.load_face_cascade()
        
    def load_face_cascade(self):
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            print("✅ Face cascade loaded successfully")
        except Exception as e:
            print(f"❌ Error loading face cascade: {e}")
    
    def setup_camera(self):
        print("🔍 Searching for Raspberry Pi Camera...")
        
        if self.try_libcamera():
            return True
            
        if self.try_legacy_camera():
            return True
            
        if self.try_usb_camera():
            return True
            
        print("❌ No camera found. Please check:")
        print("   1. Camera cable connection")
        print("   2. Camera enabled in raspi-config")
        print("   3. Camera permissions")
        return False
    
    def try_libcamera(self):
        try:
            print("🔄 Trying libcamera method...")
            
            result = os.system("which libcamera-hello > /dev/null 2>&1")
            if result != 0:
                print("   libcamera not found")
                return False
            
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
            
            if not self.cap.isOpened():
                print("   Failed to open with CAP_V4L2")
                return False
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print("✅ libcamera method successful")
                self.camera_method = "libcamera"
                return True
            else:
                self.cap.release()
                return False
                
        except Exception as e:
            print(f"   libcamera error: {e}")
            if self.cap:
                self.cap.release()
            return False
    
    def try_legacy_camera(self):
        try:
            print("🔄 Trying legacy camera method...")
            
            os.system("sudo modprobe bcm2835-v4l2 > /dev/null 2>&1")
            time.sleep(2)
            
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                return False
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print("✅ Legacy camera method successful")
                self.camera_method = "legacy"
                return True
            else:
                self.cap.release()
                return False
                
        except Exception as e:
            print(f"   Legacy camera error: {e}")
            if self.cap:
                self.cap.release()
            return False
    
    def try_usb_camera(self):
        try:
            print("🔄 Trying USB camera method...")
            
            for i in range(4):
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        print(f"✅ USB camera found at index {i}")
                        self.camera_method = f"usb_{i}"
                        return True
                    self.cap.release()
            
            return False
            
        except Exception as e:
            print(f"   USB camera error: {e}")
            return False
    
    def detect_emotion_deepface(self, frame):
        try:
            if not DEEPFACE_AVAILABLE:
                return self.detect_faces_simple(frame)
                
            result = DeepFace.analyze(
                frame, 
                actions=['emotion'], 
                enforce_detection=False,
                silent=True
            )
            
            if isinstance(result, list) and len(result) > 0:
                emotion = result[0]['dominant_emotion']
                confidence = result[0]['emotion'][emotion]
                return emotion, confidence
            else:
                return "no_face", 0.0
                
        except Exception as e:
            return self.detect_faces_simple(frame)
    
    def detect_faces_simple(self, frame):
        try:
            if self.face_cascade is None:
                return "no_cascade", 0.0
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                return "face_detected", len(faces)
            else:
                return "no_face", 0.0
                
        except Exception as e:
            print(f"Face detection error: {e}")
            return "error", 0.0
    
    def add_overlay_info(self, frame, emotion, confidence):
        height, width = frame.shape[:2]
        
        cv2.rectangle(frame, (10, 10), (width-10, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (width-10, 120), (255, 255, 255), 2)
        
        emotion_text = f"Emotion: {emotion}"
        cv2.putText(frame, emotion_text, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if isinstance(confidence, (int, float)) and confidence > 0:
            conf_text = f"Confidence: {confidence:.2f}"
            cv2.putText(frame, conf_text, (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        camera_text = f"Camera: {self.camera_method}"
        cv2.putText(frame, camera_text, (20, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        time_text = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, time_text, (width-150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return frame
    
    def save_emotion_data(self, emotion, confidence):
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
        print("🎭 Starting Raspberry Pi Camera Emotion Detection")
        print("=" * 50)
        
        if not self.setup_camera():
            return
        
        print(f"📷 Camera initialized successfully using: {self.camera_method}")
        print("🎯 Starting emotion detection...")
        print("📋 Controls:")
        print("   - Press 'q' to quit")
        print("   - Press 's' to save screenshot")
        print("   - Press 'i' to show camera info")
        print("=" * 50)
        
        frame_count = 0
        fps_start_time = time.time()
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("❌ Error: Can't receive frame")
                    break
                
                frame_count += 1
                
                emotion, confidence = self.detect_emotion_deepface(frame)
                
                frame = self.add_overlay_info(frame, emotion, confidence)
                
                if emotion != "error":
                    self.save_emotion_data(emotion, confidence)
                
                cv2.imshow('Pi Camera - Emotion Detection', frame)
                
                if frame_count % 30 == 0:
                    fps_end_time = time.time()
                    fps = 30 / (fps_end_time - fps_start_time)
                    print(f"📊 FPS: {fps:.1f} | Latest emotion: {emotion}")
                    fps_start_time = fps_end_time
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("👋 Quitting...")
                    break
                elif key == ord('s'):
                    filename = f"emotion_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")
                elif key == ord('i'):
                    self.show_camera_info()
                
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            self.cleanup()
    
    def show_camera_info(self):
        print("\n📷 Camera Information:")
        print(f"   Method: {self.camera_method}")
        if self.cap:
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            print(f"   Resolution: {int(width)}x{int(height)}")
            print(f"   FPS Setting: {fps}")
        print(f"   Emotion history: {len(self.emotion_history)} records")
        print(f"   DeepFace available: {DEEPFACE_AVAILABLE}")
    
    def cleanup(self):
        print("🧹 Cleaning up...")
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
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

def check_camera_status():
    print("🔍 Checking camera status...")
    
    libcamera_result = os.system("which libcamera-hello > /dev/null 2>&1")
    if libcamera_result == 0:
        print("✅ libcamera tools available")
        os.system("libcamera-hello --list-cameras 2>/dev/null || echo '⚠️ No cameras detected by libcamera'")
    else:
        print("⚠️ libcamera tools not found")
    
    print("\n📹 Video devices:")
    os.system("ls -la /dev/video* 2>/dev/null || echo '⚠️ No video devices found'")
    
    print("\n⚙️ Camera configuration:")
    os.system("vcgencmd get_camera 2>/dev/null || echo '⚠️ Cannot get camera status'")

def main():
    print("🍓 Raspberry Pi Camera Module 3 - Emotion Detection")
    print("🎭 Enhanced version with multiple camera support")
    print("=" * 60)
    
    check_camera_status()
    print("=" * 60)
    
    detector = PiCameraEmotionDetector()
    detector.run()

if __name__ == "__main__":
    main()
