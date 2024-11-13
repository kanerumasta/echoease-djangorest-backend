from django.db import models
from booking.models import Booking

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('downpayment', 'Down Payment'),
        ('final_payment', 'Final Payment'),
        ('payout', 'Payout'),
        ('refund', 'Refund'),
    ]
    transaction_reference = models.CharField(max_length=15, blank=True, unique=True)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
