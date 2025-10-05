# alert.py
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
            os.system("echo -e '\a'")
            print("[SOUND] System beep played (Unix)")
        except:
            print("[WARNING] Could not play any alert sound")

def send_email_alert(image_path, timestamp):
    """
    Send email alert with intruder image
    Configure your Gmail settings below
    """
    # ⚠️ IMPORTANT: Replace with your own Gmail credentials
    sender = "love.mail.000000@gmail.com"
    password = "gobb lgvl adib jnsc"  # App password from Gmail
    receiver = "love.mail.000000@gmail.com"
    
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
