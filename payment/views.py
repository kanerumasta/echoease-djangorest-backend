from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from booking.models import Booking
from django.http import Http404
from payment.models import Payment
from decimal import Decimal, InvalidOperation
from django.conf import settings
from pprint import pprint
import base64
import requests
from notification.utils import notify_artist_of_paid_downpayment
from notification.models import Notification
from django.conf import settings
from .utils import send_payout, create_payment_invoice, get_invoice_details, is_valid_payment_type
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse


USER = settings.AUTH_USER_MODEL


# class DownPaymentStatusView(APIView):
#     def post(self, request):
#         payment_intent_id = request.data.get("payment_intent_id")
#         if not payment_intent_id:
#             return Response({'error':'payment_intent_id is required'},status=status.HTTP_400_BAD_REQUEST)

#         url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
#         auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
#         headers = {
#             "Authorization": f"Basic {auth_key}",
#             "Content-Type": "application/json",
#         }

#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             payment_intent = response.json()
#             print(payment_intent)

#             intent_status = payment_intent['data']['attributes']['status']

#             # Getting booking id reference
#             booking_id = payment_intent['data']['attributes']['metadata']['booking_id']
#             booking = get_object_or_404(Booking, id= booking_id)

#             existing_downpayment = Payment.objects.filter(booking=booking, payment_type = 'downpayment').exists()


#             if not existing_downpayment:
#             # No existing downpayment, create a new one
#                 payment_data = payment_intent['data']['attributes']['payments'][0]['attributes']
#                 fee = payment_data['fee']
#                 net_amount = payment_data['net_amount']
#                 gross_amount = payment_data['amount']
#                 email = payment_data['billing']['email']
#                 name = payment_data['billing']['name']
#                 payment_status = payment_data['status']
#                 payment_id = payment_intent['data']['attributes']['payments'][0]['id']
#                 payment_method_type = payment_data['source']['type']

#                 # Convert amounts
#                 gateway_fee = Decimal(fee) / Decimal(100)
#                 net_amount = Decimal(net_amount)/ Decimal(100)
#                 gross_amount = Decimal(gross_amount) / Decimal(100)

#                 # Create new downpayment instance
#                 downpayment = Payment.objects.create(
#                     payment_type = 'downpayment',
#                     payment_id = payment_id,
#                     booking=booking,
#                     client = booking.client,
#                     payment_intent_id=payment_intent['data']['id'],
#                     amount=gross_amount,
#                     service_fee=gateway_fee,
#                     payment_gateway = payment_method_type,
#                     net_amount=net_amount,
#                     payment_status='paid',
#                     payer_email=email,
#                     payer_name=name
#                 )
#                 print("Downpayment created successfully.")
#                 #create notif
#                 # notification_choices = [
#                 #     ('admin', 'Admin'),
#                 #     ('message', 'Message'),
#                 #     ('new_booking', 'New Booking'),
#                 #     ('new_follower', 'New Follower'),
#                 #     ('booking_confirmation', 'Booking Confirmation'),
#                 #     ('booking_rejected', 'Booking Rejected'),
#                 #     ('payment_reminder', 'Payment Reminder'),
#                 #     ('event_reminder', 'Event Reminder'),
#                 # ]

#                 # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, related_name='booking_notifications')
#                 # notification_type = models.CharField(max_length=50, choices=notification_choices)
#                 # title = models.CharField(max_length=255)
#                 # description = models.TextField()\

#                 # booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.CASCADE)
#                 # message = models.CharField(max_length=255,null=True, blank=True)
#                 # follower = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="notifications_as_follower", on_delete=models.CASCADE)

#                 # is_read = models.BooleanField(default=False)
#                 # created_at = models.DateTimeField(auto_now_add=True)
#                 try:

#                     notification = Notification.objects.create(
#                         notification_type = 'downpayment_paid',
#                         user = booking.artist.user,
#                         title="Downpayment Received! Your Event is Ready!",
#                         description=f"Great news! Echoer {booking.client.first_name.title()} {booking.client.last_name.title()} has successfully paid the downpayment for your confirmed booking . Your event is now all set and ready to go. We’re excited for the big day!",  # type: ignore
#                         booking=booking
#                     )
#                 except Exception as e:
#                     print("failed create notification")

#                 #update booking status
#                 booking.downpayment_paid()
#                 notify_artist_of_paid_downpayment(artist=booking.artist.user, booking=booking)

#             else:
#                 # Downpayment already exists, take no action
#                 print("Downpayment already exists for this booking.")
#             if intent_status == 'succeeded':
#                 return Response({"status": "success", "booking_id":booking.pk}, status=status.HTTP_200_OK)
#             elif intent_status == 'awaiting_payment_method':
#                 return Response({"status": "pending"}, status=status.HTTP_200_OK)
#             elif intent_status == 'awaiting_next_action':
#                 return Response({"status": "pending_redirect"}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(response.json(), status=response.status_code)

# class CreateDownPaymentIntentView(APIView):
#     def post(self, request):
#         currency = request.data.get('currency', 'PHP')
#         booking_id = request.data.get('booking')
#         booking = get_object_or_404(Booking, id=booking_id)

#         # Calculate downpayment amount (20% of the rate)

#         downpayment_amount = booking.calculate_downpayment().quantize(Decimal('0.01'))
#         # Log downpayment amount for debugging
#         print('Downpayment Amount:', downpayment_amount)

#         # Convert downpayment to integer cents
#         amount_in_cents = int(downpayment_amount * 100)
#         print('Amount in Cents:', amount_in_cents)

#         # Prepare PayMongo API request
#         url = 'https://api.paymongo.com/v1/payment_intents'
#         secret_key = settings.PAYMONGO_SECRET_KEY
#         auth_key = base64.b64encode(f'{secret_key}:'.encode('utf-8')).decode('utf-8')
#         headers = {
#             'Authorization': f'Basic {auth_key}',
#             'Content-Type': 'application/json'
#         }

#         payload = {
#             'data': {
#                 'attributes': {
#                     'amount': amount_in_cents,
#                     'payment_method_allowed': ['gcash', 'paymaya'],
#                     'currency': currency,
#                     'description': f'Booking down payment for {booking.artist.user.first_name} {booking.artist.user.last_name}',
#                     'metadata': {
#                         'booking_id':str(booking.pk)
#                     }
#                 }
#             }
#         }

#         # Make the API request to PayMongo
#         response = requests.post(url=url, json=payload, headers=headers)

#         # Check the response status and handle accordingly
#         if response.status_code == 200:
#             payment_intent_data = response.json()
#             payment_intent_id = payment_intent_data['data']['id']
#             return Response({"payment_intent_id": payment_intent_id}, status=status.HTTP_200_OK)

#         # Handle errors from PayMongo
#         return Response(response.json(), status=response.status_code)

# class AttachPaymentMethodView(APIView):
#     def post(self, request):
#         payment_intent_id = request.data.get("payment_intent_id")
#         payment_method = request.data.get("payment_method")
#         return_url = request.data.get("return_url")

#         if not payment_intent_id or not return_url or not payment_method:
#             return Response({"error": "Payment intent ID and return URL are required and payment_method"}, status=status.HTTP_400_BAD_REQUEST)

#         # PayMongo API request
#         url = f"https://api.paymongo.com/v1/payment_methods"
#         auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
#         headers = {
#             "Authorization": f"Basic {auth_key}",
#             "Content-Type": "application/json",
#         }

#         # Create payment method with GCash or card as type
#         data = {
#             "data": {
#                 "attributes": {
#                     "type": payment_method,
#                     "billing": {
#                         "email": request.data.get("email"),
#                         "name": request.data.get("name"),
#                     }
#                 }
#             }
#         }

#         response = requests.post(url, json=data, headers=headers)

#         if response.status_code == 200:
#             payment_method_id = response.json()['data']['id']

#             # Attach payment method to intent
#             attach_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}/attach"
#             attach_data = {
#                 "data": {
#                     "attributes": {
#                         "payment_method": payment_method_id,
#                         "return_url": return_url
#                     }
#                 }
#             }

#             attach_response = requests.post(attach_url, json=attach_data, headers=headers)

#             if attach_response.status_code == 200:
#                 response = attach_response.json()
#                 amount = response['data']['attributes']['amount']
#                 description = response['data']['attributes']['description']
#                 url = response['data']['attributes']['next_action']['redirect']['url']
#                 retrieve_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
#                 retrieve_response = requests.get(url=retrieve_url, headers=headers)
#                 print(retrieve_response.json())

#                 return Response({"amount":amount,"description":description, "url":url}, status=status.HTTP_200_OK)
#             else:
#                 return Response(attach_response.json(), status=attach_response.status_code)
#         else:
#             print(response.json())
#             return Response(response.json(), status=status.HTTP_200_OK)

# class FinalPaymentIntentView(APIView):
#       def post(self, request):
#         currency = request.data.get('currency','PHP')
#         booking_id = request.data.get('booking')
#         booking = get_object_or_404(Booking, id=booking_id)

#         booking_downpayment = Payment.objects.filter(
#             payment_type = 'downpayment',
#             booking=booking,
#             payment_status='paid',
#         ).first()

#         if booking.amount is not None and  booking_downpayment:
#             net_amount = booking_downpayment.net_amount or Decimal(0)
#             payment_amount = Decimal(booking.amount) - Decimal(net_amount)
#         else:
#             return Response({"error": "Booking amount or downpayment not found"}, status=status.HTTP_400_BAD_REQUEST)

#         url = 'https://api.paymongo.com/v1/payment_intents'
#         secret_key =settings.PAYMONGO_SECRET_KEY
#         auth_key = base64.b64encode(f'{secret_key}:'.encode('utf-8')).decode('utf-8')
#         headers = {
#             'Authorization':f'Basic {auth_key}',
#             'Content-Type':'application/json'
#         }

#         payload = {
#             'data':{
#                 'attributes':{
#                     'amount':int(payment_amount) * 100 , #convert to cents
#                     'payment_method_allowed':['gcash','paymaya'],
#                     'currency':currency,
#                     'description':f'Final booking payment for {booking.artist.user.first_name} {booking.artist.user.last_name}',
#                     'metadata':{
#                         'booking_id':str(booking.pk)
#                     }
#                 }
#             }
#         }

#         response = requests.post(url=url,json=payload,headers=headers)
#         if response.status_code == 200:
#             payment_intent_data = response.json()
#             payment_intent_id = payment_intent_data['data']['id']
#             return Response({"payment_intent_id":payment_intent_id},status=status.HTTP_200_OK)
#         return Response(status=status.HTTP_400_BAD_REQUEST)

# class AttachFinalPaymentMethodView(APIView):
#     def post(self, request):
#         booking_id = request.data.get("booking")
#         booking = get_object_or_404(Booking, id = booking_id)
#         payment_intent_id = request.data.get("payment_intent_id")
#         payment_method = request.data.get("payment_method")
#         return_url = request.data.get("return_url")

#         if not payment_intent_id or not return_url or not payment_method:
#             return Response({"error": "Payment intent ID and return URL are required and payment_method"}, status=status.HTTP_400_BAD_REQUEST)

#         # PayMongo API request
#         url = f"https://api.paymongo.com/v1/payment_methods"
#         auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
#         headers = {
#             "Authorization": f"Basic {auth_key}",
#             "Content-Type": "application/json",
#         }

#         # Create payment method with GCash or card as type
#         data = {
#             "data": {
#                 "attributes": {
#                     "type": payment_method,
#                     "billing": {
#                         "email": request.data.get("email"),
#                         "name": request.data.get("name"),
#                     }
#                 }
#             }
#         }

#         response = requests.post(url, json=data, headers=headers)

#         if response.status_code == 200:
#             payment_method_id = response.json()['data']['id']

#             # Attach payment method to intent
#             attach_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}/attach"
#             attach_data = {
#                 "data": {
#                     "attributes": {
#                         "payment_method": payment_method_id,
#                         "return_url": return_url
#                     }
#                 }
#             }

#             attach_response = requests.post(attach_url, json=attach_data, headers=headers)

#             if attach_response.status_code == 200:
#                 response = attach_response.json()
#                 amount = response['data']['attributes']['amount']
#                 description = response['data']['attributes']['description']
#                 url = response['data']['attributes']['next_action']['redirect']['url']
#                 retrieve_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
#                 retrieve_response = requests.get(url=retrieve_url, headers=headers)
#                 print(retrieve_response.json())

#                 #update booking status
#                 booking.downpayment_paid()

#                 return Response({"amount":amount,"description":description, "url":url}, status=status.HTTP_200_OK)
#             else:
#                 return Response(attach_response.json(), status=attach_response.status_code)
#         else:
#             print(response.json())
#             return Response(response.json(), status=status.HTTP_200_OK)

# class FinalPaymentStatusView(APIView):
#     def post(self, request):
#         payment_intent_id = request.data.get("payment_intent_id")
#         if not payment_intent_id:
#             return Response({'error': 'payment_intent_id is required'}, status=status.HTTP_400_BAD_REQUEST)

#         # PayMongo API request to retrieve the payment intent status
#         url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
#         auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
#         headers = {
#             "Authorization": f"Basic {auth_key}",
#             "Content-Type": "application/json",
#         }

#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             payment_intent = response.json()
#             booking_id = payment_intent['data']['attributes']['metadata']['booking_id']
#             booking = get_object_or_404(Booking, pk=booking_id)
#             intent_status = payment_intent['data']['attributes']['status']

#             # Check if a final payment already exists for the booking
#             existing_payment = Payment.objects.filter(
#                 payment_intent_id=payment_intent_id,
#                 booking=booking
#                 ).first()

#             if not existing_payment:
#                 # No existing payment, attempt to process the payment data if it exists
#                 payments = payment_intent['data']['attributes'].get('payments', [])

#                 if len(payments) > 0:
#                     # Process the first payment in the list
#                     payment_data = payments[0]['attributes']
#                     fee = payment_data['fee']
#                     net_amount = payment_data['net_amount']
#                     gross_amount = payment_data['amount']
#                     email = payment_data['billing']['email']
#                     name = payment_data['billing']['name']
#                     payment_method_type = payment_data['source']['type']

#                     # Convert amounts
#                     gateway_fee = Decimal(fee) / Decimal(100)
#                     net_amount = Decimal(net_amount) / Decimal(100)
#                     gross_amount = Decimal(gross_amount) / Decimal(100)

#                     # Create new payment instance
#                     payment = Payment.objects.create(
#                         payment_type='final_payment',
#                         payment_intent_id=payment_intent_id,
#                         booking=booking,
#                         client=booking.client,
#                         amount=gross_amount,
#                         net_amount=net_amount,
#                         service_fee=gateway_fee,
#                         payment_gateway=payment_method_type,
#                         payment_status='paid',
#                         payer_email=email,
#                         payer_name=name
#                     )
#                     #update booking status
#                     booking.complete()
#                     print("Payment object created successfully.")
#                 else:
#                     # No payments found in the payment intent
#                     print("No payments found for this payment intent.")
#             else:
#                 # Payment already exists, take no action
#                 print("Payment object already exists for this booking.")

#             # Return status based on the intent status
#             if intent_status == 'succeeded':
#                 send_payout(reference_id=booking.pk,booking=booking, channel_code="PH_BDO", artist=booking.artist, amount=123000, description="sodifjpasodf")
#                 return Response({"status": "success","booking_id": booking_id}, status=status.HTTP_200_OK)
#             elif intent_status == 'awaiting_payment_method':
#                 return Response({"status": "pending"}, status=status.HTTP_200_OK)
#             elif intent_status == 'awaiting_next_action':
#                 next_action = payment_intent['data']['attributes'].get('next_action')
#                 if next_action and next_action['type'] == 'redirect':
#                     redirect_url = next_action['redirect']['url']
#                     return_url = next_action['redirect']['return_url']
#                     return Response({
#                         "status": "pending_redirect",
#                         "redirect_url": redirect_url,
#                         "return_url": return_url
#                     }, status=status.HTTP_200_OK)
#                 return Response({"status": "pending_redirect"}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)

#         else:
#             return Response(response.json(), status=response.status_code)

class CreateInvoiceView(APIView):
    def post(self, request):
        booking_id = request.data.get('booking_id')
        payment_type = request.data.get('payment_type')
        valid_payment_type = is_valid_payment_type(payment_type)
        if not valid_payment_type:
             return Response({'message':'Not a valid payment type'},status=status.HTTP_400_BAD_REQUEST)
        if not booking_id or not payment_type:
            return Response({'message':'Missing booking_id and payment_type'},status=status.HTTP_400_BAD_REQUEST)
        booking = get_object_or_404(Booking, id=booking_id)

        if payment_type == 'downpayment':
            amount = booking.amount * Decimal(0.10)
        if payment_type == 'final_payment':
            downpayment = Payment.objects.filter(booking = booking, payment_type = 'downpayment').first()
            if not downpayment:
                return Response({'message':'No downpayment found'},status=status.HTTP_400_BAD_REQUEST)
            amount = booking.amount - downpayment.amount

        invoice_url = create_payment_invoice(
            reference_id=booking.booking_reference,
            amount= float(amount),
            customer_email=booking.client.email,
            payment_type=payment_type
            )

        if invoice_url is not None:
            return Response({"invoice_url": invoice_url}, status=status.HTTP_200_OK)
        return Response({'message':'ERROR creating invoice'},status=status.HTTP_400_BAD_REQUEST)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

@csrf_exempt
@require_POST
def invoice_webhook(request):
    try:
        # Parse the JSON payload
        data = json.loads(request.body)
        print("Webhook received:", data)

        # Extract relevant fields from the webhook data
        invoice_id = data.get("id")
        booking_reference = data.get("external_id")
        status = data.get("status")
        amount = data.get("amount")
        payer_email = data.get("payer_email")
        payment_method = data.get("payment_method")
        payment_channel = data.get("payment_channel")

        # Validate required fields
        if not all([invoice_id, booking_reference, status, amount]):
            print('invoice_id', invoice_id)
            print('booking_reference', booking_reference)
            print('status', status)
            print('amount', amount)
            print("Missing required fields in the webhook data")
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Retrieve the booking object, return 404 if not found
        try:
            booking = Booking.objects.get(booking_reference=booking_reference)
        except Booking.DoesNotExist:
            print(f"Booking not found for booking_reference: {booking_reference}")
            return JsonResponse({"error": "Booking not found"}, status=404)

        # Retrieve the invoice details from Xendit (make sure to handle this gracefully)
        invoice_details = get_invoice_details(invoice_id=invoice_id)
        if invoice_details is None:
            print(f"Invoice details not found for invoice_id: {invoice_id}")
            return JsonResponse({"error": "Invoice details not found"}, status=404)

        # Extract metadata if available
        metadata = invoice_details.get("metadata", {})
        if not metadata:
            print(f"No metadata found for invoice_id: {invoice_id}")

        # Process payment if the status is 'PAID' and metadata is present
        if status == "PAID" and metadata:
            payment_type = metadata.get('payment_type')
            if payment_type:
                # Create payment entry in the database
                payment = Payment.objects.create(
                    payment_status='paid',
                    booking=booking,
                    amount=amount,
                    net_amount=amount,
                    payment_method=payment_method,
                    payer_channel=payment_channel,
                    payer_email=payer_email,
                    payment_type=payment_type
                )
                payment.payment_reference  = f'PAY{payment.pk:06d}'
                payment.save()
                print(f"Payment recorded for booking_reference: {booking_reference}")

                #Send Dibursement if final payment
                if payment_type == 'final_payment':
                    payout_amount = booking.amount - (booking.amount * Decimal(0.05))
                    payout = send_payout(amount=payout_amount,booking_id=booking.pk, channel_code="PH_GCASH")#CHANGE
            else:
                print(f"Payment type not found in metadata for booking_reference: {booking_reference}")
        else:
            print(f"Payment not processed or invalid status for booking_reference: {booking_reference}")

        return JsonResponse({"status": "success"}, status=200)

    except json.JSONDecodeError:
        print("Invalid JSON in the webhook payload")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print("Unexpected error in webhook processing:", str(e))
        return JsonResponse({"error": "Server error"}, status=500)


@csrf_exempt
@require_POST
def payout_webhook(request):
    try:
        data = json.loads(request.body)
        pprint(data)
        status = data['data']['status']
        reference_id = data['data']['reference_id']
        payment_method = data['data']['channel_category']
        payment_channel = data['data']['channel_code']
        amount = data['data']['amount']
        print('status', status)
        if status == 'SUCCEEDED':
            if reference_id:
                try:
                    booking = Booking.objects.get(booking_reference=reference_id)
                except Exception as e:
                    print('ERROR',e)
                    return JsonResponse({'message':'Error'}, status=400)
            if booking is not None:
                payment = Payment.objects.create(
                            payment_status='paid',
                            booking=booking,
                            amount=amount,
                            net_amount=amount,
                            payment_method=payment_method,
                            payer_channel=payment_channel,
                            payment_type="payout"
                        )
                payment.payment_reference  = f'PAY{payment.pk:06d}'
                payment.save()
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({'message':'Error'}, status=400)
    except Exception as e:
        print('ERROR', e)
        return JsonResponse({'message':'Error'}, status=400)

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

# HTTP POST /api/payments/payout_webhook 200 [0.01, 127.0.0.1:55354]
# {'api_version': 'v2',
#  'business_id': '6722f50cb1f853a4bd388291',
#  'created': '2024-11-13T11:39:35.043Z',
#  'data': {'account_holder_name': 'Pops Fern',
#           'account_number': '12323434',
#           'amount': 7000,
#           'channel_category': 'EWALLET',
#           'channel_code': 'PH_PAYMAYA',
#           'connector_reference': 'SIMULATED_CONNECTOR_REFERENCE_1731497974543_310',
#           'created': '2024-11-13T11:39:32.971Z',
#           'currency': 'PHP',
#           'estimated_arrival_time': '2024-11-13T11:54:32.969Z',
#           'id': 'disb-30d7cb94-b788-4ed0-a26f-5495c89dbc8e',
#           'idempotency_key': '47-payout',
#           'reference_id': 'BKG000047',
#           'status': 'SUCCEEDED',
#           'updated': '2024-11-13T11:39:34.794Z'},
#  'event': 'payout.succeeded'}
