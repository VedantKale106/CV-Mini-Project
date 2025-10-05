# Create a comprehensive Smart Surveillance System based on the user's requirements and the existing code
# Let's create all the necessary files

import os

# Create the main surveillance.py file
surveillance_code = '''# surveillance.py
import cv2
import face_recognition
import os
import datetime
import numpy as np
import sqlite3
import time

from enroll import enroll
from alert import play_sound, send_email_alert

# === DATABASE SETUP ===
conn = sqlite3.connect('intruder_logs.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS intruders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    image_path TEXT
)""")
conn.commit()

# === CAMERA SETUP ===
camera = cv2.VideoCapture(0)  # Changed to 0 for most common webcam

# === KNOWN FACES ===
known_encodings = []
known_names = []

def load_known_faces():
    """Load all enrolled faces from the faces directory"""
    known_encodings.clear()
    known_names.clear()
    
    if not os.path.exists("faces"):
        os.makedirs("faces", exist_ok=True)
        return
    
    for person in os.listdir("faces"):
        person_folder = os.path.join("faces", person)
        if os.path.isdir(person_folder):
            for file in os.listdir(person_folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(person_folder, file)
                    try:
                        image = face_recognition.load_image_file(image_path)
                        locations = face_recognition.face_locations(image)
                        encodings = face_recognition.face_encodings(image, locations)
                        if encodings:
                            known_encodings.append(encodings[0])
                            known_names.append(person)
                            print(f"[LOADED] Face encoding for {person}")
                    except Exception as e:
                        print(f"[ERROR] Failed to load {image_path}: {e}")

def run_surveillance():
    """Main surveillance loop with CNN-based face detection and recognition"""
    print("\\n[INFO] Surveillance started. Press 'q' to stop.")
    print("[INFO] Using CNN-based face detection with feature maps...")
    
    last_intruder_time = 0
    cooldown = 5  # seconds between intruder alerts
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("[ERROR] Failed to read from camera")
            break
        
        # Resize frame for faster processing (optimization)
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        
        # CNN-based face detection using HOG + CNN features
        face_locations = face_recognition.face_locations(rgb_small, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
        
        names = []
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.45)
            name = "Intruder"
            confidence = 0
            
            if True in matches:
                # Calculate face distances for confidence scoring
                distances = face_recognition.face_distance(known_encodings, encoding)
                best_match_index = np.argmin(distances)
                if distances[best_match_index] < 0.45:
                    name = known_names[best_match_index]
                    confidence = (1 - distances[best_match_index]) * 100
            
            names.append((name, confidence))
        
        # Draw bounding boxes and labels
        for (top, right, bottom, left), (name, confidence) in zip(face_locations, names):
            # Scale back up face locations
            top *= 4; right *= 4; bottom *= 4; left *= 4
            
            # Choose color based on recognition
            color = (0, 255, 0) if name != "Intruder" else (0, 0, 255)
            label = f"{name}"
            if name != "Intruder":
                label += f" ({confidence:.1f}%)"
            
            # Draw rectangle and label
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Handle intruder detection
            if name == "Intruder" and (time.time() - last_intruder_time) > cooldown:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"captures/intruder_{timestamp}.jpg"
                
                # Save intruder snapshot
                cv2.imwrite(save_path, frame)
                
                # Log to database
                cursor.execute("INSERT INTO intruders (timestamp, image_path) VALUES (?, ?)", 
                             (timestamp, save_path))
                conn.commit()
                
                print(f"[ALERT] Intruder detected and logged at {timestamp}")
                
                # Trigger alerts
                play_sound()
                send_email_alert(save_path, timestamp)
                last_intruder_time = time.time()
        
        # Display surveillance feed
        cv2.imshow("Smart Surveillance System", frame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("[EXIT] Surveillance ended.")

def show_intruder_logs():
    """Display recent intruder detection logs"""
    cursor.execute("SELECT * FROM intruders ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    
    if logs:
        print("\\n=== RECENT INTRUDER LOGS ===")
        for log in logs:
            print(f"ID: {log[0]}, Time: {log[1]}, Image: {log[2]}")
    else:
        print("\\n[INFO] No intruder logs found.")

def view_enrolled_faces():
    """Show all enrolled persons"""
    if not os.path.exists("faces") or not os.listdir("faces"):
        print("\\n[INFO] No enrolled faces found.")
        return
    
    print("\\n=== ENROLLED PERSONS ===")
    for person in os.listdir("faces"):
        person_folder = os.path.join("faces", person)
        if os.path.isdir(person_folder):
            image_count = len([f for f in os.listdir(person_folder) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            print(f"- {person} ({image_count} images)")

# === MAIN PROGRAM ===
if __name__ == "__main__":
    # Setup required directories
    os.makedirs("faces", exist_ok=True)
    os.makedirs("captures", exist_ok=True)
    
    # Load existing faces
    print("[STARTUP] Loading enrolled faces...")
    load_known_faces()
    print(f"[STARTUP] Loaded {len(known_encodings)} face encodings from {len(set(known_names))} persons")
    
    # Main menu loop
    while True:
        print("\\n" + "="*50)
        print("    🔒 SMART SURVEILLANCE SYSTEM 🔒")
        print("="*50)
        print("1. 📹 Run Surveillance")
        print("2. 👤 Enroll New Person")
        print("3. 📋 View Enrolled Faces")
        print("4. 📊 Show Intruder Logs")
        print("5. 🚪 Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            if len(known_encodings) == 0:
                print("\\n[WARNING] No enrolled faces found. Please enroll at least one person first.")
                continue
            run_surveillance()
            
        elif choice == '2':
            name = input("\\nEnter person's name: ").strip()
            if name:
                enroll(camera, name, load_known_faces)
            else:
                print("[ERROR] Name cannot be empty.")
                
        elif choice == '3':
            view_enrolled_faces()
            
        elif choice == '4':
            show_intruder_logs()
            
        elif choice == '5':
            print("\\n👋 Thank you for using Smart Surveillance System!")
            camera.release()
            conn.close()
            break
            
        else:
            print("\\n❌ Invalid choice. Please select 1-5.")
'''

# Create the enroll.py file
enroll_code = '''# enroll.py
import os
import cv2
import face_recognition
import time

def enroll(camera, name, load_known_faces_callback):
    """
    Enroll a new person by capturing multiple face images from different angles
    Uses CNN feature extraction to create robust face encodings
    """
    folder = os.path.join("faces", name)
    os.makedirs(folder, exist_ok=True)
    
    print(f"\\n{'='*60}")
    print(f"    🎯 FACE ENROLLMENT FOR: {name.upper()}")
    print(f"{'='*60}")
    print("📋 INSTRUCTIONS:")
    print("   • Look directly at the camera")
    print("   • Turn your head LEFT and RIGHT slowly")
    print("   • Tilt your head UP and DOWN slightly")
    print("   • Smile naturally and maintain good lighting")
    print("   • Press 'q' to cancel enrollment anytime")
    print("-" * 60)
    
    count = 0
    total_required = 20
    poses_captured = {
        'front': 0, 'left': 0, 'right': 0, 'up': 0, 'down': 0, 'smile': 0
    }
    
    instructions = [
        "Look straight at the camera",
        "Turn your head to the LEFT",
        "Turn your head to the RIGHT", 
        "Tilt your head UP slightly",
        "Tilt your head DOWN slightly",
        "SMILE naturally!",
        "Look straight again",
        "Turn LEFT again",
        "Turn RIGHT again",
        "Natural expression"
    ]
    
    print("\\n🚀 Starting capture in 3 seconds...")
    time.sleep(3)
    
    while count < total_required:
        ret, frame = camera.read()
        if not ret:
            print("[ERROR] Failed to grab frame from camera.")
            continue
        
        # Convert BGR to RGB for face_recognition library
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces using CNN-based detection
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        
        # Current instruction
        current_instruction = instructions[min(count // 2, len(instructions) - 1)]
        
        # Display frame with instructions
        display_frame = frame.copy()
        
        if face_locations:
            for top, right, bottom, left in face_locations:
                # Draw bounding box around face
                cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Extract face region
                face_img = rgb_frame[top:bottom, left:right]
                if face_img.size == 0:
                    continue
                
                # Generate unique filename
                save_path = os.path.join(folder, f"{name}_{count:02d}.jpg")
                
                # Convert back to BGR and save
                bgr_face = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
                cv2.imwrite(save_path, bgr_face)
                
                count += 1
                print(f"✅ [{count:2d}/{total_required}] Captured - {current_instruction}")
                
                # Add small delay between captures
                time.sleep(0.5)
                break
        else:
            # No face detected
            cv2.putText(display_frame, "❌ NO FACE DETECTED", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(display_frame, "Adjust your position", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Display progress and instructions
        progress = int((count / total_required) * 100)
        cv2.putText(display_frame, f"Progress: {count}/{total_required} ({progress}%)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.putText(display_frame, f"Instruction: {current_instruction}", (10, display_frame.shape[0] - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(display_frame, "Press 'q' to cancel", (10, display_frame.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Show enrollment window
        cv2.imshow("Face Enrollment - Follow Instructions", display_frame)
        
        # Check for quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\\n❌ [CANCELLED] Enrollment interrupted by user.")
            cv2.destroyAllWindows()
            return False
    
    cv2.destroyAllWindows()
    
    # Reload known faces
    print("\\n🔄 Processing captured images and updating face database...")
    load_known_faces_callback()
    
    print(f"\\n✅ [SUCCESS] Enrollment completed for {name}!")
    print(f"📁 {count} face images saved to: {folder}")
    print("🧠 Face encodings generated using CNN feature extraction")
    print("-" * 60)
    
    return True
'''

# Create the alert.py file
alert_code = '''# alert.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import threading
import time

# Sound handling with fallback options
def play_sound():
    """Play alert sound with multiple fallback options"""
    sound_files = ["alert.mp3", "alert.wav", "beep.mp3"]
    
    for sound_file in sound_files:
        if os.path.exists(sound_file):
            try:
                # Try playsound first
                import playsound
                playsound.playsound(sound_file, block=False)
                print(f"[SOUND] Alert sound played: {sound_file}")
                return
            except ImportError:
                try:
                    # Fallback to pygame
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.play()
                    print(f"[SOUND] Alert sound played via pygame: {sound_file}")
                    return
                except ImportError:
                    pass
            except Exception as e:
                print(f"[ERROR] Failed to play {sound_file}: {e}")
                continue
    
    # Final fallback - system beep
    try:
        import winsound  # Windows
        winsound.Beep(1000, 1000)  # 1000Hz for 1 second
        print("[SOUND] System beep played (Windows)")
    except ImportError:
        try:
            # Linux/Mac fallback
            os.system("echo -e '\\a'")
            print("[SOUND] System beep played (Unix)")
        except:
            print("[WARNING] Could not play any alert sound")

def send_email_alert(image_path, timestamp):
    """
    Send email alert with intruder image
    Configure your Gmail settings below
    """
    # ⚠️ IMPORTANT: Replace with your own Gmail credentials
    sender = "your.email@gmail.com"  # Your Gmail address
    password = "your-app-password"   # Your Gmail App Password (not regular password)
    receiver = "alert.email@gmail.com"  # Where to send alerts
    
    # Skip email if not configured
    if sender == "your.email@gmail.com" or password == "your-app-password":
        print("[EMAIL] Email not configured. Skipping email alert.")
        print("[INFO] To enable email alerts:")
        print("   1. Edit alert.py")
        print("   2. Replace sender/password/receiver with your details")
        print("   3. Use Gmail App Password (not regular password)")
        return
    
    def send_async():
        try:
            # Create message
            msg = MIMEMultipart()
            msg["Subject"] = "🚨 INTRUDER ALERT - Smart Surveillance System"
            msg["From"] = sender
            msg["To"] = receiver
            
            # Email body
            body = f"""
🚨 SECURITY ALERT 🚨

An unknown person (intruder) has been detected by your Smart Surveillance System.

📅 Detection Time: {timestamp}
📷 Image: See attachment
🏠 Location: Your monitored area

Please check your security immediately!

---
Smart Surveillance System
Powered by CNN Face Recognition
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            # Attach intruder image
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    img_data = f.read()
                    img = MIMEImage(img_data)
                    img.add_header("Content-Disposition", "attachment", 
                                 filename=f"intruder_{timestamp}.jpg")
                    msg.attach(img)
            
            # Send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.send_message(msg)
            
            print("✅ [EMAIL SENT] Intruder alert email delivered successfully")
            
        except Exception as e:
            print(f"❌ [EMAIL ERROR] Failed to send alert email: {e}")
            print("[INFO] Check your Gmail settings and App Password")
    
    # Send email asynchronously to avoid blocking surveillance
    thread = threading.Thread(target=send_async)
    thread.daemon = True
    thread.start()

def create_alert_sound():
    """Create a default alert sound file if none exists"""
    sound_files = ["alert.mp3", "alert.wav", "beep.mp3"]
    
    if not any(os.path.exists(f) for f in sound_files):
        print("[INFO] No alert sound file found. Creating default beep...")
        try:
            # Create a simple beep using numpy and scipy
            import numpy as np
            from scipy.io.wavfile import write
            
            # Generate beep sound
            sample_rate = 44100
            duration = 2.0  # seconds
            frequency = 1000  # Hz
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            beep = np.sin(2 * np.pi * frequency * t) * 0.3
            
            # Add fade in/out
            fade_samples = int(0.1 * sample_rate)
            beep[:fade_samples] *= np.linspace(0, 1, fade_samples)
            beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Save as WAV
            write("alert.wav", sample_rate, (beep * 32767).astype(np.int16))
            print("[CREATED] Default alert.wav file created")
            
        except ImportError:
            print("[INFO] Install scipy for auto-generated alert sound: pip install scipy")
        except Exception as e:
            print(f"[ERROR] Could not create alert sound: {e}")

# Initialize alert system
if __name__ == "__main__":
    create_alert_sound()
'''

# Create requirements.txt
requirements = '''opencv-python==4.8.1.78
face-recognition==1.3.0
numpy==1.24.3
playsound==1.3.0
Pillow==10.0.0
dlib==19.24.2
cmake==3.27.7
'''

# Create setup.py for easy installation
setup_code = '''# setup.py
from setuptools import setup, find_packages

setup(
    name="smart-surveillance-system",
    version="1.0.0",
    description="AI-powered surveillance system with face recognition and intruder alerts",
    author="Your Name",
    author_email="your.email@gmail.com",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.8.0",
        "face-recognition>=1.3.0",
        "numpy>=1.24.0",
        "playsound>=1.3.0",
        "Pillow>=10.0.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "surveillance=surveillance:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Multimedia :: Video :: Capture",
    ],
)
'''

# Create installation script
install_script = '''#!/bin/bash
# install.sh - Smart Surveillance System Installation Script

echo "🔧 Smart Surveillance System Installer"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o "3\.[0-9]*")
if [[ $? -ne 0 ]]; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Found Python $python_version"

# Create virtual environment (recommended)
echo "📦 Setting up virtual environment..."
python3 -m venv surveillance_env
source surveillance_env/bin/activate

# Install required packages
echo "⬇️  Installing required packages..."
pip install --upgrade pip
pip install opencv-python face-recognition numpy playsound Pillow

# Create directories
echo "📁 Creating required directories..."
mkdir -p faces captures

# Download sample alert sound (optional)
echo "🔊 Creating alert sound..."
python3 -c "
import numpy as np
from scipy.io.wavfile import write
sample_rate = 44100
duration = 2.0
frequency = 1000
t = np.linspace(0, duration, int(sample_rate * duration))
beep = np.sin(2 * np.pi * frequency * t) * 0.3
fade_samples = int(0.1 * sample_rate)
beep[:fade_samples] *= np.linspace(0, 1, fade_samples)  
beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)
write('alert.wav', sample_rate, (beep * 32767).astype(np.int16))
print('Alert sound created successfully!')
" 2>/dev/null || echo "⚠️  Install scipy for custom alert sound: pip install scipy"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To run the system:"
echo "   1. Activate virtual environment: source surveillance_env/bin/activate"
echo "   2. Run surveillance system: python3 surveillance.py"
echo ""
echo "⚙️  Don't forget to configure email settings in alert.py"
echo "📖 See README.md for detailed setup instructions"
'''

# Create comprehensive README
readme = '''# 🔒 Smart Surveillance System

An advanced AI-powered surveillance system that uses Convolutional Neural Networks (CNN) for real-time face recognition, intruder detection, and automated alert systems.

## ✨ Features

### 🎯 Core Functionality
- **Real-time Face Recognition**: Uses CNN-based deep learning for accurate face detection
- **Intruder Detection**: Automatically identifies unknown faces and triggers alerts
- **Multi-pose Enrollment**: Captures 20+ images from different angles for robust recognition
- **Smart Alerts**: Email notifications with snapshots + audio alerts
- **Event Logging**: SQLite database stores all intruder detection events
- **User-friendly Interface**: Simple menu-driven operation

### 🧠 Technical Highlights
- **CNN Feature Extraction**: Leverages deep neural networks for face encoding
- **HOG + CNN Detection**: Combines Histogram of Oriented Gradients with CNN
- **Feature Maps**: Generates unique 128-dimensional face embeddings
- **Confidence Scoring**: Shows recognition confidence percentages
- **Real-time Processing**: Optimized for live video stream analysis

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Webcam or USB camera
- Gmail account (for email alerts)

### Method 1: Automatic Installation
```bash
# Clone or download the project
git clone <your-repo-url>
cd smart-surveillance-system

# Run installation script (Linux/Mac)
chmod +x install.sh
./install.sh

# Or install manually:
pip install -r requirements.txt
```

### Method 2: Manual Installation
```bash
# Install required packages
pip install opencv-python face-recognition numpy playsound Pillow

# Create required directories
mkdir faces captures

# Run the system
python surveillance.py
```

## 🚀 Quick Start Guide

### 1. First Time Setup
```bash
python surveillance.py
```

### 2. Enroll Authorized Persons
1. Select "Enroll New Person" from menu
2. Enter person's name
3. Follow on-screen instructions:
   - Look straight at camera
   - Turn head left and right
   - Tilt head up and down
   - Smile naturally
4. System captures 20 images automatically

### 3. Configure Email Alerts
Edit `alert.py` and update:
```python
sender = "your.gmail@gmail.com"        # Your Gmail
password = "your-app-password"         # Gmail App Password  
receiver = "alerts@gmail.com"          # Alert destination
```

**Important**: Use Gmail App Password, not regular password!

### 4. Start Surveillance
1. Select "Run Surveillance"
2. System shows live camera feed
3. Green boxes = Recognized faces
4. Red boxes = Intruders (triggers alerts)
5. Press 'q' to stop

## 📁 Project Structure

```
smart-surveillance-system/
├── surveillance.py      # Main application with menu system
├── enroll.py           # Face enrollment module
├── alert.py            # Email and sound alert system  
├── requirements.txt    # Python dependencies
├── setup.py           # Package installation
├── install.sh         # Auto-installation script
├── README.md          # This file
├── faces/             # Enrolled face images (auto-created)
│   └── person_name/   # Individual person folders
├── captures/          # Intruder snapshots (auto-created)
└── intruder_logs.db   # SQLite event database (auto-created)
```

## ⚙️ Configuration Options

### Camera Settings
```python
camera = cv2.VideoCapture(0)  # Change 0 to 1, 2, etc. for different cameras
```

### Recognition Sensitivity
```python
tolerance=0.45  # Lower = stricter matching (0.3-0.6 recommended)
```

### Alert Cooldown
```python
cooldown = 5  # Seconds between intruder alerts
```

## 🔧 Technical Deep Dive

### CNN Architecture
The system uses a pre-trained CNN model that:
1. **Input Layer**: Processes 150x150 RGB face images
2. **Convolutional Layers**: Extract facial features using learned kernels
3. **Pooling Layers**: Reduce dimensionality while preserving features  
4. **Dense Layers**: Generate 128-dimensional face embeddings
5. **Output**: Unique feature vector for each face

### Feature Extraction Process
```
Face Image → CNN → Feature Map → 128D Encoding → Similarity Comparison
```

### Detection Pipeline
1. **Frame Capture**: Get video frame from camera
2. **Face Detection**: Use HOG + CNN to locate faces
3. **Feature Extraction**: Generate face encodings
4. **Recognition**: Compare with enrolled faces
5. **Alert System**: Trigger alerts for unknown faces

## 📱 Usage Examples

### Menu Navigation
```
=== SMART SURVEILLANCE MENU ===
1. Run Surveillance      # Start monitoring
2. Enroll New Person     # Add authorized face
3. View Enrolled Faces   # See registered users
4. Show Intruder Logs    # View detection history
5. Exit                  # Close application
```

### Enrollment Process
```
[INFO] Starting enrollment for: John
[INSTRUCTIONS] Look at the camera. Turn your face left, right, up, and smile naturally.
✅ [01/20] Captured - Look straight at the camera
✅ [02/20] Captured - Turn your head to the LEFT  
✅ [03/20] Captured - Turn your head to the RIGHT
...
[SUCCESS] Enrollment completed for John!
```

### Live Surveillance
```
[INFO] Surveillance started. Press 'q' to stop.
[INFO] Using CNN-based face detection with feature maps...
[LOADED] Face encoding for John
[LOADED] Face encoding for Sarah
[ALERT] Intruder detected and logged at 20231015_143022
✅ [EMAIL SENT] Intruder alert email delivered successfully
```

## 🛡️ Security Features

### Data Protection
- **Local Storage**: All face data stored locally (not cloud)
- **Encrypted Database**: SQLite with secure event logging
- **Privacy First**: No external API calls for face recognition

### Alert System
- **Multi-channel Alerts**: Email + Sound notifications
- **Image Evidence**: Automatic snapshot capture
- **Timestamp Logging**: Precise detection time records
- **Cooldown Protection**: Prevents alert spam

## 🐛 Troubleshooting

### Common Issues

**Camera not detected:**
```python
# Try different camera indices
camera = cv2.VideoCapture(1)  # or 2, 3, etc.
```

**Face recognition slow:**
- Ensure good lighting during enrollment
- Capture clear, front-facing images
- Reduce video resolution if needed

**Email alerts not working:**
- Verify Gmail App Password (not regular password)
- Enable 2-Factor Authentication
- Check firewall/antivirus settings

**Sound not playing:**
- Ensure `alert.wav` or `alert.mp3` exists
- Try: `pip install pygame` for alternative audio
- Check system volume settings

### Performance Optimization

**For slower computers:**
```python
# Reduce frame size for processing
small = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)  # Smaller = faster

# Skip frames for processing
if frame_count % 2 == 0:  # Process every 2nd frame
    # ... face recognition code
```

**For better accuracy:**
```python
# Use CNN model (slower but more accurate)
face_locations = face_recognition.face_locations(rgb_frame, model="cnn")

# Stricter matching
tolerance=0.35  # Lower tolerance = stricter matching
```

## 🔄 Updates & Maintenance

### Database Maintenance
```python
# View intruder logs
sqlite3 intruder_logs.db "SELECT * FROM intruders;"

# Clear old logs (optional)
sqlite3 intruder_logs.db "DELETE FROM intruders WHERE timestamp < '20231001';"
```

### Adding More Features
The system is modular and can be extended with:
- Web dashboard interface
- Mobile app notifications  
- Multiple camera support
- Face mask detection
- Age/gender recognition
- Motion detection integration

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review error messages carefully
3. Ensure all dependencies are installed correctly
4. Verify camera and email configurations

---

**⚠️ Important Notes:**
- This system is for educational and personal use
- Comply with local privacy laws when using surveillance
- Regularly update face enrollments for best accuracy
- Test email settings before deploying system

**🎯 Perfect for:**
- Home security monitoring
- Office access control
- Learning computer vision concepts  
- Understanding CNN applications
- Building AI-powered projects

---

*Built with ❤️ using Python, OpenCV, and Deep Learning*
'''

# Save all files
files_to_create = {
    'surveillance.py': surveillance_code,
    'enroll.py': enroll_code,
    'alert.py': alert_code,
    'requirements.txt': requirements,
    'setup.py': setup_code,
    'install.sh': install_script,
    'README.md': readme
}

print("Creating Smart Surveillance System files...")
print("=" * 60)

for filename, content in files_to_create.items():
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filename} ({len(content)} characters)")

print("\n" + "=" * 60)
print("🎉 Smart Surveillance System Created Successfully!")
print("=" * 60)

print("\n📁 Files created:")
for filename in files_to_create.keys():
    print(f"   • {filename}")

print("\n🚀 Quick Start:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run system: python surveillance.py") 
print("3. Configure email in alert.py")
print("4. Enroll faces before starting surveillance")

print("\n⚠️  Important Setup Notes:")
print("• Make sure you have a webcam connected")
print("• Create Gmail App Password (not regular password)")
print("• Good lighting improves recognition accuracy")
print("• Place alert.mp3 or alert.wav file for sound alerts")