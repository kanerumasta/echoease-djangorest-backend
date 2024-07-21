from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Artist, Portfolio

@receiver(post_save, sender = Artist)
def generate_slug_stage_name(sender, instance,created, **kwargs):
    if created:
        try:
            instance.slug = instance.user.full_name.replace(' ','-')
            instance.stage_name = instance.user.full_name
            instance.save()
        except:
            print('ERROR(signals): cant generate slug or stage name')

@receiver(post_save, sender = Artist)
def create_portfolio(sender, instance, created, **kwargs):
    if created:
        try:
            Portfolio.objects.create(artist = instance)
        except Exception as e:
            print('Error(signals): failed creating portfolio')

