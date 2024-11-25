from django.db.models.signals import post_save

from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not instance.is_staff:
            try:
                profile = Profile.objects.create()
                profile.user = instance
                profile.save()
            except:
                print(f'ERROR: cant create profile to user {instance.full_name}')
