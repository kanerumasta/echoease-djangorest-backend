from django.urls import path
from .views import CreateInvoiceView, invoice_webhook, payout_webhook
# from .views import CreateDownPaymentIntentView,AttachPaymentMethodView,DownPaymentStatusView,FinalPaymentIntentView, AttachFinalPaymentMethodView, FinalPaymentStatusView

# urlpatterns =[
#     path('create-downpayment-intent', CreateDownPaymentIntentView.as_view(), name='downpayment-intent'),
#     path('attach-downpayment-intent', AttachPaymentMethodView.as_view(), name='downpayment-attach'),
#     path('retrieve-downpayment-intent', DownPaymentStatusView.as_view(), name='downpayment-retrieve'),
#     path('create-finalpayment-intent', FinalPaymentIntentView.as_view(), name='finalpayment-intent'),
#     path('attach-finalpayment-intent', AttachFinalPaymentMethodView.as_view(), name='final-payment-attach'),
#     path('retrieve-finalpayment-intent', FinalPaymentStatusView.as_view(), name='final-payment-retrieve'),
# ]


urlpatterns=[
    path('create-invoice', CreateInvoiceView.as_view()),
    path('invoice_webhook', invoice_webhook),
    path('payout_webhook', payout_webhook)
]
