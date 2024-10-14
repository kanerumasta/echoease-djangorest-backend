from django.db import models
from booking.models import Booking
from django.conf import settings
from artists.models import Artist
from decimal import Decimal

USER =  settings.AUTH_USER_MODEL
class Payment(models.Model):
    payment_intent_id = models.CharField(max_length=50, unique=True) #Token in paypal
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payment")
    client  = models.ForeignKey(USER, on_delete=models.CASCADE)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2) #Payment service(E.g Paypal) processing fee
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(max_length=50,default='pending')
    payer_email = models.CharField(max_length=50, null=True, blank=True)
    payer_name = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return f'Payment {self.pk} refid:{self.payment_intent_id}'



class Payout(models.Model):
    payment_intent_id = models.CharField(max_length=255, unique=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE,related_name='payout')
    app_commission = models.DecimalField(max_digits=10,decimal_places=1,null=True)
    processing_fee = models.DecimalField(max_digits=10,decimal_places=1,null=True)
    payout_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50,default='pending')

    def __str__(self) -> str:
        return f'PAYMENT-{self.booking}'

class DownPayment(models.Model):
    payment_intent_id = models.CharField(max_length=255, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE,related_name='down_payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50) #gcash/paypal/paymaya
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50,default='pending')
    payer_email = models.CharField(max_length=50, null=True, blank=True)
    payer_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self) -> str:
        return f'DOWNPAYMENT-{self.booking}'


# class Payment
