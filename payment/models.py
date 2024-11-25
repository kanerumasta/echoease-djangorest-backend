from django.db import models
from booking.models import Booking
from django.conf import settings
from artists.models import Artist
from decimal import Decimal
import base64
import requests


USER =  settings.AUTH_USER_MODEL
from django.db import models
from booking.models import Booking
from django.conf import settings
from artists.models import Artist
from decimal import Decimal

USER = settings.AUTH_USER_MODEL

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('downpayment', 'Downpayment'),
        ('final_payment', 'Final Payment'),
        ('payout', 'Payout'),
    ]
    user = models.ForeignKey(USER,on_delete=models.CASCADE, null=True, blank=True) #payer or receiver
    title = models.TextField(null=True, blank=True)
    payment_reference = models.CharField(max_length=15, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_id=models.CharField(max_length=255, blank=True,null=True) #FROM XENDIT payment_id
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    payer_channel = models.CharField(max_length=50, null=True, blank=True)
    payer_email = models.CharField(max_length=50, null=True, blank=True)
    is_refunded = models.BooleanField(default=False)
    echoease_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    payment_type = models.CharField(max_length=25, choices=PAYMENT_TYPE_CHOICES)
    def __str__(self):
        return f'Payment {self.pk} ({self.payment_type}) - {self.booking}'


class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="refunds")
    refund_id = models.CharField(max_length=255)#from xendit
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'Refund {self.pk} - {self.payment}'
