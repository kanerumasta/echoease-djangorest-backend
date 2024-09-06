from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import make_paypal_payment,execute_paypal_payment, send_paypal_payout


class PaypalPaymentView(APIView):
    """
    endpoint for create payment url
    """
    def post(self, request, *args, **kwargs):
        try:
            amount=request.data['amount']
            return_url = request.data['return_url']
            cancel_url = request.data['cancel_url']
            payment_status,payment_id,approved_url=make_paypal_payment(amount=amount,currency="USD",return_url=return_url,cancel_url=cancel_url)
            if payment_status:
                # handel_subscribtion_paypal(plan=plan,user_id=request.user,payment_id=payment_id)
                
                return Response({"success":True,"msg":"payment link has been successfully created","approved_url":approved_url},status=status.HTTP_201_CREATED)
            else:
                return Response({"success":False,"msg":"Authentication or payment failed"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
class PaypalValidatePaymentView(APIView):
    """
    endpoint for validate payment 
    """
    def post(self, request, *args, **kwargs):
        payment_id=request.data.get("payment_id")
        payer_id = request.data.get("payer_id")
        print(request.data)
        print(payment_id)
        print(payer_id)
        payment_status=execute_paypal_payment(payment_id=payment_id, payer_id=payer_id)
        if payment_status:
            # your business logic 
             
            return Response({"success":True,"msg":"payment improved"},status=200)
        else:
            return Response({"success":False,"msg":"payment failed or cancelled"},status=status.HTTP_400_BAD_REQUEST)
        
class PayPalPayoutView(APIView):
    def post(self, request, *args, **kwargs):
        # Get recipient details from request
        recipient_email = request.data.get("recipient_email")
        amount = request.data.get("amount")
        
        if not recipient_email or not amount:
            return Response({"success": False, "msg": "Recipient email and amount are required."}, status=400)
        
        success, result = send_paypal_payout(amount=amount, recipient_email=recipient_email)
        
        if success:
            return Response({"success": True, "msg": "Payout sent successfully", "data": result}, status=200)
        else:
            return Response({"success": False, "msg": "Payout failed", "error": result}, status=400)