# 🎭 Emotion Detection for Raspberry Pi 4

ระบบตรวจจับอารมณ์ด้วยกล้อง Raspberry Pi 4 พร้อมการบันทึกข้อมูลลง Excel

## 🚨 ปัญหาที่แก้ไขแล้ว

### 1. ปัญหา `__main__` เขียนผิด
**ปัญหา:** ในไฟล์ `app.py` บรรทัด 342 เขียน `if __name__ == "_main_":` ผิด
**แก้ไข:** เปลี่ยนเป็น `if __name__ == "__main__":`

### 2. ฟังก์ชัน `show_camera_info` ขาด `def`
**ปัญหา:** ในไฟล์ `emotion_detector.py` บรรทัด 771 ขาด `def show_camera_info(self):`
**แก้ไข:** เพิ่ม `def show_camera_info(self):` หน้า docstring

### 3. ปัญหา PiCamera2 ไม่ทำงานกับกล้อง USB
**ปัญหา:** PiCamera2 ใช้สำหรับกล้อง Raspberry Pi Camera Module (CSI) ไม่ใช่กล้อง USB
**แก้ไข:** 
- เพิ่มฟังก์ชัน `detect_usb_camera()` เพื่อตรวจสอบกล้อง USB
- แก้ไขลำดับการเลือกกล้องให้ลอง USB ก่อน PiCamera2
- สร้างสคริปต์วินิจฉัย `diagnose_camera.py` และ `test_usb_camera.py`

### 4. ปัญหาการแสดงผลภาษาไทยเป็น "?????"
**ปัญหา:** OpenCV ไม่รองรับการแสดงผลภาษาไทย ทำให้แสดงเป็น "?????"
**แก้ไข:** 
- เปลี่ยนการแสดงผลอารมณ์เป็นภาษาอังกฤษ (Happy, Neutral, Sad, Angry)
- เก็บข้อมูลภาษาไทยใน Excel แต่แสดงผลเป็นภาษาอังกฤษบนหน้าจอ
- สร้างสคริปต์ทดสอบ `test_thai_display.py`

### 5. ปัญหาการบันทึก Excel ไม่เป็นไปตามเวลาที่ต้องการ
**ปัญหา:** ระบบบันทึก Excel ทุก 10 ครั้ง แทนที่จะเป็นทุก 5 วินาที
**แก้ไข:** 
- เปลี่ยนจาก counter-based เป็น time-based saving
- บันทึก Excel ทุก 5 วินาทีตามที่ต้องการ
- แสดงข้อความยืนยันเมื่อบันทึกสำเร็จ

### 6. ปัญหา Score แสดงเป็น "????"
**ปัญหา:** ดาว (★) ไม่สามารถแสดงผลใน OpenCV ได้
**แก้ไข:** 
- เปลี่ยนจาก ★ เป็น * (asterisk)
- ปรับขนาดข้อความให้เหมาะสมกับหน้าจอเต็ม
- เพิ่มการปรับขนาดข้อความอัตโนมัติ

### 7. ปัญหาหน้าต่างไม่เต็มจอ
**ปัญหา:** หน้าต่างแสดงผลไม่เต็มจอ
**แก้ไข:** 
- เพิ่มโหมดเต็มจออัตโนมัติ
- เพิ่มปุ่ม 'f' สำหรับสลับโหมดเต็มจอ
- ปรับขนาดข้อความให้เหมาะสมกับหน้าจอใหญ่

### 8. ปัญหา GStreamer และ V4L2 ไม่ทำงาน
**ปัญหา:** ระบบพยายามใช้ GStreamer และ V4L2 ก่อน แต่ไม่สามารถเปิดกล้องได้
**แก้ไข:** 
- เปลี่ยนลำดับการทดสอบกล้องให้ลอง OpenCV แบบธรรมดาก่อน
- เพิ่มการจัดการ error ที่ดีขึ้น
- สร้างสคริปต์ทดสอบกล้องแบบง่าย `test_simple_camera.py`

### 9. ปัญหากล้องเปิดไม่ติด (ไฟไม่พอ)
**ปัญหา:** กล้องไม่สามารถเปิดได้ อาจเกิดจากพลังงานไม่เพียงพอ
**แก้ไข:** 
- สร้างสคริปต์วินิจฉัยพลังงาน `diagnose_camera_power.py`
- สร้างสคริปต์ทดสอบพลังงาน `test_power_supply.py`
- สร้างสคริปต์แก้ไขปัญหาอัตโนมัติ `fix_camera_issues.sh`

### 10. ปัญหาการตรวจจับใบหน้าไม่ดี
**ปัญหา:** ระบบตรวจจับใบหน้าไม่ได้หรือไม่แม่นยำ
**แก้ไข:** 
- ปรับปรุงพารามิเตอร์การตรวจจับใบหน้า (scaleFactor, minNeighbors)
- เพิ่มฟังก์ชันปรับปรุงเฟรม (frame enhancement)
- เพิ่มกรอบแสดงใบหน้าที่ตรวจจับได้
- สร้างสคริปต์ทดสอบการตรวจจับใบหน้า `test_face_detection.py`
- เพิ่มโหมดทดสอบการตรวจจับใบหน้าในโปรแกรมหลัก

### 11. ปรับปรุงเป็น Real-time Detection + Data Save Every 5s
**ปัญหา:** ต้องการการตรวจจับแบบ real-time แต่บันทึกข้อมูลทุก 5 วินาที
**แก้ไข:** 
- ปรับ FRAME_SKIP = 1 (ไม่ข้ามเฟรม)
- ตรวจจับทุก 50ms (20 FPS) สำหรับ real-time
- บันทึกข้อมูลทุก 5 วินาทีแทนการบันทึกทุกเฟรม
- เพิ่มการแสดงสถานะการบันทึกข้อมูล
- สร้างสคริปต์ทดสอบ real-time `test_realtime_detection.py`

### 12. แก้ไขปัญหาการบันทึกข้อมูลลง Excel
**ปัญหา:** ข้อมูลไม่ถูกสร้างและบันทึกลง Excel
**แก้ไข:** 
- แก้ไขฟังก์ชัน `save_to_excel` ให้เรียกใช้ `_save_to_excel_internal` โดยตรง
- เพิ่มการตรวจสอบการสร้างไฟล์ Excel ใน `_save_to_excel_internal`
- เพิ่มการแสดงข้อความ debug และ error handling
- สร้างสคริปต์ทดสอบ Excel `test_excel_saving.py`
- เพิ่มการแสดง path ของไฟล์ Excel

## 📋 ไฟล์ที่สร้างใหม่

1. **`requirements.txt`** - รายการ dependencies ที่จำเป็น
2. **`setup_raspberry_pi.sh`** - สคริปต์ติดตั้งและตั้งค่าระบบ
3. **`test_camera.py`** - สคริปต์ทดสอบกล้อง
4. **`diagnose_camera.py`** - สคริปต์วินิจฉัยปัญหากล้อง
5. **`test_usb_camera.py`** - สคริปต์ทดสอบกล้อง USB
6. **`test_manual_emotion.py`** - สคริปต์ทดสอบ manual emotion
7. **`test_thai_display.py`** - สคริปต์ทดสอบการแสดงผลภาษาไทย
8. **`test_fullscreen.py`** - สคริปต์ทดสอบโหมดเต็มจอ
9. **`test_simple_camera.py`** - สคริปต์ทดสอบกล้องแบบง่าย
10. **`diagnose_camera_power.py`** - สคริปต์วินิจฉัยพลังงานกล้อง
11. **`test_power_supply.py`** - สคริปต์ทดสอบแหล่งจ่ายไฟ
12. **`fix_camera_issues.sh`** - สคริปต์แก้ไขปัญหากล้องอัตโนมัติ
13. **`test_face_detection.py`** - สคริปต์ทดสอบการตรวจจับใบหน้า
14. **`test_realtime_detection.py`** - สคริปต์ทดสอบ real-time detection
15. **`test_excel_saving.py`** - สคริปต์ทดสอบการบันทึก Excel
16. **`README.md`** - คู่มือการใช้งาน

## 🚀 วิธีการติดตั้งและใช้งาน

### ขั้นตอนที่ 1: ติดตั้งระบบ
```bash
# ให้สิทธิ์สคริปต์
chmod +x setup_raspberry_pi.sh

# รันสคริปต์ติดตั้ง
./setup_raspberry_pi.sh
```

### ขั้นตอนที่ 2: รีบูตระบบ
```bash
sudo reboot
```

### ขั้นตอนที่ 3: ทดสอบกล้อง
```bash
# เปิดใช้งาน virtual environment
source emotion_detection_env/bin/activate

# ทดสอบกล้องทั่วไป
python3 test_camera.py

# ทดสอบกล้อง USB เฉพาะ
python3 test_usb_camera.py

# วินิจฉัยปัญหากล้อง
python3 diagnose_camera.py
```

### ขั้นตอนที่ 4: ทดสอบระบบ Manual Emotion
```bash
# ทดสอบระบบ manual emotion
python3 test_manual_emotion.py

# ทดสอบการแสดงผลภาษาไทย
python3 test_thai_display.py

# ทดสอบโหมดเต็มจอ
python3 test_fullscreen.py

# ทดสอบกล้องแบบง่าย
python3 test_simple_camera.py

# ทดสอบแหล่งจ่ายไฟ
python3 test_power_supply.py

# วินิจฉัยปัญหาพลังงานกล้อง
python3 diagnose_camera_power.py

# ทดสอบการตรวจจับใบหน้า
python3 test_face_detection.py

# ทดสอบ real-time detection
python3 test_realtime_detection.py

# ทดสอบการบันทึก Excel
python3 test_excel_saving.py
```

### ขั้นตอนที่ 5: รันระบบตรวจจับอารมณ์
```bash
# รันเวอร์ชันใหม่ (แนะนำ)
python3 emotion_detector.py

# หรือรันเวอร์ชันเก่า
python3 app.py
```

### 🎯 วิธีการใช้งาน Manual Emotion Input

1. **รันระบบ:** `python3 emotion_detector.py`
2. **เลือกกล้อง:** เลือก "2. กล้อง Raspberry Pi"
3. **กดปุ่ม Manual:**
   - กด **1** = Happy 90% → *****
   - กด **2** = Neutral 60% → ***
   - กด **3** = Sad 35% → **
   - กด **4** = Angry 10% → *
4. **Manual input จะแสดง 5 วินาที** แล้วกลับไปใช้ AI detection

## 🔧 การแก้ไขปัญหากล้องเปิดไม่ติด

### ⚡ ปัญหาพลังงานไม่เพียงพอ

หากกล้องเปิดไม่ติด อาจเกิดจากพลังงานไม่เพียงพอ:

```bash
# ทดสอบแหล่งจ่ายไฟ
python3 test_power_supply.py

# วินิจฉัยปัญหาพลังงาน
python3 diagnose_camera_power.py

# แก้ไขปัญหาอัตโนมัติ
sudo ./fix_camera_issues.sh
```

### 🔍 สาเหตุที่พบบ่อย:

1. **แหล่งจ่ายไฟไม่เพียงพอ**
   - ใช้ adapter ที่ไม่ใช่ของทางการ
   - ไฟไม่ถึง 5V 3A
   - สาย USB ยาวเกินไป

2. **สิทธิ์การเข้าถึงกล้อง**
   - User ไม่ได้อยู่ใน video group
   - Permissions ของ /dev/video* ไม่ถูกต้อง

3. **การตั้งค่าระบบ**
   - Camera ไม่ได้เปิดใช้งานใน raspi-config
   - config.txt ไม่มีการตั้งค่ากล้อง

4. **ฮาร์ดแวร์**
   - สาย USB เสีย
   - Port USB เสีย
   - กล้องไม่เข้ากัน

## 🔧 การแก้ไขปัญหาการตรวจจับใบหน้า

### 👤 ปัญหาการตรวจจับใบหน้าไม่ดี

หากระบบตรวจจับใบหน้าไม่ได้หรือไม่แม่นยำ:

```bash
# ทดสอบการตรวจจับใบหน้า
python3 test_face_detection.py

# รันโปรแกรมหลักในโหมดทดสอบ
python3 emotion_detector.py
# เลือก "2. ทดสอบการตรวจจับใบหน้า"
```

### 🔍 สาเหตุที่พบบ่อย:

1. **แสงไม่เพียงพอ**
   - ใช้แสงธรรมชาติหรือไฟสว่าง
   - หลีกเลี่ยงแสงจ้าจากด้านหลัง
   - ปรับตำแหน่งกล้องให้เหมาะสม

2. **ตำแหน่งใบหน้า**
   - ใบหน้าต้องอยู่ตรงกลางกล้อง
   - ระยะห่างประมาณ 50-100 ซม.
   - หลีกเลี่ยงการเอียงหัวมาก

3. **สิ่งกีดขวาง**
   - เอาหน้าตา แว่นตา หรือหมวกออก
   - หลีกเลี่ยงผมบังหน้า
   - ตรวจสอบเลนส์กล้องสะอาด

4. **การตั้งค่ากล้อง**
   - ปรับโฟกัสให้ชัด
   - ตรวจสอบความละเอียดกล้อง
   - ลองใช้กล้องอื่น

## 🔧 การแก้ไขปัญหาเพิ่มเติม

### ⚠️ สิ่งสำคัญ: PiCamera2 vs กล้อง USB

**PiCamera2** ใช้สำหรับ:
- กล้อง Raspberry Pi Camera Module (เสียบผ่าน CSI connector)
- ไม่ใช่กล้อง USB

**กล้อง USB** ใช้:
- OpenCV กับ camera index (0, 1, 2, ...)
- ไม่ใช่ PiCamera2

### ถ้ากล้องยังไม่ทำงาน:

1. **ตรวจสอบประเภทกล้อง**
   ```bash
   # ตรวจสอบกล้อง CSI (PiCamera2)
   libcamera-hello --list-cameras
   
   # ตรวจสอบกล้อง USB
   ls -la /dev/video*
   lsusb | grep -i camera
   ```

2. **ทดสอบกล้อง USB**
   ```bash
   python3 test_usb_camera.py
   python3 diagnose_camera.py
   ```

3. **เปิดใช้งานกล้อง**
   ```bash
   sudo raspi-config
   # เลือก Interface Options > Camera > Enable
   ```

4. **แก้ไข config.txt**
   ```bash
   sudo nano /boot/config.txt
   # เพิ่มบรรทัดเหล่านี้:
   camera_auto_detect=1
   start_x=1
   gpu_mem=128
   ```

5. **รีบูตระบบ**
   ```bash
   sudo reboot
   ```

### ถ้า DeepFace ไม่ทำงาน:
```bash
# ติดตั้ง TensorFlow สำหรับ ARM64
pip install tensorflow==2.13.0

# ติดตั้ง DeepFace
pip install deepface==0.0.79
```

## 📊 ฟีเจอร์ที่เพิ่มใหม่

- ✅ รองรับ PiCamera2 (แนะนำสำหรับ RPi 4)
- ✅ รองรับ GStreamer pipeline
- ✅ รองรับ V4L2 direct access
- ✅ รองรับกล้อง USB
- ✅ บันทึกข้อมูลลง Excel
- ✅ ปรับแต่งความสว่างและคอนทราสต์
- ✅ สลับโหมดสี/ขาวดำ
- ✅ แสดงสถิติอารมณ์
- ✅ **ระบบประเมินอารมณ์แบบ Manual ด้วย Keyboard**
- ✅ **การแปลผลอารมณ์ตามเกณฑ์ใหม่ (Happy 80-100%, Neutral 50-70%, Sad 30-40%, Angry 0-20%)**

## 🎮 คำสั่งควบคุม

### การควบคุมทั่วไป
- **q** - ออกจากโปรแกรม
- **s** หรือ **SPACE** - บันทึกรูปภาพ
- **i** - แสดงข้อมูลกล้อง
- **c** - สลับโหมดสี
- **f** - สลับโหมดเต็มจอ (ใหม่!)
- **b/v** - ปรับความสว่าง (+/-)
- **n/m** - ปรับคอนทราสต์ (+/-)

### 🎯 Manual Emotion Input (ใหม่!)
- **1** - Happy 80-100% → *****
- **2** - Neutral 50-70% → ***
- **3** - Sad 30-40% → **
- **4** - Angry 0-20% → *

> **หมายเหตุ:** Manual input จะใช้งานได้ 5 วินาที หลังจากกดปุ่ม

## 📁 โครงสร้างไฟล์

```
detected-face-ai/
├── app.py                    # เวอร์ชันเก่า (แก้ไขแล้ว)
├── emotion_detector.py       # เวอร์ชันใหม่ (แนะนำ)
├── emotion_data.xlsx         # ไฟล์ข้อมูลอารมณ์
├── requirements.txt          # Dependencies
├── setup_raspberry_pi.sh    # สคริปต์ติดตั้ง
├── test_camera.py           # สคริปต์ทดสอบกล้อง
├── diagnose_camera.py       # สคริปต์วินิจฉัยปัญหากล้อง
├── test_usb_camera.py       # สคริปต์ทดสอบกล้อง USB
├── test_manual_emotion.py   # สคริปต์ทดสอบ manual emotion
├── test_thai_display.py     # สคริปต์ทดสอบการแสดงผลภาษาไทย
├── test_fullscreen.py       # สคริปต์ทดสอบโหมดเต็มจอ
├── test_simple_camera.py    # สคริปต์ทดสอบกล้องแบบง่าย
├── diagnose_camera_power.py # สคริปต์วินิจฉัยพลังงานกล้อง
├── test_power_supply.py     # สคริปต์ทดสอบแหล่งจ่ายไฟ
├── fix_camera_issues.sh     # สคริปต์แก้ไขปัญหากล้องอัตโนมัติ
├── test_face_detection.py   # สคริปต์ทดสอบการตรวจจับใบหน้า
├── test_realtime_detection.py # สคริปต์ทดสอบ real-time detection
├── test_excel_saving.py     # สคริปต์ทดสอบการบันทึก Excel
└── README.md                # คู่มือการใช้งาน
```

## 🆘 การแก้ไขปัญหา

หากยังมีปัญหา ให้รันคำสั่งเหล่านี้เพื่อตรวจสอบ:

```bash
# ตรวจสอบสถานะกล้อง
vcgencmd get_camera

# ตรวจสอบ libcamera
libcamera-hello --list-cameras

# ตรวจสอบ OpenCV
python3 -c "import cv2; print(cv2.__version__)"

# ตรวจสอบ PiCamera2
python3 -c "from picamera2 import Picamera2; print('PiCamera2 OK')"
```

## 📞 การสนับสนุน

หากยังมีปัญหา กรุณาตรวจสอบ:
1. การเชื่อมต่อสายกล้อง
2. การตั้งค่าใน raspi-config
3. การติดตั้ง dependencies
4. การรีบูตระบบหลังการตั้งค่า
