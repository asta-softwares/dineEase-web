from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(user, code):
    """
    Send a confirmation email with a 6-digit code.
    """
    subject = "Confirm Your Email Address with DineEase"
    message = f"""
    Hello {user.first_name},

    Thank you for registering with DineEase. 
    Please confirm your email address by using the following code:

    Confirmation Code: {code}

    If you did not register, please ignore this email.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['mico.dahang@gmail.com'] # NOTE: [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")
