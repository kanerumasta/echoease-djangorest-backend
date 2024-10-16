from django.db import models
from booking.models import Booking
from django.conf import settings
from artists.models import Artist
from decimal import Decimal

USER =  settings.AUTH_USER_MODEL
from django.db import models
from booking.models import Booking
from django.conf import settings
from artists.models import Artist
from decimal import Decimal

USER = settings.AUTH_USER_MODEL

class Payment(models.Model):
    payment_reference = models.CharField(max_length=15, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')


    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    client = models.ForeignKey(USER, on_delete=models.CASCADE, null=True, blank=True)  # Only for down payments and full payments
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)  # Only for payouts
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Only applicable for payouts

    payment_intent_id = models.CharField(max_length=255, unique=True)  # Token in payment gateway
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Only applicable for payments
    payment_gateway = models.CharField(max_length=50, null=True, blank=True)
    payer_email = models.CharField(max_length=50, null=True, blank=True)
    payer_name = models.CharField(max_length=50, null=True, blank=True)

    payment_type = models.CharField(max_length=25, choices=[
        ('downpayment', 'Downpayment'),
        ('final_payment', 'Final Payment'),
        ('payout', 'Payout'),
        ('refund', 'Refund'),
    ])

    def __str__(self):
        return f'Payment {self.pk} ({self.payment_type}) - {self.booking}'
