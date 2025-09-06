#!/usr/bin/env python3

import cv2
import time
import os
import subprocess

def test_usb_camera_simple():
    """ทดสอบกล้อง USB แบบง่าย"""
    print("🔌 Testing USB Camera")
    print("=" * 30)
    
    # ตรวจสอบ video devices
    print("📹 Available video devices:")
    os.system("ls -la /dev/video* 2>/dev/null || echo 'No video devices found'")
    
    # ตรวจสอบ USB devices
    print("\n🔌 USB devices:")
    os.system("lsusb | grep -i camera || echo 'No USB cameras found'")
    
    # ทดสอบกล้องแต่ละตัว
    print("\n🔄 Testing cameras...")
    
    for i in range(5):
        print(f"\nTesting camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            print(f"✅ Camera {i} opened successfully")
            
            # ตั้งค่าความละเอียด
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # ดูข้อมูลกล้อง
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"   Resolution: {int(width)}x{int(height)}")
            print(f"   FPS: {fps}")
            
            # ลองอ่านเฟรม
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera {i} working - Frame shape: {frame.shape}")
                
                # แสดงภาพ 5 วินาที
                print(f"📺 Showing camera {i} for 5 seconds...")
                print("Press 'q' to quit early")
                
                start_time = time.time()
                while time.time() - start_time < 5:
                    ret, frame = cap.read()
                    if ret:
                        # เพิ่มข้อความบนภาพ
                        cv2.putText(frame, f"Camera {i} - USB Test", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        
                        cv2.imshow(f'USB Camera {i} Test', frame)
                        
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        print(f"❌ Cannot read frame from camera {i}")
                        break
                
                cv2.destroyAllWindows()
                cap.release()
                
                print(f"✅ Camera {i} test completed successfully!")
                return i
            else:
                print(f"❌ Camera {i} cannot read frame")
                cap.release()
        else:
            print(f"❌ Camera {i} cannot be opened")
    
    print("\n❌ No working USB cameras found")
    return None

def test_camera_with_different_backends():
    """ทดสอบกล้องด้วย backend ต่างๆ"""
    print("\n🔧 Testing different backends")
    print("=" * 40)
    
    backends = [
        (cv2.CAP_V4L2, "V4L2"),
        (cv2.CAP_GSTREAMER, "GStreamer"),
        (cv2.CAP_ANY, "Any")
    ]
    
    for backend, name in backends:
        print(f"\n🔄 Testing {name} backend...")
        
        for i in range(3):
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ {name} backend works with camera {i}")
                    cap.release()
                    return i, name
                cap.release()
    
    return None, None

def main():
    print("🔌 USB Camera Test Tool")
    print("🎯 Comprehensive USB camera testing")
    print("=" * 50)
    
    # ทดสอบกล้องแบบง่าย
    working_camera = test_usb_camera_simple()
    
    if working_camera is not None:
        print(f"\n🎉 SUCCESS: Camera {working_camera} is working!")
        print(f"💡 Use camera index {working_camera} in your application")
        
        # ทดสอบ backend ต่างๆ
        backend_camera, backend_name = test_camera_with_different_backends()
        if backend_camera is not None:
            print(f"🔧 Best backend: {backend_name} with camera {backend_camera}")
    else:
        print("\n❌ No working USB cameras found")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check USB connection")
        print("2. Try different USB port")
        print("3. Check camera permissions: sudo usermod -a -G video $USER")
        print("4. Reboot system")
        print("5. Run: python3 diagnose_camera.py")
        print("6. Check if camera is supported by Linux")

if __name__ == "__main__":
    main()
