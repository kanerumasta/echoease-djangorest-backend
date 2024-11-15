from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import create_paypal_order,capture_payment, create_paymongo_payment_link
from django.shortcuts import get_object_or_404
from booking.models import Booking
from django.http import Http404
from payment.models import DownPayment, Payment, Payout
from decimal import Decimal, InvalidOperation
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



class DownPaymentStatusView(APIView):
    def post(self, request):
        payment_intent_id = request.data.get("payment_intent_id")
        if not payment_intent_id:
            return Response({'error':'payment_intent_id is required'},status=status.HTTP_400_BAD_REQUEST)

        # PayMongo API request to retrieve the payment intent status
        url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
        auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {auth_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            payment_intent = response.json()
            intent_status = payment_intent['data']['attributes']['status']
            print(payment_intent)
           # Check if a downpayment already exists for the booking

            # Getting booking id reference
            booking_id = payment_intent['data']['attributes']['metadata']['booking_id']
            booking = get_object_or_404(Booking, id= booking_id)

            existing_downpayment = booking.down_payment.filter(payment_intent_id=payment_intent['data']['id']).first()
            if not existing_downpayment:
            # No existing downpayment, create a new one
                payment_data = payment_intent['data']['attributes']['payments'][0]['attributes']
                fee = payment_data['fee']
                net_amount = payment_data['net_amount']
                gross_amount = payment_data['amount']
                email = payment_data['billing']['email']
                name = payment_data['billing']['name']
                payment_status = payment_data['status']
                payment_method_type = payment_data['source']['type']

                # Convert amounts
                gateway_fee = Decimal(fee) / Decimal(100)
                net_amount = Decimal(net_amount)/ Decimal(100)
                gross_amount = Decimal(gross_amount) / Decimal(100)

                # Create new downpayment instance
                downpayment = DownPayment.objects.create(
                    booking=booking,
                    payment_intent_id=payment_intent['data']['id'],
                    amount=gross_amount,
                    processing_fee=gateway_fee,
                    net_amount=net_amount,
                    payment_status='paid',
                    payment_method=payment_method_type,
                    payer_email=email,
                    payer_name=name,

                )
                print("Downpayment created successfully.")
            else:
                # Downpayment already exists, take no action
                print("Downpayment already exists for this booking.")
            if intent_status == 'succeeded':
                return Response({"status": "success", "booking_id":booking.id}, status=status.HTTP_200_OK)
            elif intent_status == 'awaiting_payment_method':
                return Response({"status": "pending"}, status=status.HTTP_200_OK)
            elif intent_status == 'awaiting_next_action':
                return Response({"status": "pending_redirect"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(response.json(), status=response.status_code)

class CreateDownPaymentIntentView(APIView):
    def post(self, request):
        currency = request.data.get('currency', 'PHP')
        booking_id = request.data.get('booking')
        booking = get_object_or_404(Booking, id=booking_id)

        # Calculate downpayment amount (20% of the rate)
        downpayment_amount = (Decimal(booking.rate.amount) * Decimal(0.20)).quantize(Decimal('0.01'))

        # Log downpayment amount for debugging
        print('Downpayment Amount:', downpayment_amount)

        # Convert downpayment to integer cents
        amount_in_cents = int(downpayment_amount * 100)
        print('Amount in Cents:', amount_in_cents)

        # Prepare PayMongo API request
        url = 'https://api.paymongo.com/v1/payment_intents'
        secret_key = settings.PAYMONGO_SECRET_KEY
        auth_key = base64.b64encode(f'{secret_key}:'.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'data': {
                'attributes': {
                    'amount': amount_in_cents,
                    'payment_method_allowed': ['gcash', 'paymaya'],
                    'currency': currency,
                    'description': f'Booking down payment for {booking.artist.user.first_name} {booking.artist.user.last_name}',
                    'metadata': {
                        'booking_id':str(booking.id)
                    }
                }
            }
        }

        # Make the API request to PayMongo
        response = requests.post(url=url, json=payload, headers=headers)

        # Check the response status and handle accordingly
        if response.status_code == 200:
            payment_intent_data = response.json()
            payment_intent_id = payment_intent_data['data']['id']
            return Response({"payment_intent_id": payment_intent_id}, status=status.HTTP_200_OK)

        # Handle errors from PayMongo
        return Response(response.json(), status=response.status_code)


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
                amount = response['data']['attributes']['amount']
                description = response['data']['attributes']['description']
                url = response['data']['attributes']['next_action']['redirect']['url']
                retrieve_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
                retrieve_response = requests.get(url=retrieve_url, headers=headers)
                print(retrieve_response.json())

                #update booking status
                booking.downpayment_paid()

                return Response({"amount":amount,"description":description, "url":url}, status=status.HTTP_200_OK)
            else:
                return Response(attach_response.json(), status=attach_response.status_code)
        else:
            print(response.json())
            return Response(response.json(), status=status.HTTP_200_OK)

class FinalPaymentIntentView(APIView):
      def post(self, request):
        currency = request.data.get('currency','PHP')
        booking_id = request.data.get('booking')
        booking = get_object_or_404(Booking, id=booking_id)
        booking_downpayment = booking.down_payment.filter(booking = booking).first()
        payment_amount = Decimal(booking.rate.amount) - booking_downpayment.net_amount

        print(int(payment_amount) * 100)

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
                    'amount':int(payment_amount) * 100,
                    'payment_method_allowed':['gcash','paymaya'],
                    'currency':currency,
                    'description':f'Final booking payment for {booking.artist.user.first_name} {booking.artist.user.last_name}'
                }
            }
        }

        response = requests.post(url=url,json=payload,headers=headers)
        if response.status_code == 200:
            payment_intent_data = response.json()
            payment_intent_id = payment_intent_data['data']['id']
            return Response({"payment_intent_id":payment_intent_id},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class AttachFinalPaymentMethodView(APIView):
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
                amount = response['data']['attributes']['amount']
                description = response['data']['attributes']['description']
                url = response['data']['attributes']['next_action']['redirect']['url']
                retrieve_url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
                retrieve_response = requests.get(url=retrieve_url, headers=headers)
                print(retrieve_response.json())

                #update booking status
                booking.downpayment_paid()

                return Response({"amount":amount,"description":description, "url":url}, status=status.HTTP_200_OK)
            else:
                return Response(attach_response.json(), status=attach_response.status_code)
        else:
            print(response.json())
            return Response(response.json(), status=status.HTTP_200_OK)


class FinalPaymentStatusView(APIView):
    def post(self, request):
        payment_intent_id = request.data.get("payment_intent_id")
        booking_id = request.data.get("booking")
        booking = get_object_or_404(Booking, id=booking_id)

        if not payment_intent_id:
            return Response({'error': 'payment_intent_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # PayMongo API request to retrieve the payment intent status
        url = f"https://api.paymongo.com/v1/payment_intents/{payment_intent_id}"
        auth_key = base64.b64encode(f'{settings.PAYMONGO_SECRET_KEY}:'.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {auth_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            payment_intent = response.json()
            intent_status = payment_intent['data']['attributes']['status']

            # Check if a final payment already exists for the booking
            existing_payment = booking.payment.filter(payment_intent_id=payment_intent['data']['id']).first()

            if not existing_payment:
                # No existing payment, attempt to process the payment data if it exists
                payments = payment_intent['data']['attributes'].get('payments', [])

                if len(payments) > 0:
                    # Process the first payment in the list
                    payment_data = payments[0]['attributes']
                    fee = payment_data['fee']
                    net_amount = payment_data['net_amount']
                    gross_amount = payment_data['amount']
                    email = payment_data['billing']['email']
                    name = payment_data['billing']['name']
                    payment_status = payment_data['status']
                    payment_method_type = payment_data['source']['type']

                    # Convert amounts
                    gateway_fee = Decimal(fee) / Decimal(100)
                    net_amount = Decimal(net_amount) / Decimal(100)
                    gross_amount = Decimal(gross_amount) / Decimal(100)

                    # Create new payment instance
                    payment_obj = Payment.objects.create(
                        payment_intent_id=payment_intent_id,
                        booking=booking,
                        client=booking.client,
                        gross_amount=gross_amount,
                        net_amount=net_amount,
                        processing_fee=gateway_fee,
                        payment_method=payment_method_type,
                        payment_status=payment_status,
                        payer_email=email,
                        payer_name=name
                    )
                    #update booking status
                    booking.complete()
                    print("Payment object created successfully.")
                else:
                    # No payments found in the payment intent
                    print("No payments found for this payment intent.")
            else:
                # Payment already exists, take no action
                print("Payment object already exists for this booking.")

            # Return status based on the intent status
            if intent_status == 'succeeded':
                return Response({"status": "success"}, status=status.HTTP_200_OK)
            elif intent_status == 'awaiting_payment_method':
                return Response({"status": "pending"}, status=status.HTTP_200_OK)
            elif intent_status == 'awaiting_next_action':
                next_action = payment_intent['data']['attributes'].get('next_action')
                if next_action and next_action['type'] == 'redirect':
                    redirect_url = next_action['redirect']['url']
                    return_url = next_action['redirect']['return_url']
                    return Response({
                        "status": "pending_redirect",
                        "redirect_url": redirect_url,
                        "return_url": return_url
                    }, status=status.HTTP_200_OK)
                return Response({"status": "pending_redirect"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(response.json(), status=response.status_code)
