from django.urls import path
from .views import PaypalPaymentView, PaypalValidatePaymentView, PayPalPayoutView

urlpatterns =[
    path('create/', PaypalPaymentView.as_view(), name='ordercreate'),
path('validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),
path('payout',PayPalPayoutView.as_view())
]