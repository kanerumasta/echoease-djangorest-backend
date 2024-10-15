from django.db import models
from booking.models import Booking
from users.models import UserAccount
from decimal import Decimal
from artists.models import Artist

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('downpayment', 'Downpayment'),
        ('final_payment', 'Final Payment'),
        ('payout', 'Payout'),
        ('refund', 'Refund'),
    ]

    transaction_reference = models.CharField(max_length=15, blank=True, unique=True)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    client = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50,default="pending", choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_gateway = models.CharField(max_length=50)
    payment_intent_id = models.CharField(max_length=50)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payer_email = models.CharField(max_length=150, null=True)
    payer_name = models.CharField(max_length=150, null=True)

    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0.00))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
