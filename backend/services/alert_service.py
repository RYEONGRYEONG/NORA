import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

def alert_if_heavy_rain(user_email, farm_name, forecast_time, precip):
    load_dotenv()
    sender_email = os.getenv("EMAIL")
    sender_password = os.getenv("EMAIL_PW")

    subject = f"[NORA Alert] Heavy Rain Warning for {farm_name}"
    body = f"""Dear Farmer,
Based on the latest Met Éireann forecast, heavy rainfall is expected at your farm:

-----------------------------------
Farm Name: {farm_name}
Expected Time: {forecast_time}
Predicted Rainfall: {precip} mm
-----------------------------------

To prevent nutrient leaching and protect local water quality,
please REFRAIN from spreading fertiliser for the next 48 hours.

Stay safe and thank you for your consideration.

* This is an auto-generated email. Please do not reply.
"""
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = user_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)