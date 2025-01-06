from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order   
from core.models import VerificationCode
from django.db import transaction

@receiver(post_save, sender=Order)
def create_verification_code(sender, instance, created, **kwargs):
    """
    Signal to create a new VerificationCode for an Order.
    """
    if created:
        try:
            with transaction.atomic():
                # Always create a new VerificationCode for the user
                verification_code = VerificationCode.objects.create(user=instance.customer)
                verification_code.generate_code()

                # Associate the new VerificationCode with the order
                instance.verification_code = verification_code
                instance.save(update_fields=['verification_code'])
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error creating verification code: {e}")
            raise e