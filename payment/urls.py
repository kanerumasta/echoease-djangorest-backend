from django.urls import path
from .views import DownPaymentView,CreateDownPaymentIntentView,AttachPaymentMethodView

urlpatterns =[
    path('create-downpayment-intent', CreateDownPaymentIntentView.as_view(), name='intent'),
    path('attach-downpayment-intent', AttachPaymentMethodView.as_view(), name='attch'),
]
