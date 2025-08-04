# alert.py
import smtplib
import playsound
from email.mime.text import MIMEText  # ✅ Fix here
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os

def play_sound():
    try:
        playsound.playsound("alert.mp3")  # Make sure this file exists
    except Exception as e:
        print(f"[ERROR] Couldn't play sound: {e}")

def send_email_alert(image_path, timestamp):
    sender = "love.mail.000000@gmail.com"
    password = "gobb lgvl adib jnsc"  # App password from Gmail
    receiver = "love.mail.000000@gmail.com"

    msg = MIMEMultipart()
    msg["Subject"] = "🚨 Intruder Alert!"
    msg["From"] = sender
    msg["To"] = receiver

    body = f"Intruder detected at {timestamp}. See attached image."
    msg.attach(MIMEText(body))  # ✅ Fix here

    try:
        with open(image_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-Disposition", "attachment", filename=os.path.basename(image_path))
            msg.attach(img)
    except Exception as e:
        print(f"[ERROR] Failed to attach image: {e}")
        return

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("[EMAIL SENT] Intruder alert email sent.")
    except Exception as e:
        print(f"[ERROR] Email sending failed: {e}")
