from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import create_paypal_order,capture_payment, create_paymongo_payment_link
from django.shortcuts import get_object_or_404
from booking.models import Booking
from django.http import Http404
from .models import Payment,DownPayment
from decimal import Decimal, InvalidOperation
from django.conf import settings
import base64
import requests
from .serializers import DownpaymentSerializer


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

class CreateDownPaymentIntentView(APIView):
    def post(self, request):
        currency = request.data.get('currency','PHP')
        booking_id = request.data.get('booking')
        booking = get_object_or_404(Booking, id=booking_id)
        downpayment_amount = float(booking.rate.amount) * float(0.20)
        print('Downpayment Amount', downpayment_amount)

        print(int(downpayment_amount) * 100)

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
                    'amount':int(downpayment_amount) * 100,
                    'payment_method_allowed':['gcash','card'],
                    'currency':currency,
                    'description':f'Down Payment for booking {booking_id}'
                }
            }
        }

        response = requests.post(url=url,json=payload,headers=headers)
        if response.status_code == 200:
            payment_intent_data = response.json()
            payment_intent_id = payment_intent_data['data']['id']
            return Response({"payment_intent_id":payment_intent_id},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class AttachPaymentMethodView(APIView):
    def post(self, request):
        booking_id = request.data.get("booking")
        booking = get_object_or_404(Booking, id = booking_id)
        payment_intent_id = request.data.get("payment_intent_id")
        payment_method = request.data.get("payment_method")
        return_url = request.data.get("return_url")

        if not payment_intent_id or not return_url or not payment_method:
            return Response({"error": "Payment intent ID and return URL are required and payment_method"}, status=status.HTTP_400_BAD_REQUEST)

        # PayMongo API request
        url = f"https://api.paymongo.com/v1/payment_methods"
        auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {auth_key}",
            "Content-Type": "application/json",
        }

        # Create payment method with GCash or card as type
        data = {
            "data": {
                "attributes": {
                    "type": payment_method,
                    "billing": {
                        "email": request.data.get("email"),
                        "name": request.data.get("name"),
                    }
                }
            }
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            payment_method_id = response.json()['data']['id']

            # Attach payment method to intent
            attach_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}/attach"
            attach_data = {
                "data": {
                    "attributes": {
                        "payment_method": payment_method_id,
                        "return_url": return_url
                    }
                }
            }

            attach_response = requests.post(attach_url, json=attach_data, headers=headers)

            if attach_response.status_code == 200:
                response = attach_response.json()
                print(response)
                amount = response['data']['attributes']['amount']
                description = response['data']['attributes']['description']
                url = response['data']['attributes']['next_action']['redirect']['url']

                #update booking status
                booking.downpayment_paid()

                return Response({"amount":amount,"description":description, "url":url}, status=status.HTTP_200_OK)
            else:
                return Response(attach_response.json(), status=attach_response.status_code)
        else:
            print(response.json())
            return Response(response.json(), status=response.status_code)

class PaymentView(APIView):
    pass


class DownPaymentView(APIView):
    def post(self, request):
        serializer = DownpaymentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Downpayment recorded successfully."}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
