from django.urls import path
from .views import (PaypalOrderView, PaypalCapturePaymentView, CreatePaymongoPaymentLinkView)

urlpatterns =[
    path('create-order', PaypalOrderView.as_view(), name='ordercreate'),
    path('capture-payment', PaypalCapturePaymentView.as_view()),
    path('create-link', CreatePaymongoPaymentLinkView.as_view())

   
]