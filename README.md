# Smart Surveillance System

A smart home/office surveillance and face recognition system using Python, OpenCV, and face_recognition.  
Automatically detects intruders, sends alert emails with snapshots, plays a warning sound, and allows secure enrollment of authorized faces.

## Features

- **Live Surveillance:** Real-time camera monitoring with face detection and recognition.
- **Intruder Alerts:** Plays a loud alert sound and sends an email (with image and timestamp) if an unknown face is detected.
- **Face Enrollment:** Simple guided enrollment of new authorized persons (multi-pose image capturing).
- **Intruder Logging:** All intruder events (timestamp and image) logged in a local SQLite database.
- **Local Storage:** Intruder snapshots saved for review in a `captures/` folder.
- **User Menu:** Simple command-line interface for operation.

## Requirements

- Python 3.7+
- Webcam/camera
- Gmail account (App password for sending email alerts)

### Python Packages

```bash
pip install opencv-python face_recognition numpy playsound
```

## Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/smart-surveillance.git
cd smart-surveillance
```

2. **Set up required folders (auto-created if missing):**
   - `faces/` — For authorized persons’ images
   - `captures/` — For storing snapshots of detected intruders

3. **Configure Gmail (for email alerts):**
   - Enable 2FA on your Gmail account.
   - Create an **App Password** for your Google account and update it in `alert.py`:
     ```python
     sender = "your.email@gmail.com"
     password = "your-app-password"
     receiver = "destination.email@gmail.com"
     ```
   - (Optional) Adjust the email address as needed.

4. **Verify you have a sound file called `alert.mp3` in your working directory (for alarm sound).**

## How to Use

### 1. Run the Program

```bash
python surveillance.py
```

### 2. Main Menu

- **1. Run Surveillance:** Start monitoring. Press `q` to stop.
- **2. Enroll New Person:** Add a new face profile.
- **3. Exit:** Quit the system.

### 3. Enrolling a New Person

1. Choose "Enroll New Person" from the menu.
2. Enter the person's name (this will create a folder in `faces/`).
3. Follow the camera instructions (turn head, smile, etc.). 20 images will be captured.
4. Enrollment completes and the new face becomes authorized.

### 4. Surveillance Mode

- Known faces are labeled in **green** with their name.
- Unknown faces (“Intruder”) are labeled in **red**.
- On intruder detection:
    - A snapshot is saved.
    - Alert sound is played.
    - Email alert (with image & timestamp) is sent.
    - Event is logged in the `intruder_logs.db` SQLite database.

## File Overview

| File             | Purpose                                          |
|------------------|--------------------------------------------------|
| `surveillance.py`| Main menu, surveillance loop, database/logging   |
| `enroll.py`      | Handles face data enrollment for new people      |
| `alert.py`       | Sound alarm and email alert logic                |

## Notes & Customization

- **Camera Index:** If your webcam isn’t recognized, try changing the index in `cv2.VideoCapture(1)` to `0` or another number.
- **Face Recognition Threshold:** Adjust `tolerance=0.45` for stricter/looser matching.
- Works *offline* for detection (except for email alerts).
- Default email/password in code are for demonstration — always use your own with app passwords!

## Example Surveillance Screenshot

*Insert a demo screenshot here if available.*

## Troubleshooting

- **Sound issues:** Ensure `alert.mp3` exists and can be played on your system.
- **Face recognition slow:** Improve performance by capturing clearer, front-facing images during enrollment.
- **Gmail blocked sign-in:** Ensure you’re using Gmail App Passwords and not your regular password.

## Credits

- [OpenCV](https://opencv.org/)
- [face_recognition](https://github.com/ageitgey/face_recognition)
- Python Standard Library

**For questions or contributions, open an Issue or Pull Request!**
