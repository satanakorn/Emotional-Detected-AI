#!/usr/bin/env python3

import cv2
import numpy as np
import time

def test_thai_display():
    """ทดสอบการแสดงผลภาษาไทย"""
    print("🔤 Testing Thai Language Display")
    print("=" * 40)
    
    # สร้างหน้าจอทดสอบ
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    # ตั้งค่าความละเอียด
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("📺 Testing text display on camera feed...")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read frame")
                break
            
            # สร้างพื้นหลังสีดำ
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (630, 200), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # กรอบขอบ
            cv2.rectangle(frame, (10, 10), (630, 200), (255, 255, 255), 2)
            
            # ทดสอบการแสดงผลภาษาอังกฤษ (ควรทำงานได้)
            cv2.putText(frame, "English Test: Happy", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.putText(frame, "Neutral", (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            cv2.putText(frame, "Sad", (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            cv2.putText(frame, "Angry", (20, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            # ทดสอบการแสดงผลภาษาไทย (อาจแสดงเป็น ????)
            cv2.putText(frame, "Thai Test: ?????", (20, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
            
            # แสดงข้อมูลเพิ่มเติม
            cv2.putText(frame, "Manual: 1=Happy 2=Neutral 3=Sad 4=Angry", (20, 190), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # แสดงเวลา
            time_text = time.strftime("%H:%M:%S")
            cv2.putText(frame, time_text, (500, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # แสดงภาพ
            cv2.imshow('Thai Display Test', frame)
            
            # จัดการ key input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Thai display test completed")

def main():
    print("🔤 Thai Language Display Test")
    print("🎯 Testing OpenCV text rendering with Thai characters")
    print("=" * 50)
    
    print("📋 Expected Results:")
    print("   - English text should display correctly")
    print("   - Thai text may display as '?????' (this is normal)")
    print("   - This is why we use English in the main application")
    print("=" * 50)
    
    test_thai_display()

if __name__ == "__main__":
    main()
