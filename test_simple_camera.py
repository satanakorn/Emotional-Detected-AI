#!/usr/bin/env python3

import cv2
import time
import os

def test_simple_camera():
    """ทดสอบกล้องแบบง่าย"""
    print("📷 Simple Camera Test")
    print("=" * 30)
    
    print("🔍 Testing camera access methods...")
    
    # ทดสอบกล้องแบบธรรมดา
    print("\n🔄 Testing simple OpenCV camera access...")
    for i in range(5):
        print(f"   Testing camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            print(f"✅ Camera {i} opened successfully")
            
            # ตั้งค่าความละเอียด
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # ลองอ่านเฟรม
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera {i} working - Frame shape: {frame.shape}")
                
                # แสดงภาพ 3 วินาที
                print(f"📺 Showing camera {i} for 3 seconds...")
                print("Press 'q' to quit early")
                
                start_time = time.time()
                while time.time() - start_time < 3:
                    ret, frame = cap.read()
                    if ret:
                        # เพิ่มข้อความบนภาพ
                        cv2.putText(frame, f"Camera {i} - Simple Test", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        
                        cv2.imshow(f'Simple Camera {i} Test', frame)
                        
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
    
    print("\n❌ No working cameras found with simple method")
    return None

def test_video_devices():
    """ทดสอบ video devices"""
    print("\n📹 Testing video devices...")
    
    # ตรวจสอบ video devices
    import glob
    video_devices = glob.glob('/dev/video*')
    if video_devices:
        print(f"Found video devices: {video_devices}")
        
        for device in video_devices:
            try:
                device_num = int(device.split('video')[1])
                print(f"Testing {device} (index {device_num})...")
                
                cap = cv2.VideoCapture(device_num)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ {device} working - Shape: {frame.shape}")
                        cap.release()
                        return device_num
                    cap.release()
                else:
                    print(f"❌ {device} cannot be opened")
            except Exception as e:
                print(f"❌ Error testing {device}: {e}")
    else:
        print("No video devices found")
    
    return None

def test_usb_devices():
    """ทดสอบ USB devices"""
    print("\n🔌 Testing USB devices...")
    
    try:
        import subprocess
        result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("USB devices:")
            print(result.stdout)
            
            if 'camera' in result.stdout.lower() or 'webcam' in result.stdout.lower():
                print("✅ USB camera detected in lsusb")
                return True
            else:
                print("⚠️ No USB camera found in lsusb")
        else:
            print("❌ Cannot run lsusb")
    except Exception as e:
        print(f"❌ Error running lsusb: {e}")
    
    return False

def main():
    print("📷 Simple Camera Detection Test")
    print("🎯 Testing basic camera access without complex backends")
    print("=" * 60)
    
    # ทดสอบกล้องแบบธรรมดา
    working_camera = test_simple_camera()
    
    if working_camera is not None:
        print(f"\n🎉 SUCCESS: Camera {working_camera} is working!")
        print(f"💡 Use camera index {working_camera} in your application")
    else:
        print("\n❌ No working cameras found with simple method")
        
        # ทดสอบ video devices
        video_camera = test_video_devices()
        
        if video_camera is not None:
            print(f"\n🎉 SUCCESS: Video device {video_camera} is working!")
        else:
            # ทดสอบ USB devices
            usb_detected = test_usb_devices()
            
            if usb_detected:
                print("\n⚠️ USB camera detected but not accessible")
                print("🔧 Try running with sudo or check permissions")
            else:
                print("\n❌ No cameras detected")
                print("\n🔧 Troubleshooting steps:")
                print("1. Check USB connection")
                print("2. Try different USB port")
                print("3. Check camera permissions: sudo usermod -a -G video $USER")
                print("4. Reboot system")
                print("5. Run: python3 diagnose_camera.py")

if __name__ == "__main__":
    main()
