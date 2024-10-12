from django.contrib import admin
from .models import Payment, DownPayment, Payout




admin.site.register(Payment)
admin.site.register(DownPayment)
admin.site.register(Payout)
