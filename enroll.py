# enroll.py
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
    
    print(f"\n{'='*60}")
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
    
    print("\n🚀 Starting capture in 3 seconds...")
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
            print("\n❌ [CANCELLED] Enrollment interrupted by user.")
            cv2.destroyAllWindows()
            return False
    
    cv2.destroyAllWindows()
    
    # Reload known faces
    print("\n🔄 Processing captured images and updating face database...")
    load_known_faces_callback()
    
    print(f"\n✅ [SUCCESS] Enrollment completed for {name}!")
    print(f"📁 {count} face images saved to: {folder}")
    print("🧠 Face encodings generated using CNN feature extraction")
    print("-" * 60)
    
    return True
