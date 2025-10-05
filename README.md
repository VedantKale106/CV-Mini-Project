# 🔒 Smart Surveillance System

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
