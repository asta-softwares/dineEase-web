from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order   
from core.models import VerificationCode

@receiver(post_save, sender=Order)
def create_verification_code(sender, instance, created, **kwargs):
    """
    Signal to create or reuse a VerificationCode when an Order is created.
    """
    if created:
        # Check if a VerificationCode already exists for the customer
        verification_code, created_code = VerificationCode.objects.get_or_create(user=instance.customer)

        # Generate a new code only if the VerificationCode is newly created
        if created_code:
            verification_code.generate_code()

        # Associate the verification code with the order
        instance.verification_code = verification_code
        instance.save()