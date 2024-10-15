from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking

@receiver(post_save, sender = Booking)
def generate_booking_reference(sender, instance, created, **kwargs):
    if created and not instance.booking_reference:
        instance.booking_reference = f"BKG{instance.id:06d}"
        instance.save()
