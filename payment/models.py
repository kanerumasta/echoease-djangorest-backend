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
    payment_reference = models.CharField(max_length=15, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')
    payment_id= models.CharField(max_length=255)
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
    is_refunded = models.BooleanField(default=False)
    refund_transaction_id = models.CharField(max_length=255, null=True, blank=True)

    payment_type = models.CharField(max_length=25, choices=[
        ('downpayment', 'Downpayment'),
        ('final_payment', 'Final Payment'),
        ('payout', 'Payout'),
        ('refund', 'Refund'),
    ])


    def refund(self):
        print('attempt refund now')
        url = f"https://api.paymongo.com/refunds"
        auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {auth_key}",
            "Content-Type": "application/json",
        }

        payload = {
                    "data": {
                        "attributes": {
                        "amount": int(self.net_amount) * 100,
                        "payment_id": self.payment_id,
                        "reason": "others"
                        }
                    }
                }


        response = requests.post(url=url, headers=headers, json=payload)
        print(response)
        rt = response.json()
        print(rt)

        if response.status_code == 200:
            refund_data = response.json()
            self.payment_status = 'refunded'
            self.is_refunded = True
            self.refund_transaction_id = refund_data['data']['id']
            self.save()

    def __str__(self):
        return f'Payment {self.pk} ({self.payment_type}) - {self.booking}'

class Payout(models.Model):
    booking = models.ForeignKey(Booking, related_name='bookings', on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, related_name='artists', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout_date = models.DateTimeField(auto_now_add=True)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    reference_id = models.CharField(max_length=255)
