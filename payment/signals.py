from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Refund
from transaction.models import Transaction
from logs.models import TransactionLogs


from booking.models import Booking


@receiver(post_save, sender=Payment)
def create_payment_transaction(sender, instance, created, **kwargs):
    if created:
        transaction_type = instance.payment_type
        if transaction_type == 'payout':
            user = instance.booking.artist.user
        else:
            user  = instance.booking.client
        try:
            Transaction.objects.create(
                payment=instance,
                transaction_type=transaction_type,
                booking=instance.booking,
                amount=instance.amount,
                user = user
            )
            print(f'Created transaction for booking {instance.booking.id}')
        except Exception as e:
            print(f'Error creating transaction in signals: {e}')

@receiver(post_save, sender=Payment)
def log_payment(sender, instance, created, **kwargs):
    if created:
        try:
            TransactionLogs.objects.create(
                transaction_type = "PAYMENT",
                message=f'{instance.payment_type} received for booking {instance.booking.id}'
            )
        except Exception as e:
            print(f'Error logging payment in signals: {e}')

@receiver(post_save, sender=Refund)
def log_transaction(sender, instance, created, **kwargs):
    if created:
        try:
            TransactionLogs.objects.create(
                transaction_type = 'REFUND',
                message=f'Refund initiated for payment {instance.payment.id}'
            )
        except Exception as e:
            print(f'Error logging refund in signals: {e}')
