import xendit
from xendit.apis import BalanceApi
from pprint import pprint
from django.conf import settings
import time



import xendit.payout
import xendit.refund
from payment.models import Payment
from xendit.apis import PayoutApi, InvoiceApi, RefundApi
from xendit.invoice.model.create_invoice_request import CreateInvoiceRequest
from xendit.payout.model.create_payout_request import CreatePayoutRequest
from xendit.refund.model.create_refund import CreateRefund
from xendit.payout.model.get_payouts200_response_data_inner import GetPayouts200ResponseDataInner
from xendit.payout.model.error import Error
from booking.models import Booking

xendit.set_api_key(settings.XENDIT_SECRET_KEY)

client = xendit.ApiClient()
api_instance = PayoutApi(client)
refund_api = RefundApi(client)
invoice_api_instance = InvoiceApi(client)


def create_payment_invoice(reference_id,redirect_url, amount,payment_type, customer_email, description="Payment for service"):
    create_invoice_request = {
        "external_id": reference_id,
        "amount": amount,
        "payer_email": customer_email,
        "description": description,
        "currency": "PHP",
        "metadata":{
            "payment_type":str(payment_type)
        },
        "success_redirect_url":redirect_url,
         "payment_methods": ["GCASH","PAYMAYA","GRABPAY"]
    }

    try:
        # Create an invoice
        api_response = invoice_api_instance.create_invoice(
            create_invoice_request=create_invoice_request ) # type: ignore
        pprint(api_response)
        print("Invoice created successfully!")
        print(api_response.invoice_url)
        return api_response.invoice_url  # URL that the customer can use to pay
    except xendit.XenditSdkException as e:
        print("XenditSdkException:", e)
        return None
def get_invoice_details(invoice_id):
    try:
        api_response = invoice_api_instance.get_invoice_by_id(invoice_id=invoice_id)
        pprint(api_response)
        return api_response
    except xendit.XenditSdkException as e:
        print("XenditSdkException:", e)
        return None
def send_payout(booking_id,amount, channel_code,description="Payout Payment"):
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        print(f"Booking with id {booking_id} does not exist.")
        return None
    artist = booking.artist
    if not artist.account_holder_name or not artist.get_account_number() or not artist.channel_code:
        print('artist channel code or account holder name or account number is null')
        return None
    idempotence_key = f'Payout||{booking.booking_reference}'
    create_payout_request = {
        "reference_id": str(booking.booking_reference or booking.pk),
        "channel_code":channel_code,
        "currency": "PHP",
        "channel_properties":{
            "account_holder_name":artist.account_holder_name,
            "account_number":artist.get_account_number(),
        },
        "amount":float(amount),

    }
    try:
        api_response = api_instance.create_payout(idempotency_key=idempotence_key, create_payout_request=create_payout_request) #type: ignore
        print(api_response)
    except xendit.XenditSdkException as e:
        print('XenditSdkException: ',e)

def send_compensation_fee(booking_id, amount, channel_code, description="Compenstation"):
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        print(f"Booking with id {booking_id} does not exist.")
        return None
    artist = booking.artist
    if not artist.account_holder_name or not artist.get_account_number() or not artist.channel_code:
        print('artist channel code or account holder name or account number is null')
        return None
    idempotence_key = f'CompensationFee||{booking.booking_reference}'
    create_payout_request = {
        "reference_id": str(booking.booking_reference or booking.pk),
        "channel_code":channel_code,
        "currency": "PHP",
        "channel_properties":{
            "account_holder_name":artist.account_holder_name,
            "account_number":artist.get_account_number(),
        },
        "amount": float(amount),
    }

    try:
        api_response = api_instance.create_payout(idempotency_key=idempotence_key, create_payout_request=create_payout_request) #type: ignore
        print(api_response)
    except xendit.XenditSdkException as e:
        print('XenditSdkException: ',e)


def is_valid_payment_type(payment_type):
    valid_payment_types = [choice[0] for choice in Payment.PAYMENT_TYPE_CHOICES]
    return payment_type in valid_payment_types

def refund_payment(amount, invoice_id, payment_id, reason): #payment_pk is from database
    refund_request = CreateRefund(
        amount=float(amount),
        invoice_id=invoice_id,
        description='Refund for payment',
        currency='PHP',
        metadata={
            'payment_id': payment_id,
        },
        reason="CANCELLATION"
    )



    try:
        refund = refund_api.create_refund(
            idempotency_key=f'Refund::{payment_id}',
            create_refund=refund_request,
        )
        return True
    except xendit.XenditSdkException as e:

        print('XenditSdkException: ',e)
        return False
