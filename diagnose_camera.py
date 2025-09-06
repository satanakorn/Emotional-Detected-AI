#!/usr/bin/env python3

import cv2
import os
import subprocess
import time
import sys

def check_system_info():
    """ตรวจสอบข้อมูลระบบ"""
    print("🔍 System Information")
    print("=" * 40)
    
    # ตรวจสอบ OS
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if 'PRETTY_NAME' in line:
                    print(f"OS: {line.split('=')[1].strip().strip('\"')}")
                    break
    except:
        print("OS: Unknown")
    
    # ตรวจสอบ Python version
    print(f"Python: {sys.version}")
    
    # ตรวจสอบ OpenCV version
    try:
        import cv2
        print(f"OpenCV: {cv2.__version__}")
    except ImportError:
        print("OpenCV: Not installed")
    
    print("=" * 40)

def check_picamera2():
    """ตรวจสอบ PiCamera2"""
    print("📷 PiCamera2 Check")
    print("=" * 30)
    
    try:
        from picamera2 import Picamera2
        print("✅ PiCamera2 library available")
        
        # ลองสร้าง instance
        try:
            picam2 = Picamera2()
            print("✅ PiCamera2 instance created")
            
            # ลองดู cameras
            try:
                cameras = picam2.camera_properties
                print(f"📷 Available cameras: {len(cameras)}")
                for i, camera in enumerate(cameras):
                    print(f"   Camera {i}: {camera}")
            except Exception as e:
                print(f"⚠️ Cannot get camera properties: {e}")
            
            # ลอง configure
            try:
                config = picam2.create_preview_configuration(
                    main={"size": (640, 480), "format": "RGB888"}
                )
                picam2.configure(config)
                print("✅ PiCamera2 configuration successful")
                
                # ลอง start
                picam2.start()
                print("✅ PiCamera2 started")
                
                # ลอง capture
                time.sleep(1)
                frame = picam2.capture_array()
                if frame is not None:
                    print(f"✅ PiCamera2 capture successful - Shape: {frame.shape}")
                else:
                    print("❌ PiCamera2 capture failed - No frame")
                
                picam2.stop()
                print("✅ PiCamera2 stopped")
                
            except Exception as e:
                print(f"❌ PiCamera2 operation failed: {e}")
                
        except Exception as e:
            print(f"❌ PiCamera2 instance creation failed: {e}")
            
    except ImportError as e:
        print(f"❌ PiCamera2 library not available: {e}")
        print("💡 Install with: sudo apt install python3-picamera2")

def check_usb_cameras():
    """ตรวจสอบกล้อง USB"""
    print("\n🔌 USB Camera Check")
    print("=" * 30)
    
    # ตรวจสอบ video devices
    print("📹 Video devices:")
    os.system("ls -la /dev/video* 2>/dev/null || echo '⚠️ No video devices found'")
    
    # ตรวจสอบ USB devices
    print("\n🔌 USB devices:")
    os.system("lsusb | grep -i camera || echo '⚠️ No USB cameras found'")
    
    # ทดสอบ OpenCV กับ USB cameras
    print("\n🔄 Testing OpenCV with USB cameras...")
    
    for i in range(5):  # ลอง 5 devices
        print(f"Testing /dev/video{i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            print(f"✅ /dev/video{i} opened")
            
            # ตั้งค่าความละเอียด
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # ลองอ่านเฟรม
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ /dev/video{i} working - Shape: {frame.shape}")
                
                # ดูข้อมูลเพิ่มเติม
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                fps = cap.get(cv2.CAP_PROP_FPS)
                print(f"   Resolution: {int(width)}x{int(height)}")
                print(f"   FPS: {fps}")
                
                cap.release()
                return i  # คืนค่า index ของกล้องที่ทำงาน
            else:
                print(f"❌ /dev/video{i} cannot read frame")
            
            cap.release()
        else:
            print(f"❌ /dev/video{i} cannot open")
    
    return None

def check_libcamera():
    """ตรวจสอบ libcamera"""
    print("\n📷 libcamera Check")
    print("=" * 30)
    
    try:
        result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ libcamera tools available")
            print("Available cameras:")
            print(result.stdout)
        else:
            print("⚠️ libcamera available but no cameras detected")
            print("Error:", result.stderr)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"❌ libcamera tools not found: {e}")

def check_v4l2():
    """ตรวจสอบ V4L2"""
    print("\n📹 V4L2 Check")
    print("=" * 20)
    
    # ตรวจสอบ v4l2-ctl
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ v4l2-ctl available")
            print("V4L2 devices:")
            print(result.stdout)
        else:
            print("⚠️ v4l2-ctl available but no devices")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ v4l2-ctl not found")
    
    # ตรวจสอบ bcm2835-v4l2 module
    print("\n🔧 Checking bcm2835-v4l2 module...")
    os.system("lsmod | grep bcm2835 || echo '⚠️ bcm2835-v4l2 module not loaded'")
    
    # ลองโหลด module
    print("🔄 Trying to load bcm2835-v4l2...")
    os.system("sudo modprobe bcm2835-v4l2 2>/dev/null && echo '✅ Module loaded' || echo '❌ Cannot load module'")

def main():
    print("🔍 Camera Diagnostic Tool")
    print("🎯 Comprehensive camera detection for Raspberry Pi")
    print("=" * 60)
    
    # ตรวจสอบข้อมูลระบบ
    check_system_info()
    
    # ตรวจสอบ PiCamera2 (สำหรับ CSI camera)
    check_picamera2()
    
    # ตรวจสอบ libcamera
    check_libcamera()
    
    # ตรวจสอบ V4L2
    check_v4l2()
    
    # ตรวจสอบกล้อง USB
    working_camera = check_usb_cameras()
    
    # สรุปผล
    print("\n📊 Diagnostic Summary")
    print("=" * 30)
    
    if working_camera is not None:
        print(f"✅ Working USB camera found at index {working_camera}")
        print("💡 Use this camera index in your application")
    else:
        print("❌ No working USB cameras found")
    
    print("\n🔧 Troubleshooting Tips:")
    print("1. For USB cameras: Use OpenCV with camera index")
    print("2. For Pi Camera Module: Use PiCamera2 (CSI connector)")
    print("3. Check camera permissions: sudo usermod -a -G video $USER")
    print("4. Reboot after connecting camera")
    print("5. Try different USB ports")

if __name__ == "__main__":
    main()
