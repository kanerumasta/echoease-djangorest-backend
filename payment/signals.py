from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from transaction.models import Transaction


from booking.models import Booking

# class Transaction(models.Model):
#     TRANSACTION_TYPES = [
#         ('downpayment', 'Down Payment'),
#         ('final_payment', 'Final Payment'),
#         ('payout', 'Payout'),
#         ('refund', 'Refund'),
#     ]
#     transaction_reference = models.CharField(max_length=15, blank=True, unique=True)
#     transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-created_at']


@receiver(post_save, sender=Payment)
def create_payment_transaction(sender, instance, created, **kwargs):
    if created:
        transaction_type = instance.payment_type
        try:
            Transaction.objects.create(
                transaction_type=transaction_type,
                booking=instance.booking,
                amount=instance.amount
            )
            print(f'Created transaction for booking {instance.booking.id}')
        except Exception as e:
            print(f'Error creating transaction in signals: {e}')
