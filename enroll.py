# enroll.py
import os
import cv2
import face_recognition

def enroll(camera, name, load_known_faces):
    folder = os.path.join("faces", name)
    os.makedirs(folder, exist_ok=True)

    print(f"\n[INFO] Starting enrollment for: {name}")
    print("[INSTRUCTIONS] Look at the camera. Turn your face left, right, up, and smile naturally.")
    print("[TIP] Press 'q' to cancel anytime.")

    count = 0
    total_required = 20

    while count < total_required:
        ret, frame = camera.read()
        if not ret:
            print("[ERROR] Failed to grab frame from camera.")
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            for top, right, bottom, left in face_locations:
                face_img = rgb_frame[top:bottom, left:right]
                if face_img.size == 0:
                    continue

                save_path = os.path.join(folder, f"{count}.jpg")
                bgr_face = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
                cv2.imwrite(save_path, bgr_face)
                count += 1
                print(f"[{count}/{total_required}] Captured")
        else:
            cv2.putText(frame, "No face detected. Adjust position.", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.putText(frame, f"Capturing images: {count}/{total_required}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.imshow("Enrollment", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[CANCELLED] Enrollment interrupted.")
            break

    cv2.destroyAllWindows()
    load_known_faces()
    print("[DONE] Enrollment complete!")
