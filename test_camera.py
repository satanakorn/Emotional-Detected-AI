#!/usr/bin/env python3

import cv2
import os
import subprocess
import time

def test_camera_hardware():
    """ทดสอบฮาร์ดแวร์กล้อง Raspberry Pi 4"""
    print("🔍 Testing Raspberry Pi 4 Camera Hardware")
    print("=" * 50)
    
    # ตรวจสอบ libcamera
    print("📷 Testing libcamera...")
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

def test_opencv_camera():
    """ทดสอบกล้องด้วย OpenCV"""
    print("🔄 Testing OpenCV camera access...")
    
    # ลองใช้ GStreamer pipeline
    print("Trying GStreamer pipeline...")
    gst_pipeline = (
        "libcamerasrc ! "
        "video/x-raw,width=640,height=480,framerate=30/1 ! "
        "videoconvert ! appsink"
    )
    
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✅ GStreamer pipeline successful - Shape: {frame.shape}")
            cap.release()
            return True
        cap.release()
    
    # ลองใช้ V4L2
    print("Trying V4L2 direct access...")
    os.system("sudo modprobe bcm2835-v4l2 2>/dev/null")
    time.sleep(2)
    
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✅ V4L2 method successful - Shape: {frame.shape}")
            cap.release()
            return True
        cap.release()
    
    # ลองกล้อง USB
    print("Trying USB cameras...")
    for i in range(4):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ USB camera found at index {i} - Shape: {frame.shape}")
                cap.release()
                return True
            cap.release()
    
    print("❌ No camera found with OpenCV")
    return False

def test_picamera2():
    """ทดสอบ PiCamera2"""
    print("🔄 Testing PiCamera2...")
    
    try:
        from picamera2 import Picamera2
        print("✅ PiCamera2 library available")
        
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            controls={"FrameRate": 30}
        )
        picam2.configure(config)
        picam2.start()
        time.sleep(2)
        
        frame = picam2.capture_array()
        if frame is not None and frame.size > 0:
            print(f"✅ PiCamera2 successful - Shape: {frame.shape}")
            picam2.stop()
            return True
        else:
            picam2.stop()
            return False
            
    except ImportError:
        print("❌ PiCamera2 library not available")
        return False
    except Exception as e:
        print(f"❌ PiCamera2 error: {e}")
        return False

def main():
    print("🍓 Raspberry Pi 4 Camera Test")
    print("🎭 Testing all camera methods")
    print("=" * 60)
    
    # ทดสอบฮาร์ดแวร์
    test_camera_hardware()
    
    # ทดสอบ PiCamera2
    picamera2_works = test_picamera2()
    
    # ทดสอบ OpenCV
    opencv_works = test_opencv_camera()
    
    # สรุปผล
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    print(f"PiCamera2: {'✅ Working' if picamera2_works else '❌ Failed'}")
    print(f"OpenCV: {'✅ Working' if opencv_works else '❌ Failed'}")
    
    if not picamera2_works and not opencv_works:
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check camera cable connection")
        print("2. Enable camera: sudo raspi-config")
        print("3. Add to /boot/config.txt: camera_auto_detect=1")
        print("4. Increase GPU memory: gpu_mem=128")
        print("5. Reboot system: sudo reboot")
        print("6. Run setup script: ./setup_raspberry_pi.sh")
    else:
        print("\n🎉 Camera is working! You can run the emotion detection.")

if __name__ == "__main__":
    main()
