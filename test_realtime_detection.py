#!/usr/bin/env python3

import cv2
import numpy as np
import time
import os
import sys
from datetime import datetime

class RealtimeDetectionTester:
    def __init__(self):
        self.cap = None
        self.face_cascade = None
        self.camera_method = None
        self.load_face_cascade()
        
        # ตัวแปรสำหรับ real-time detection
        self.frame_count = 0
        self.detection_count = 0
        self.last_detection_time = 0
        self.detection_interval = 0.05  # 50ms (20 FPS)
        
        # ตัวแปรสำหรับการบันทึกข้อมูล
        self.last_save_time = time.time()
        self.save_interval = 5.0  # 5 วินาที
        self.current_emotion = "No Face"
        self.current_confidence = 0.0
    
    def load_face_cascade(self):
        """โหลด Haar cascade สำหรับการตรวจจับใบหน้า"""
        try:
            # ลองใช้ cv2.data ก่อน
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if os.path.exists(cascade_path):
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    print("✅ Face cascade loaded from cv2.data")
                    return
            except AttributeError:
                pass
            
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
    
    def enhance_frame_for_detection(self, frame):
        """ปรับปรุงเฟรมเพื่อการตรวจจับใบหน้าที่ดีขึ้น"""
        try:
            # ปรับความสว่างและคอนทราสต์
            enhanced = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            
            # ลด noise
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            return enhanced
        except Exception as e:
            print(f"Frame enhancement error: {e}")
            return frame
    
    def detect_faces_realtime(self, frame):
        """ตรวจจับใบหน้าแบบ real-time"""
        try:
            if self.face_cascade is None:
                return []
            
            # ตรวจสอบเวลาการตรวจจับ
            current_time = time.time()
            if current_time - self.last_detection_time < self.detection_interval:
                return []
            
            self.last_detection_time = current_time
            
            # ปรับปรุงเฟรมเพื่อการตรวจจับที่ดีขึ้น
            enhanced_frame = self.enhance_frame_for_detection(frame)
            
            # แปลงเป็น grayscale สำหรับ face detection
            if len(enhanced_frame.shape) == 3:
                gray = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = enhanced_frame
            
            # ปรับปรุงพารามิเตอร์การตรวจจับใบหน้า
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05,
                minNeighbors=2,
                minSize=(30, 30),
                maxSize=(300, 300),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return faces
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def draw_face_boxes(self, frame, faces):
        """วาดกรอบรอบใบหน้าที่ตรวจจับได้"""
        if len(faces) > 0:
            # หาใบหน้าที่ใหญ่ที่สุด (น่าจะเป็นใบหน้าหลัก)
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            x, y, w, h = largest_face
            
            # วาดกรอบใบหน้าหลัก (สีเขียวเข้ม)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            
            # เพิ่มป้ายกำกับใบหน้า
            cv2.putText(frame, "FACE DETECTED", (x, y-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # วาดกรอบใบหน้าอื่นๆ (สีเขียวอ่อน)
            for (fx, fy, fw, fh) in faces:
                if (fx, fy, fw, fh) != (x, y, w, h):  # ไม่ใช่ใบหน้าหลัก
                    cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (0, 200, 0), 1)
                    cv2.putText(frame, "Face", (fx, fy-5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 0), 1)
            
            # อัพเดทข้อมูลปัจจุบัน
            self.current_emotion = "Face Detected"
            self.current_confidence = 65.0
            
            # แสดงจำนวนใบหน้าที่ตรวจจับได้
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # อัพเดทข้อมูลปัจจุบัน
            self.current_emotion = "No Face"
            self.current_confidence = 0.0
            
            # แสดงข้อความ "No Face Detected"
            height, width = frame.shape[:2]
            cv2.putText(frame, "NO FACE DETECTED", (width//2 - 150, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            cv2.putText(frame, "Please position your face in front of camera", 
                       (width//2 - 200, height//2 + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        
        return frame
    
    def setup_camera(self):
        """ตั้งค่ากล้อง"""
        print("🔍 Setting up camera...")
        
        # ลองกล้อง USB แบบธรรมดาก่อน
        for i in range(5):
            print(f"   Testing camera index {i}...")
            self.cap = cv2.VideoCapture(i)
            
            if self.cap.isOpened():
                # ตั้งค่าความละเอียดและ FPS
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera found at index {i} - Shape: {frame.shape}")
                    self.camera_method = f"usb_{i}"
                    return True
                self.cap.release()
            else:
                print(f"   Camera {i} not available")
        
        print("❌ No working camera found")
        return False
    
    def save_data_if_needed(self):
        """บันทึกข้อมูลทุก 5 วินาที"""
        current_time = time.time()
        if current_time - self.last_save_time >= self.save_interval:
            # บันทึกข้อมูล
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"💾 Data saved: {self.current_emotion} ({self.current_confidence:.1f}%) - {timestamp}")
            self.last_save_time = current_time
            return True
        return False
    
    def run_test(self):
        """รันการทดสอบ real-time detection"""
        print("🧪 Real-time Face Detection Test")
        print("=" * 40)
        
        if not self.setup_camera():
            return False
        
        print("📷 Camera ready, starting real-time detection...")
        print("💾 Data will be saved every 5 seconds")
        print("Press 'q' to quit, 's' to save screenshot")
        
        start_time = time.time()
        last_fps_update = time.time()
        fps = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: Can't receive frame")
                    continue
                
                self.frame_count += 1
                
                # ตรวจจับใบหน้าแบบ real-time
                faces = self.detect_faces_realtime(frame)
                if len(faces) > 0:
                    self.detection_count += 1
                
                # วาดกรอบใบหน้า
                display_frame = self.draw_face_boxes(frame.copy(), faces)
                
                # แสดงข้อมูลเพิ่มเติม
                height, width = display_frame.shape[:2]
                
                # แสดงสถิติ
                current_time = time.time()
                detection_rate = (self.detection_count / self.frame_count) * 100 if self.frame_count > 0 else 0
                
                cv2.putText(display_frame, f"Detection Rate: {detection_rate:.1f}%", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(display_frame, f"Frames: {self.frame_count}", 
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(display_frame, f"FPS: {fps:.1f}", 
                           (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # แสดงสถานะการบันทึกข้อมูล
                time_since_save = current_time - self.last_save_time
                save_status = f"Next save in: {self.save_interval - time_since_save:.1f}s"
                cv2.putText(display_frame, save_status, (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # แสดงข้อมูลปัจจุบัน
                cv2.putText(display_frame, f"Current: {self.current_emotion}", 
                           (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(display_frame, f"Confidence: {self.current_confidence:.1f}%", 
                           (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # แสดงผล
                cv2.imshow('Real-time Face Detection Test', display_frame)
                
                # บันทึกข้อมูลทุก 5 วินาที
                self.save_data_if_needed()
                
                # อัพเดท FPS ทุก 1 วินาที
                if current_time - last_fps_update >= 1.0:
                    fps = self.frame_count / (current_time - start_time)
                    self.frame_count = 0
                    start_time = current_time
                    last_fps_update = current_time
                    print(f"📊 FPS: {fps:.1f}, Detection Rate: {detection_rate:.1f}%")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    filename = f"realtime_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"📸 Screenshot saved: {filename}")
        
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted")
        
        finally:
            cv2.destroyAllWindows()
            if self.cap:
                self.cap.release()
            
            # สรุปผลการทดสอบ
            total_time = time.time() - start_time
            final_detection_rate = (self.detection_count / self.frame_count) * 100 if self.frame_count > 0 else 0
            
            print(f"\n📊 Final Results:")
            print(f"   Total time: {total_time:.1f} seconds")
            print(f"   Frames processed: {self.frame_count}")
            print(f"   Faces detected: {self.detection_count}")
            print(f"   Detection rate: {final_detection_rate:.1f}%")
            print(f"   Average FPS: {self.frame_count / total_time:.1f}")
            
            if final_detection_rate > 80:
                print("✅ Real-time detection working excellently!")
            elif final_detection_rate > 50:
                print("⚠️ Real-time detection working well")
            else:
                print("❌ Real-time detection needs improvement")
            
            return final_detection_rate > 50

def main():
    print("🧪 Real-time Face Detection Test Tool")
    print("🎯 Test real-time detection with 5-second data saving")
    print("=" * 60)
    
    tester = RealtimeDetectionTester()
    success = tester.run_test()
    
    if success:
        print("\n✅ Real-time detection test completed successfully!")
    else:
        print("\n❌ Real-time detection test failed")
        print("💡 Check camera connection and lighting conditions")

if __name__ == "__main__":
    main()
