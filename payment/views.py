from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import create_paypal_order,capture_payment, create_paymongo_payment_link
from django.shortcuts import get_object_or_404
from booking.models import Booking
from django.http import Http404
from .models import Payment
from decimal import Decimal
from django.conf import settings
import base64
import requests

# class PaypalOrderView(APIView):
#     def post(self, request, *args, **kwargs):
#         print(request.data)
#         try:
#             amount=request.data['amount']
#             return_url = request.data['return_url']
#             cancel_url = request.data['cancel_url']
#             booking_id = request.data['booking_id']

#             booking = get_object_or_404(Booking, pk=booking_id)
#             if booking.is_completed:
#                 return Response({'message':'Booking already paid'}, status=status.HTTP_400_BAD_REQUEST)

#             if not booking.is_confirmed:
#                 return Response({'messsage':'Booking is not yet confirmed'}, status=status.HTTP_400_BAD_REQUEST)
#             order_result= create_paypal_order(booking_id=booking.pk,amount=amount, currency_code="USD",return_url=return_url,cancel_url=cancel_url)

#             if order_result.success:
#                 return Response({"success":True,"msg":"payment link has been successfully created","payer_action":str(order_result.payer_action_link)},status=status.HTTP_201_CREATED)
#             else:
#                 return Response({"success":False,"msg":"Authentication or payment failed"},status=status.HTTP_400_BAD_REQUEST)
#         except Http404:
#             return Response({'message':'Booking does not exist'}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             print(e)
#             print('ERROR: create payment order')
#             return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class PaypalCapturePaymentView(APIView):
#     def post(self, request):
#         order_id = request.data.get('order_id')

#         capture_result = capture_payment(order_id=order_id)
#         if capture_result.success:
#             reference_id  =capture_result.booking_id #reference id is booking id
#             if not reference_id:
#                 return Response({'message':'ERROR: booking reference id not found'}, status=status.HTTP_400_BAD_REQUEST)
#             booking = get_object_or_404(Booking, pk=reference_id)
#             booking.complete_booking()
#             payment = Payment.objects.create(
#                 reference_id =capture_result.capture_id,
#                 booking = booking,
#                 client = booking.client,
#                 amount = Decimal(capture_result.gross_amount or '0.00'),
#                 processing_fee = Decimal(capture_result.paypal_fee or '0.00'),
#                 payment_method = 'paypal'
#             )

#             return Response({"message":"captured payment"}, status=status.HTTP_200_OK)
#         print('ERROR: capture payment')
#         return Response({'message':'error capture downpayment'}, status=status.HTTP_400_BAD_REQUEST)

# class CreatePaymongoPaymentLinkView(APIView):
#     def post(self, request):
#         amount = request.data.get('amount')
#         booking_id = request.data.get('booking_id')
#         if not amount:
#             return Response({'error':'amount is required'})
#         if not booking_id:
#             return Response({'error':'booking id is required'})

#         success, data = create_paymongo_payment_link(amount=int(amount))
#         if success:
#             return Response({'checkout_link':data},status=status.HTTP_200_OK)
#         return Response(status=status.HTTP_400_BAD_REQUEST)

class CreatePaymentIntentView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        currency = request.data.get('currency','PHP')
        booking_id = request.data.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        url = 'https://api.paymongo.com/v1/payment_intents'
        secret_key =settings.PAYMONGO_SECRET_KEY
        auth_key = base64.b64encode(f'{secret_key}:'.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization':f'Basic {auth_key}',
            'Content-Type':'application/json'
        }

        payload = {
            'data':{
                'attributes':{
                    'amount':amount,
                    'payment_method_allowed':['card','gcash'],
                    'currency':currency,
                    'description':f'Payment for booking {booking_id}'
                }
            }
        }

        response = requests.post(url=url,json=payload,headers=headers)

        if response.status_code == 200:
            payment_intent_data = response.json()
            payment_intent_id = payment_intent_data['data']['id']

class PaymentView(APIView):
    pass
