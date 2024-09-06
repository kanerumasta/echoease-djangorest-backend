from django.urls import path
from .views import PaypalPaymentView, PaypalValidatePaymentView

urlpatterns =[
    path('create/', PaypalPaymentView.as_view(), name='ordercreate'),
path('validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),
]