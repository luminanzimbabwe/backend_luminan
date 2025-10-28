# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_verification_email(email: str, otp_code: str, expiry_minutes: int):
    """
    Send a verification OTP email asynchronously.
    
    Args:
        email (str): Recipient email address
        otp_code (str): The OTP code to send
        expiry_minutes (int): How long the OTP is valid
    """
    subject = "Your LuminaN OTP Verification Code"
    message = (
        f"Hello,\n\n"
        f"Your OTP code is: {otp_code}\n"
        f"It will expire in {expiry_minutes} minutes.\n\n"
        "Thank you!"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False
        )
        return f"Email sent successfully to {email}"
    except Exception as e:
        # You can also log this properly with Django logger
        print(f"❌ Failed to send OTP to {email}: {e}")
        return f"Failed to send email to {email}: {str(e)}"
