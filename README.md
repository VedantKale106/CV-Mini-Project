# 🔒 Smart Surveillance System

An advanced AI-powered surveillance system using CNN-based face recognition for real-time intruder detection, alert notifications, and multi-pose face enrollment.

***

## ✨ Features

### 🎯 Core Functionality
- **Real-time Face Recognition:** Uses CNN-based deep learning for accurate detection and recognition.
- **Intruder Detection:** Automatically identifies unknown faces and triggers alerts.
- **Multi-pose Enrollment:** Captures 20+ images from different angles for robust face encoding.
- **Smart Alerts:** Plays alert sounds and sends email notifications with intruder snapshots.
- **Event Logging:** Logs all intruder events with timestamps in a local SQLite database.
- **User-friendly CLI:** Intuitive menu-driven interface for easy enrollment and monitoring.

### 🧠 Technical Highlights
- **CNN Feature Extraction:** Extracts 128-dimensional face embeddings using a convolutional network.
- **HOG + CNN Detection:** Combines Histogram of Oriented Gradients with CNN for robust detection.
- **Confidence Scoring:** Displays recognition confidence on live feed.
- **Optimized for Live Processing:** Processes webcam video stream with efficiency and cooldown to avoid alert spam.

***

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Webcam or USB camera
- Gmail account (for email alerts with app password)

### Quick Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd smart-surveillance-system

# Install dependencies via pip
pip install -r requirements.txt

# Create required directories (auto-created on first run)
mkdir faces captures

# Run the system
python surveillance.py
```

***

## 🚀 Usage Guide

### 1. Launch System

Run the main application:

```bash
python surveillance.py
```

You will see a menu:
```
1. Run Surveillance
2. Enroll New Person
3. View Enrolled Faces
4. Show Intruder Logs
5. Exit
```

### 2. Enroll Authorized Persons

- Choose option 2 "Enroll New Person".
- Enter the person's name.
- Follow the on-screen instructions to capture 20 images with multiple poses (head turns, smiles, etc).
- Enrollment creates robust facial feature maps for accurate future recognition.

### 3. Run Live Surveillance

- Choose option 1 "Run Surveillance".
- The system monitors the webcam feed in real-time.
- Recognized faces are shown with green bounding boxes and names.
- Unknown faces (intruders) are shown with red bounding boxes.
- Intruder images are saved, sound alerts are played, and emails are sent automatically.

### 4. Configure Email Alerts

Open `alert.py` and update with your Gmail credentials and alert recipient:

```python
sender = "your.email@gmail.com"        # Your Gmail address
password = "your-app-password"         # Gmail App Password (enable 2FA and generate App Password)
receiver = "alerts_recipient@gmail.com" # Email where alerts are sent
```

> **Note:** Use a Gmail App Password, not your regular account password.

### 5. View Intruder Logs

Select option 4 to view recent intruder detection logs stored locally.

***

## 📁 Project Structure

```
smart-surveillance-system/
├── surveillance.py        # Main surveillance script with menu
├── enroll.py             # Face enrollment with pose guidance
├── alert.py              # Email and sound alert system
├── requirements.txt      # Required Python packages
├── faces/                # Enrolled face images (auto-created)
├── captures/             # Intruder snapshots (auto-created)
├── intruder_logs.db      # SQLite database logging events (auto-created)
├── README.md             # This documentation file
```

***

## ⚙️ Configuration and Settings

- **Camera Index:** Change in `surveillance.py` if multiple cameras are connected:

```python
camera = cv2.VideoCapture(0)  # Change index if needed (1, 2, etc.)
```

- **Matching Tolerance:** Adjust matching strictness (default is 0.45):

```python
tolerance = 0.45
```

- **Alert Cooldown:** Time between alerts to prevent spam (default 5 seconds).

***

## 🔧 Technical Overview

### CNN Architecture

1. Input: 150x150 RGB face images
2. Convolutional Layers: Learn facial features via kernels
3. Pooling Layers: Dimensionality reduction with feature preservation
4. Dense Layers: Generate 128-dimensional embeddings (feature maps)
5. Output: Unique feature vector per face for matching

### Detection Pipeline

- Capture video frame → Detect faces (HOG + CNN) → Generate face encodings → Compare with enrolled encodings → Classify as authorized or intruder → Trigger alerts and logging for intruders.

***

## 🐛 Troubleshooting

- **Camera Not Detected:** Try different camera indices (`0`, `1`, `2`).
- **Face Recognition Too Slow:** Ensure good lighting; reduce video resolution for faster processing.
- **Emails Not Sent:** Confirm Gmail 2FA is enabled and App Password is correct.
- **No Sound:** Ensure `alert.mp3` or `alert.wav` is in the working folder. Install `pygame` as fallback.
- **Faces Not Recognized:** Re-enroll users with clearer images from multiple angles.

***

## 📄 License & Contribution

This project is open-source. Contributions, feature requests, and bug reports are welcome via pull requests and issues.

***

Built with ❤️ using Python, OpenCV, face_recognition, and deep learning techniques.

