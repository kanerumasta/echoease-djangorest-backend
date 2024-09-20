from django.urls import path
from .views import (PaypalOrderView, PaypalCapturePaymentView)

urlpatterns =[
    path('create-order', PaypalOrderView.as_view(), name='ordercreate'),
    path('capture-payment', PaypalCapturePaymentView.as_view()),

   
]