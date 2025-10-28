from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_verification_email(email, otp_code):
    """
    Send a verification OTP email asynchronously.
    """
    subject = "Your Verification Code"
    message = f"Hello,\n\nYour OTP code is: {otp_code}\n\nThank you!"
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
        return f"Failed to send email to {email}: {str(e)}"
