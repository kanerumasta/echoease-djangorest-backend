from django.db import models
from booking.models import Booking
from django.conf import settings
from artists.models import Artist
from decimal import Decimal

USER =  settings.AUTH_USER_MODEL
class Payment(models.Model):
    reference_id = models.CharField(max_length=50) #Token in paypal
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    client  = models.ForeignKey(USER, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2) #Payment service(E.g Paypal) processing fee
    payment_method = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.app_commission = self.amount - Decimal('0.12') #12% COMMISSION CHANGEABLE
        super().save(*args, **kwargs)

    @property
    def net_amount(self):
        return self.amount - self.processing_fee

    def __str__(self):
        return f'Payment {self.pk} refid:{self.reference_id}'



class Payout(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    app_commission = models.DecimalField(max_digits=10,decimal_places=1,null=True)
    payout_date = models.DateTimeField(auto_now_add=True)


class DownPayment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    gateway = models.CharField(max_length=50) #gcash/paypal/paymaya
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
