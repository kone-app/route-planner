import smtplib
from email.mime.text import MIMEText
from journey_service import config

def send_email(body_text):
    try:
        msg = MIMEText("\n".join(body_text))
        msg["From"] = config.FROM_EMAIL
        msg["To"] = config.TO_EMAIL
        msg["Subject"] = "Journey Details"

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(config.FROM_EMAIL, config.GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return "Email Sent"

    except Exception as e:
        print(f"Email failed: {e}")
        return "Email Failed"

