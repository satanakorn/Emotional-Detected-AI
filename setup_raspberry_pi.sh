#!/bin/bash

echo "🍓 Setting up Raspberry Pi 4 Camera for Emotion Detection"
echo "=================================================="

# อัพเดทระบบ
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# ติดตั้ง dependencies พื้นฐาน
echo "🔧 Installing basic dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt install -y libjasper-dev libjpeg-dev libpng-dev libtiff-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev

# ติดตั้ง libcamera และ picamera2
echo "📷 Installing camera libraries..."
sudo apt install -y python3-picamera2
sudo apt install -y libcamera-tools

# เปิดใช้งานกล้อง
echo "⚙️ Enabling camera..."
sudo raspi-config nonint do_camera 0

# เพิ่มการตั้งค่าใน config.txt
echo "📝 Configuring camera settings..."
sudo bash -c 'echo "camera_auto_detect=1" >> /boot/config.txt'
sudo bash -c 'echo "gpu_mem=128" >> /boot/config.txt'
sudo bash -c 'echo "start_x=1" >> /boot/config.txt'

# สร้าง virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv emotion_detection_env
source emotion_detection_env/bin/activate

# ติดตั้ง Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install openpyxl==3.1.2

# ติดตั้ง TensorFlow สำหรับ ARM64
echo "🧠 Installing TensorFlow for ARM64..."
pip install tensorflow==2.13.0

# ติดตั้ง DeepFace
echo "😊 Installing DeepFace..."
pip install deepface==0.0.79

# ตรวจสอบการติดตั้ง
echo "✅ Verifying installation..."
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"
python3 -c "import tensorflow; print('TensorFlow version:', tensorflow.__version__)"

# ตรวจสอบกล้อง
echo "📷 Testing camera..."
libcamera-hello --list-cameras

echo "🎉 Setup completed!"
echo "📋 Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. Activate virtual environment: source emotion_detection_env/bin/activate"
echo "3. Run the emotion detection: python3 emotion_detector.py"
