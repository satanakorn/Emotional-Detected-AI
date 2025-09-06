#!/usr/bin/env python3

import cv2
import numpy as np
import time

def test_fullscreen_display():
    """ทดสอบการแสดงผลเต็มจอ"""
    print("🖥️ Testing Fullscreen Display")
    print("=" * 40)
    
    # สร้างหน้าจอทดสอบ
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    # ตั้งค่าความละเอียด
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    fullscreen_mode = True
    
    print("📺 Testing fullscreen display...")
    print("Press 'f' to toggle fullscreen")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read frame")
                break
            
            height, width = frame.shape[:2]
            
            # สร้างพื้นหลังสีดำ
            overlay = frame.copy()
            overlay_height = max(200, int(height * 0.3))
            cv2.rectangle(overlay, (10, 10), (width-10, overlay_height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # กรอบขอบ
            cv2.rectangle(frame, (10, 10), (width-10, overlay_height), (255, 255, 255), 2)
            
            # คำนวณขนาดข้อความตามขนาดหน้าจอ
            font_scale = max(0.8, min(2.0, width / 800))
            font_thickness = max(1, int(width / 400))
            
            # ทดสอบการแสดงผลข้อความ
            cv2.putText(frame, "Fullscreen Test", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), font_thickness)
            
            cv2.putText(frame, "Score: *****", (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, (0, 255, 255), font_thickness)
            
            cv2.putText(frame, "Happy", (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, (255, 255, 0), font_thickness)
            
            cv2.putText(frame, "Confidence: 90.00%", (20, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, (0, 255, 255), font_thickness)
            
            # แสดงสถานะ fullscreen
            mode_text = "Fullscreen" if fullscreen_mode else "Window"
            cv2.putText(frame, f"Mode: {mode_text}", (20, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (255, 0, 255), font_thickness)
            
            # แสดงเวลา
            time_text = time.strftime("%H:%M:%S")
            time_x = max(width - 200, width - int(width * 0.3))
            cv2.putText(frame, time_text, (time_x, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, (255, 255, 0), font_thickness)
            
            # แสดงภาพ
            cv2.namedWindow('Fullscreen Test', cv2.WINDOW_NORMAL)
            if fullscreen_mode:
                cv2.setWindowProperty('Fullscreen Test', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty('Fullscreen Test', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.imshow('Fullscreen Test', frame)
            
            # จัดการ key input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('f'):
                fullscreen_mode = not fullscreen_mode
                if fullscreen_mode:
                    print("🖥️ Switched to fullscreen mode")
                else:
                    print("🖥️ Switched to window mode")
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Fullscreen test completed")

def main():
    print("🖥️ Fullscreen Display Test")
    print("🎯 Testing fullscreen mode and text scaling")
    print("=" * 50)
    
    print("📋 Expected Results:")
    print("   - Text should scale properly in fullscreen")
    print("   - Score should display as ***** (not ?????)")
    print("   - All text should be readable")
    print("=" * 50)
    
    test_fullscreen_display()

if __name__ == "__main__":
    main()
