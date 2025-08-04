# main.py
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
cursor.execute('''CREATE TABLE IF NOT EXISTS intruders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    image_path TEXT
)''')
conn.commit()

# === CAMERA SETUP ===
camera = cv2.VideoCapture(1)

# === KNOWN FACES ===
known_encodings = []
known_names = []

def load_known_faces():
    known_encodings.clear()
    known_names.clear()
    for person in os.listdir("faces"):
        person_folder = os.path.join("faces", person)
        if os.path.isdir(person_folder):
            for file in os.listdir(person_folder):
                image_path = os.path.join(person_folder, file)
                image = face_recognition.load_image_file(image_path)
                locations = face_recognition.face_locations(image)
                encodings = face_recognition.face_encodings(image, locations)
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(person)

load_known_faces()

# === SURVEILLANCE FUNCTION ===
def run_surveillance():
    print("\n[INFO] Surveillance started. Press 'q' to stop.")
    last_intruder_time = 0
    cooldown = 5  # seconds

    while True:
        ret, frame = camera.read()
        if not ret:
            break

        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        names = []
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.45)
            name = "Intruder"
            confidence = 0
            if True in matches:
                distances = face_recognition.face_distance(known_encodings, encoding)
                best_match_index = np.argmin(distances)
                if distances[best_match_index] < 0.45:
                    name = known_names[best_match_index]
                    confidence = (1 - distances[best_match_index]) * 100
            names.append((name, confidence))

        for (top, right, bottom, left), (name, confidence) in zip(face_locations, names):
            top *= 4; right *= 4; bottom *= 4; left *= 4
            color = (0, 255, 0) if name != "Intruder" else (0, 0, 255)
            label = f"{name} ({confidence:.1f}%)"

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            if name == "Intruder" and (time.time() - last_intruder_time) > cooldown:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"captures/intruder_{timestamp}.jpg"
                cv2.imwrite(save_path, frame)
                cursor.execute("INSERT INTO intruders (timestamp, image_path) VALUES (?, ?)", (timestamp, save_path))
                conn.commit()
                print(f"[ALERT] Intruder logged at {timestamp}")
                play_sound()
                send_email_alert(save_path, timestamp)
                last_intruder_time = time.time()

        cv2.imshow("Surveillance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    print("[EXIT] Surveillance ended.")

# === FOLDER SETUP ===
if __name__ == "__main__":
    os.makedirs("faces", exist_ok=True)
    os.makedirs("captures", exist_ok=True)

    while True:
        print("\n=== SMART SURVEILLANCE MENU ===")
        print("1. Run Surveillance")
        print("2. Enroll New Person")
        print("3. Exit")
        choice = input("Enter choice (1/2/3): ")

        if choice == '1':
            run_surveillance()
        elif choice == '2':
            name = input("Enter person's name: ")
            enroll(camera, name, load_known_faces)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2 or 3.")
