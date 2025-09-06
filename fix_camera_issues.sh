#!/bin/bash

echo "🔧 Camera Issues Fix Script"
echo "=========================="

# ตรวจสอบว่าทำงานด้วย sudo หรือไม่
if [ "$EUID" -ne 0 ]; then
    echo "⚠️ This script needs to be run with sudo"
    echo "Usage: sudo ./fix_camera_issues.sh"
    exit 1
fi

echo "🔍 Checking current camera status..."

# ตรวจสอบ camera status
echo "📷 Current camera status:"
vcgencmd get_camera 2>/dev/null || echo "⚠️ Cannot get camera status"

# ตรวจสอบ video devices
echo "📹 Video devices:"
ls -la /dev/video* 2>/dev/null || echo "⚠️ No video devices found"

# ตรวจสอบ USB devices
echo "🔌 USB devices:"
lsusb | grep -i camera || echo "⚠️ No USB cameras found"

echo ""
echo "🔧 Applying fixes..."

# 1. เพิ่ม user เข้า video group
echo "1. Adding user to video group..."
usermod -a -G video $SUDO_USER
echo "✅ User added to video group"

# 2. เปิดใช้งาน camera ใน config.txt
echo "2. Enabling camera in config.txt..."
if [ -f /boot/config.txt ]; then
    # สำรองไฟล์เดิม
    cp /boot/config.txt /boot/config.txt.backup
    
    # เพิ่มการตั้งค่ากล้อง
    if ! grep -q "camera_auto_detect=1" /boot/config.txt; then
        echo "camera_auto_detect=1" >> /boot/config.txt
        echo "✅ Added camera_auto_detect=1"
    else
        echo "✅ camera_auto_detect=1 already exists"
    fi
    
    if ! grep -q "start_x=1" /boot/config.txt; then
        echo "start_x=1" >> /boot/config.txt
        echo "✅ Added start_x=1"
    else
        echo "✅ start_x=1 already exists"
    fi
    
    if ! grep -q "gpu_mem=128" /boot/config.txt; then
        echo "gpu_mem=128" >> /boot/config.txt
        echo "✅ Added gpu_mem=128"
    else
        echo "✅ gpu_mem=128 already exists"
    fi
else
    echo "⚠️ /boot/config.txt not found"
fi

# 3. โหลด camera modules
echo "3. Loading camera modules..."
modprobe bcm2835-v4l2 2>/dev/null && echo "✅ bcm2835-v4l2 loaded" || echo "⚠️ bcm2835-v4l2 not available"
modprobe uvcvideo 2>/dev/null && echo "✅ uvcvideo loaded" || echo "⚠️ uvcvideo not available"

# 4. ตั้งค่า permissions สำหรับ video devices
echo "4. Setting video device permissions..."
for device in /dev/video*; do
    if [ -e "$device" ]; then
        chmod 666 "$device"
        echo "✅ Set permissions for $device"
    fi
done

# 5. ตั้งค่า USB permissions
echo "5. Setting USB permissions..."
if [ -d /etc/udev/rules.d ]; then
    cat > /etc/udev/rules.d/99-camera.rules << EOF
# Camera permissions
SUBSYSTEM=="video4linux", GROUP="video", MODE="0664"
SUBSYSTEM=="usb", ATTRS{idVendor}=="*", ATTRS{idProduct}=="*", GROUP="video", MODE="0664"
EOF
    echo "✅ Created camera udev rules"
    udevadm control --reload-rules
    udevadm trigger
else
    echo "⚠️ udev rules directory not found"
fi

# 6. ตรวจสอบ power supply
echo "6. Checking power supply..."
echo "📊 System status:"
vcgencmd measure_volts 2>/dev/null || echo "⚠️ Cannot measure voltage"
vcgencmd measure_temp 2>/dev/null || echo "⚠️ Cannot measure temperature"
vcgencmd get_throttled 2>/dev/null || echo "⚠️ Cannot check throttling"

echo ""
echo "✅ Fixes applied!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot the system: sudo reboot"
echo "2. After reboot, test camera: python3 test_simple_camera.py"
echo "3. If still not working, check:"
echo "   - Power supply (use official 5V 3A adapter)"
echo "   - USB cable (try different cable)"
echo "   - USB port (try different port)"
echo "   - Camera compatibility"
echo ""
echo "🔍 To check if fixes worked:"
echo "   python3 test_power_supply.py"
echo "   python3 diagnose_camera_power.py"
