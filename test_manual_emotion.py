#!/usr/bin/env python3

import cv2
import time
import numpy as np

def test_manual_emotion_system():
    """ทดสอบระบบ manual emotion input"""
    print("🎯 Manual Emotion Input Test")
    print("=" * 40)
    
    # สร้างหน้าจอทดสอบ
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    # ตั้งค่าความละเอียด
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # ตัวแปรสำหรับ manual emotion
    manual_emotion = None
    manual_confidence = 0.0
    last_manual_time = 0
    
    def set_manual_emotion(emotion, confidence):
        nonlocal manual_emotion, manual_confidence, last_manual_time
        manual_emotion = emotion
        manual_confidence = confidence
        last_manual_time = time.time()
        print(f"🎯 Manual emotion set: {emotion} ({confidence:.1f}%)")
    
    def get_emotion_assessment(confidence):
        """ประเมินอารมณ์ตามเกณฑ์ใหม่"""
        if confidence >= 80:
            return "สุข (Happy)", "★★★★★", 5
        elif confidence >= 50:
            return "เฉยๆ (Neutral)", "★★★☆☆", 3
        elif confidence >= 30:
            return "เศร้า (Sad)", "★★☆☆☆", 2
        else:
            return "โกรธ (Angry)", "★☆☆☆☆", 1
    
    def get_current_emotion():
        """รับอารมณ์ปัจจุบัน (Manual)"""
        current_time = time.time()
        
        # ตรวจสอบ manual emotion (ใช้ได้ 5 วินาที)
        if (manual_emotion and 
            current_time - last_manual_time < 5.0):
            assessed_emotion, satisfaction_text, satisfaction_level = get_emotion_assessment(manual_confidence)
            return (
                f"[Manual] {assessed_emotion}",
                manual_confidence,
                satisfaction_level,
                satisfaction_text
            )
        
        return None
    
    def add_overlay_info(frame, emotion, confidence, satisfaction_level, satisfaction_text):
        """เพิ่มข้อมูลลงบนเฟรม"""
        if frame is None:
            return frame
        
        height, width = frame.shape[:2]
        
        # วาดกรอบข้อมูลพื้นหลังโปร่งใส
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (width-10, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # กรอบขอบ
        cv2.rectangle(frame, (10, 10), (width-10, 250), (255, 255, 255), 2)
        
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
        
        # แสดง manual controls
        manual_text = "Manual: 1=Happy 2=Neutral 3=Sad 4=Angry"
        cv2.putText(frame, manual_text, (20, 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # แสดงสถานะ manual mode
        if manual_emotion and time.time() - last_manual_time < 5.0:
            manual_status = f"Manual Active: {manual_emotion}"
            cv2.putText(frame, manual_status, (20, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # เวลา
        time_text = time.strftime("%H:%M:%S")
        cv2.putText(frame, time_text, (width-150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return frame
    
    print("🎮 Manual Emotion Test Started")
    print("📋 Controls:")
    print("   - กด '1' = สุข (Happy) 90%")
    print("   - กด '2' = เฉยๆ (Neutral) 60%")
    print("   - กด '3' = เศร้า (Sad) 35%")
    print("   - กด '4' = โกรธ (Angry) 10%")
    print("   - กด 'q' = ออก")
    print("=" * 40)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Cannot read frame")
                break
            
            # ตรวจสอบ manual emotion
            manual_result = get_current_emotion()
            if manual_result:
                emotion, confidence, satisfaction_level, satisfaction_text = manual_result
            else:
                emotion, confidence, satisfaction_level, satisfaction_text = "รอการประเมิน (Waiting)", 0.0, 0, ""
            
            # เพิ่มข้อมูลลงบนเฟรม
            display_frame = add_overlay_info(
                frame, emotion, confidence, satisfaction_level, satisfaction_text
            )
            
            # แสดงภาพ
            cv2.imshow('Manual Emotion Test', display_frame)
            
            # จัดการ key input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1'):
                set_manual_emotion("สุข (Happy)", 90.0)
            elif key == ord('2'):
                set_manual_emotion("เฉยๆ (Neutral)", 60.0)
            elif key == ord('3'):
                set_manual_emotion("เศร้า (Sad)", 35.0)
            elif key == ord('4'):
                set_manual_emotion("โกรธ (Angry)", 10.0)
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Manual emotion test completed")

def main():
    print("🎭 Manual Emotion Input Test System")
    print("🎯 Testing keyboard-based emotion assessment")
    print("=" * 50)
    
    test_manual_emotion_system()

if __name__ == "__main__":
    main()
