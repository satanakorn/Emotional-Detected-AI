#!/usr/bin/env python3

import cv2
import os
import subprocess
import time
import sys

def check_system_power():
    """ตรวจสอบพลังงานระบบ"""
    print("⚡ System Power Check")
    print("=" * 30)
    
    try:
        # ตรวจสอบ voltage
        result = subprocess.run(['vcgencmd', 'measure_volts'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Voltage: {result.stdout.strip()}")
        else:
            print("⚠️ Cannot measure voltage")
    except:
        print("⚠️ vcgencmd not available")
    
    try:
        # ตรวจสอบ temperature
        result = subprocess.run(['vcgencmd', 'measure_temp'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Temperature: {result.stdout.strip()}")
        else:
            print("⚠️ Cannot measure temperature")
    except:
        print("⚠️ vcgencmd not available")
    
    try:
        # ตรวจสอบ throttling
        result = subprocess.run(['vcgencmd', 'get_throttled'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            throttled = result.stdout.strip()
            print(f"✅ Throttling: {throttled}")
            if throttled != "throttled=0x0":
                print("⚠️ System is throttled - power supply may be insufficient")
        else:
            print("⚠️ Cannot check throttling")
    except:
        print("⚠️ vcgencmd not available")

def check_usb_power():
    """ตรวจสอบพลังงาน USB"""
    print("\n🔌 USB Power Check")
    print("=" * 25)
    
    try:
        # ตรวจสอบ USB devices
        result = subprocess.run(['lsusb', '-v'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'MaxPower' in line:
                    print(f"   {line.strip()}")
                elif 'bcdUSB' in line:
                    print(f"   {line.strip()}")
        else:
            print("⚠️ Cannot check USB power")
    except:
        print("⚠️ lsusb not available")
    
    # ตรวจสอบ USB current
    try:
        if os.path.exists('/sys/kernel/debug/usb/devices'):
            with open('/sys/kernel/debug/usb/devices', 'r') as f:
                content = f.read()
                if 'MaxPower' in content:
                    print("✅ USB power information available")
                else:
                    print("⚠️ USB power information not available")
        else:
            print("⚠️ USB debug info not available")
    except:
        print("⚠️ Cannot access USB debug info")

def check_camera_permissions():
    """ตรวจสอบสิทธิ์การเข้าถึงกล้อง"""
    print("\n🔐 Camera Permissions Check")
    print("=" * 35)
    
    # ตรวจสอบ video group
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            groups = result.stdout.strip()
            print(f"✅ User groups: {groups}")
            if 'video' in groups:
                print("✅ User is in video group")
            else:
                print("⚠️ User is NOT in video group")
                print("💡 Run: sudo usermod -a -G video $USER")
        else:
            print("⚠️ Cannot check user groups")
    except:
        print("⚠️ Cannot check user groups")
    
    # ตรวจสอบ video devices permissions
    import glob
    video_devices = glob.glob('/dev/video*')
    if video_devices:
        print(f"\n📹 Video devices permissions:")
        for device in video_devices:
            try:
                stat = os.stat(device)
                print(f"   {device}: {oct(stat.st_mode)[-3:]}")
            except:
                print(f"   {device}: Cannot check permissions")
    else:
        print("⚠️ No video devices found")

def test_camera_with_different_methods():
    """ทดสอบกล้องด้วยวิธีต่างๆ"""
    print("\n📷 Camera Access Test")
    print("=" * 30)
    
    methods = [
        ("Simple OpenCV", lambda i: cv2.VideoCapture(i)),
        ("OpenCV with V4L2", lambda i: cv2.VideoCapture(i, cv2.CAP_V4L2)),
        ("OpenCV with GStreamer", lambda i: cv2.VideoCapture(i, cv2.CAP_GSTREAMER))
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 Testing {method_name}...")
        working_cameras = []
        
        for i in range(5):
            try:
                cap = method_func(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"   ✅ Camera {i}: Working - Shape: {frame.shape}")
                        working_cameras.append(i)
                    else:
                        print(f"   ❌ Camera {i}: Cannot read frame")
                    cap.release()
                else:
                    print(f"   ❌ Camera {i}: Cannot open")
            except Exception as e:
                print(f"   ❌ Camera {i}: Error - {e}")
        
        if working_cameras:
            print(f"✅ {method_name}: {len(working_cameras)} cameras working")
        else:
            print(f"❌ {method_name}: No cameras working")

def check_camera_hardware():
    """ตรวจสอบฮาร์ดแวร์กล้อง"""
    print("\n🔧 Camera Hardware Check")
    print("=" * 35)
    
    # ตรวจสอบ libcamera
    try:
        result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ libcamera tools available")
            print("📷 Available cameras:")
            print(result.stdout)
        else:
            print("⚠️ libcamera available but no cameras detected")
    except:
        print("❌ libcamera tools not found")
    
    # ตรวจสอบ vcgencmd camera
    try:
        result = subprocess.run(['vcgencmd', 'get_camera'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Camera status: {result.stdout.strip()}")
        else:
            print("⚠️ Cannot get camera status")
    except:
        print("⚠️ vcgencmd not available")
    
    # ตรวจสอบ config.txt
    try:
        if os.path.exists('/boot/config.txt'):
            with open('/boot/config.txt', 'r') as f:
                content = f.read()
                camera_settings = []
                for line in content.split('\n'):
                    if 'camera' in line.lower() or 'start_x' in line or 'gpu_mem' in line:
                        camera_settings.append(line.strip())
                
                if camera_settings:
                    print("📝 Camera settings in config.txt:")
                    for setting in camera_settings:
                        print(f"   {setting}")
                else:
                    print("⚠️ No camera settings found in config.txt")
        else:
            print("⚠️ config.txt not found")
    except:
        print("⚠️ Cannot read config.txt")

def check_system_resources():
    """ตรวจสอบทรัพยากรระบบ"""
    print("\n💻 System Resources Check")
    print("=" * 35)
    
    # ตรวจสอบ memory
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemAvailable' in line or 'MemFree' in line:
                    print(f"   {line.strip()}")
    except:
        print("⚠️ Cannot check memory")
    
    # ตรวจสอบ CPU load
    try:
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip()
            print(f"   CPU Load: {load}")
    except:
        print("⚠️ Cannot check CPU load")
    
    # ตรวจสอบ disk space
    try:
        result = subprocess.run(['df', '-h', '/'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   Disk space: {result.stdout.split('\\n')[1]}")
        else:
            print("⚠️ Cannot check disk space")
    except:
        print("⚠️ Cannot check disk space")

def main():
    print("🔍 Camera Power & Hardware Diagnostic Tool")
    print("🎯 Comprehensive camera troubleshooting")
    print("=" * 60)
    
    # ตรวจสอบพลังงานระบบ
    check_system_power()
    
    # ตรวจสอบพลังงาน USB
    check_usb_power()
    
    # ตรวจสอบสิทธิ์กล้อง
    check_camera_permissions()
    
    # ตรวจสอบฮาร์ดแวร์กล้อง
    check_camera_hardware()
    
    # ตรวจสอบทรัพยากรระบบ
    check_system_resources()
    
    # ทดสอบกล้องด้วยวิธีต่างๆ
    test_camera_with_different_methods()
    
    print("\n" + "=" * 60)
    print("📋 Troubleshooting Summary:")
    print("1. Check power supply - use official Raspberry Pi power adapter")
    print("2. Check USB cable - try different cable")
    print("3. Check camera permissions - run: sudo usermod -a -G video $USER")
    print("4. Enable camera - run: sudo raspi-config")
    print("5. Check config.txt - add: camera_auto_detect=1")
    print("6. Reboot system after changes")
    print("7. Try different USB port")
    print("8. Check if camera works on other computer")

if __name__ == "__main__":
    main()
