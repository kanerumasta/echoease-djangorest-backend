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

#     {'amount': 7800,
#  'created': '2024-11-13T08:36:08.538Z',
#  'currency': 'PHP',
#  'description': 'Payment for service',
#  'ewallet_type': 'GRABPAY',
#  'external_id': 'Y9283943',
#  'id': '673464f8a714627104c5cbd7',
#  'is_high': False,
#  'merchant_name': 'Echoease',
#  'paid_amount': 7800,
#  'paid_at': '2024-11-13T08:47:58.488Z',
#  'payer_email': 'donmacnino@gmail.com',
#  'payment_channel': 'GRABPAY',
#  'payment_id': 'ewc_2f2ebe49-c011-48e9-8190-04241f60fb35',
#  'payment_method': 'EWALLET',
#  'payment_method_id': 'pm-f4c5a7fe-2506-4326-84b5-7e5b54cb60bb',
#  'status': 'PAID',
#  'success_redirect_url': 'https://example.com',
#  'updated': '2024-11-13T08:48:00.340Z',
#  'user_id': '6722f50cb1f853a4bd388291'}

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('downpayment', 'Downpayment'),
        ('final_payment', 'Final Payment'),
        ('payout', 'Payout'),
        ('refund', 'Refund'),
    ]
    user = models.ForeignKey(USER,on_delete=models.CASCADE, null=True, blank=True) #payer or receiver
    title = models.TextField(null=True, blank=True)
    payment_reference = models.CharField(max_length=15, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payer_channel = models.CharField(max_length=50, null=True, blank=True)
    payer_email = models.CharField(max_length=50, null=True, blank=True)
    is_refunded = models.BooleanField(default=False)
    refund_transaction_id = models.CharField(max_length=255, null=True, blank=True)

    payment_type = models.CharField(max_length=25, choices=PAYMENT_TYPE_CHOICES)


    # def refund(self):
    #     print('attempt refund now')
    #     url = f"https://api.paymongo.com/refunds"
    #     auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
    #     headers = {
    #         "Authorization": f"Basic {auth_key}",
    #         "Content-Type": "application/json",
    #     }

    #     payload = {
    #                 "data": {
    #                     "attributes": {
    #                     "amount": int(self.net_amount) * 100,
    #                     "payment_id": self.payment_id,
    #                     "reason": "others"
    #                     }
    #                 }
    #             }
    #     response = requests.post(url=url, headers=headers, json=payload)
    #     print(response)
    #     rt = response.json()


    #     if response.status_code == 200:
    #         refund_data = response.json()
    #         self.payment_status = 'refunded'
    #         self.is_refunded = True
    #         self.refund_transaction_id = refund_data['data']['id']
    #         self.save()

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
