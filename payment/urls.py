from django.urls import path
from .views import CreateInvoiceView, invoice_webhook, payout_webhook, refund_success_webhook, refund_failed_webhook

urlpatterns=[
    path('create-invoice', CreateInvoiceView.as_view()),
    path('invoice_webhook', invoice_webhook),
    path('payout_webhook', payout_webhook),
    path('refund_success_webhook', refund_success_webhook),
    path('refund_failed_webhook', refund_failed_webhook),
]
