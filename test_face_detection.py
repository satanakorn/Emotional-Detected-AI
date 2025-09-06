#!/usr/bin/env python3

import cv2
import numpy as np
import time
import os
import sys
from datetime import datetime

class FaceDetectionTester:
    def __init__(self):
        self.cap = None
        self.face_cascade = None
        self.camera_method = None
        self.load_face_cascade()
    
    def load_face_cascade(self):
        """โหลด Haar cascade สำหรับการตรวจจับใบหน้า"""
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
    
    def enhance_frame_for_detection(self, frame):
        """ปรับปรุงเฟรมเพื่อการตรวจจับใบหน้าที่ดีขึ้น"""
        try:
            # ปรับความสว่างและคอนทราสต์
            enhanced = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            
            # ลด noise
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # ปรับ histogram
            if len(enhanced.shape) == 3:
                # แปลงเป็น LAB color space
                lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                # ปรับ L channel ด้วย CLAHE
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                l = clahe.apply(l)
                
                # รวมกลับ
                enhanced = cv2.merge([l, a, b])
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            return enhanced
        except Exception as e:
            print(f"Frame enhancement error: {e}")
            return frame
    
    def detect_faces(self, frame):
        """ตรวจจับใบหน้าในเฟรม"""
        try:
            if self.face_cascade is None:
                return []
            
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
                scaleFactor=1.05,  # ลดลงเพื่อตรวจจับได้ดีขึ้น
                minNeighbors=2,    # ลดลงเพื่อตรวจจับได้ง่ายขึ้น
                minSize=(30, 30),  # เพิ่มขนาดขั้นต่ำเล็กน้อย
                maxSize=(300, 300), # เพิ่มขนาดสูงสุด
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
            
            # แสดงจำนวนใบหน้าที่ตรวจจับได้
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
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
    
    def run_test(self):
        """รันการทดสอบการตรวจจับใบหน้า"""
        print("🧪 Face Detection Test")
        print("=" * 30)
        
        if not self.setup_camera():
            return False
        
        print("📷 Camera ready, testing face detection...")
        print("Press 'q' to quit, 's' to save screenshot")
        print("Press 'e' to toggle frame enhancement")
        
        frame_count = 0
        face_detected_count = 0
        use_enhancement = True
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: Can't receive frame")
                    continue
                
                frame_count += 1
                
                # ตรวจจับใบหน้า
                faces = self.detect_faces(frame)
                if len(faces) > 0:
                    face_detected_count += 1
                
                # วาดกรอบใบหน้า
                display_frame = self.draw_face_boxes(frame.copy(), faces)
                
                # แสดงข้อมูลเพิ่มเติม
                height, width = display_frame.shape[:2]
                
                # แสดงสถิติ
                if frame_count > 0:
                    detection_rate = (face_detected_count / frame_count) * 100
                    cv2.putText(display_frame, f"Detection Rate: {detection_rate:.1f}%", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(display_frame, f"Frames: {frame_count}", 
                               (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(display_frame, f"Enhancement: {'ON' if use_enhancement else 'OFF'}", 
                               (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # แสดงผล
                cv2.imshow('Face Detection Test', display_frame)
                
                # แสดงสถิติในคอนโซล
                if frame_count % 30 == 0:  # ทุก 30 เฟรม
                    detection_rate = (face_detected_count / frame_count) * 100
                    print(f"📊 Detection rate: {detection_rate:.1f}% ({face_detected_count}/{frame_count})")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    filename = f"face_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"📸 Screenshot saved: {filename}")
                elif key == ord('e'):
                    use_enhancement = not use_enhancement
                    print(f"🔧 Frame enhancement: {'ON' if use_enhancement else 'OFF'}")
        
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted")
        
        finally:
            cv2.destroyAllWindows()
            if self.cap:
                self.cap.release()
            
            # สรุปผลการทดสอบ
            if frame_count > 0:
                detection_rate = (face_detected_count / frame_count) * 100
                print(f"\n📊 Final Detection Rate: {detection_rate:.1f}%")
                print(f"📈 Frames processed: {frame_count}")
                print(f"👤 Faces detected: {face_detected_count}")
                
                if detection_rate > 80:
                    print("✅ Face detection working well!")
                elif detection_rate > 50:
                    print("⚠️ Face detection working but could be better")
                else:
                    print("❌ Face detection needs improvement")
                    print("💡 Try:")
                    print("   - Better lighting")
                    print("   - Face directly in front of camera")
                    print("   - Remove glasses or hat")
                    print("   - Check camera focus")
                    print("   - Try different camera position")
                
                return detection_rate > 50
            else:
                print("❌ No frames processed")
                return False

def main():
    print("🧪 Face Detection Test Tool")
    print("🎯 Test and improve face detection performance")
    print("=" * 50)
    
    tester = FaceDetectionTester()
    success = tester.run_test()
    
    if success:
        print("\n✅ Face detection test completed successfully!")
    else:
        print("\n❌ Face detection test failed")
        print("💡 Check camera connection and lighting conditions")

if __name__ == "__main__":
    main()
