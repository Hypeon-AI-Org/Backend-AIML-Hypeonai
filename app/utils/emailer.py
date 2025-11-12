from aiosmtplib import SMTP
from email.message import EmailMessage
from app.core.config import settings

async def send_reset_email(to_email: str, reset_url: str):
    """
    Send a password reset email to the specified email address.
    
    Args:
        to_email (str): The recipient's email address
        reset_url (str): The password reset URL to include in the email
    """
    # Check if email settings are configured
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASS:
        raise ValueError("Email settings are not properly configured")
    
    # Ensure we have non-None values for SMTP authentication
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS
    
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM or smtp_user
    msg["To"] = to_email
    msg["Subject"] = "Reset your Hypeon password"
    msg.set_content(f"Reset your password using this link (valid for 1 hour): {reset_url}")
    msg.add_alternative(f"""
        <p>Reset your password using this link (valid for 1 hour):</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
    """, subtype="html")

    smtp = SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT)
    await smtp.connect()
    await smtp.starttls()
    # Type checker now sees these as non-None values
    await smtp.login(smtp_user, smtp_pass)
    await smtp.send_message(msg)
    await smtp.quit()