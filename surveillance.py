# surveillance.py
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
    print("\n[INFO] Surveillance started. Press 'q' to stop.")
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
        print("\n=== RECENT INTRUDER LOGS ===")
        for log in logs:
            print(f"ID: {log[0]}, Time: {log[1]}, Image: {log[2]}")
    else:
        print("\n[INFO] No intruder logs found.")

def view_enrolled_faces():
    """Show all enrolled persons"""
    if not os.path.exists("faces") or not os.listdir("faces"):
        print("\n[INFO] No enrolled faces found.")
        return
    
    print("\n=== ENROLLED PERSONS ===")
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
        print("\n" + "="*50)
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
                print("\n[WARNING] No enrolled faces found. Please enroll at least one person first.")
                continue
            run_surveillance()
            
        elif choice == '2':
            name = input("\nEnter person's name: ").strip()
            if name:
                enroll(camera, name, load_known_faces)
            else:
                print("[ERROR] Name cannot be empty.")
                
        elif choice == '3':
            view_enrolled_faces()
            
        elif choice == '4':
            show_intruder_logs()
            
        elif choice == '5':
            print("\n👋 Thank you for using Smart Surveillance System!")
            camera.release()
            conn.close()
            break
            
        else:
            print("\n❌ Invalid choice. Please select 1-5.")
