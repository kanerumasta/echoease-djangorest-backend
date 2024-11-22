from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction

@receiver(post_save, sender = Transaction)
def generate_transaction_reference(sender, instance, created, **kwargs):
    if created and not instance.transaction_reference:
        try:
            instance.transaction_reference = f'TSN{instance.id:06d}'
            instance.save()
        except Exception as e:
            print(f'Error(signals): Failed to generate transaction reference for transaction {instance.pk}: {str(e)}')
