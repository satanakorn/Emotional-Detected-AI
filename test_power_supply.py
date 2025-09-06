#!/usr/bin/env python3

import subprocess
import os
import time

def test_power_supply():
    """ทดสอบแหล่งจ่ายไฟ"""
    print("⚡ Power Supply Test")
    print("=" * 25)
    
    # ตรวจสอบ voltage
    try:
        result = subprocess.run(['vcgencmd', 'measure_volts'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            voltage_str = result.stdout.strip()
            print(f"✅ {voltage_str}")
            
            # แปลงเป็นตัวเลข
            try:
                voltage = float(voltage_str.split('=')[1].replace('V', ''))
                if voltage >= 4.8:
                    print("✅ Voltage is good (>= 4.8V)")
                elif voltage >= 4.6:
                    print("⚠️ Voltage is low but acceptable (4.6-4.8V)")
                else:
                    print("❌ Voltage is too low (< 4.6V) - Power supply insufficient!")
            except:
                print("⚠️ Cannot parse voltage")
        else:
            print("❌ Cannot measure voltage")
    except:
        print("❌ vcgencmd not available")
    
    # ตรวจสอบ temperature
    try:
        result = subprocess.run(['vcgencmd', 'measure_temp'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            temp_str = result.stdout.strip()
            print(f"✅ {temp_str}")
            
            # แปลงเป็นตัวเลข
            try:
                temp = float(temp_str.split('=')[1].replace("'C", ''))
                if temp < 70:
                    print("✅ Temperature is good (< 70°C)")
                elif temp < 80:
                    print("⚠️ Temperature is warm (70-80°C)")
                else:
                    print("❌ Temperature is too high (> 80°C)")
            except:
                print("⚠️ Cannot parse temperature")
        else:
            print("❌ Cannot measure temperature")
    except:
        print("❌ vcgencmd not available")
    
    # ตรวจสอบ throttling
    try:
        result = subprocess.run(['vcgencmd', 'get_throttled'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            throttled = result.stdout.strip()
            print(f"✅ {throttled}")
            
            if throttled == "throttled=0x0":
                print("✅ No throttling detected - Power supply is adequate")
            else:
                print("❌ Throttling detected - Power supply is insufficient!")
                print("💡 Use official Raspberry Pi power adapter (5V, 3A)")
        else:
            print("❌ Cannot check throttling")
    except:
        print("❌ vcgencmd not available")

def test_usb_power():
    """ทดสอบพลังงาน USB"""
    print("\n🔌 USB Power Test")
    print("=" * 20)
    
    # ตรวจสอบ USB devices
    try:
        result = subprocess.run(['lsusb'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ USB devices detected:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ Cannot list USB devices")
    except:
        print("❌ lsusb not available")
    
    # ตรวจสอบ USB power
    try:
        result = subprocess.run(['lsusb', '-v'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            power_info = []
            for line in lines:
                if 'MaxPower' in line:
                    power_info.append(line.strip())
            
            if power_info:
                print("✅ USB power information:")
                for info in power_info:
                    print(f"   {info}")
            else:
                print("⚠️ No USB power information available")
        else:
            print("❌ Cannot get USB power info")
    except:
        print("❌ lsusb -v not available")

def test_camera_simple():
    """ทดสอบกล้องแบบง่าย"""
    print("\n📷 Simple Camera Test")
    print("=" * 25)
    
    try:
        import cv2
        
        for i in range(3):
            print(f"Testing camera {i}...")
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                print(f"✅ Camera {i} opened successfully")
                
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {i} working - Shape: {frame.shape}")
                    cap.release()
                    return True
                else:
                    print(f"❌ Camera {i} cannot read frame")
                
                cap.release()
            else:
                print(f"❌ Camera {i} cannot be opened")
        
        print("❌ No working cameras found")
        return False
        
    except ImportError:
        print("❌ OpenCV not installed")
        return False
    except Exception as e:
        print(f"❌ Camera test error: {e}")
        return False

def main():
    print("⚡ Power Supply & Camera Test")
    print("🎯 Quick diagnostic for camera issues")
    print("=" * 50)
    
    # ทดสอบแหล่งจ่ายไฟ
    test_power_supply()
    
    # ทดสอบพลังงาน USB
    test_usb_power()
    
    # ทดสอบกล้อง
    camera_works = test_camera_simple()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    
    if camera_works:
        print("✅ Camera is working!")
        print("💡 If you still have issues, try:")
        print("   - Different USB port")
        print("   - Different USB cable")
        print("   - Reboot system")
    else:
        print("❌ Camera is not working")
        print("💡 Possible solutions:")
        print("   1. Check power supply - use official adapter")
        print("   2. Check USB cable - try different cable")
        print("   3. Check camera permissions:")
        print("      sudo usermod -a -G video $USER")
        print("   4. Enable camera:")
        print("      sudo raspi-config")
        print("   5. Add to /boot/config.txt:")
        print("      camera_auto_detect=1")
        print("   6. Reboot system")
        print("   7. Try different USB port")

if __name__ == "__main__":
    main()
