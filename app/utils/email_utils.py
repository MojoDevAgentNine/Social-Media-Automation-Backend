# utils/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import EmailVerificationCode


def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))


def send_verification_email(to_email: str, verification_code: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = "Your Verification Code"

    body = f"""
    Your verification code is: {verification_code}

    This code will expire in 10 minutes.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def create_verification_code(db: Session, user_id: int) -> str:
    # Delete any existing unused codes for this user
    db.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_id == user_id,
        EmailVerificationCode.is_used == False
    ).delete()

    code = generate_verification_code()
    verification_code = EmailVerificationCode(
        user_id=user_id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )

    db.add(verification_code)
    db.commit()
    db.refresh(verification_code)

    return code
