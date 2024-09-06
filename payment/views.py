from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import make_paypal_payment, verify_paypal_payment, execute_paypal_payment


class PaypalPaymentView(APIView):
    """
    endpoint for create payment url
    """
    def post(self, request, *args, **kwargs):
        amount=40 # 20$ for example
        status,payment_id,approved_url=make_paypal_payment(amount=amount,currency="USD",return_url="http://localhost:3000/payment/success/",cancel_url="http://localhost:3000/payment")
        if status:
            # handel_subscribtion_paypal(plan=plan,user_id=request.user,payment_id=payment_id)
            print(payment_id)
            print('good')
            return Response({"success":True,"msg":"payment link has been successfully created","approved_url":approved_url},status=201)
        else:
            return Response({"success":False,"msg":"Authentication or payment failed"},status=400)
        
class PaypalValidatePaymentView(APIView):
    """
    endpoint for validate payment 
    """
    def post(self, request, *args, **kwargs):
        print(request.data.get('payment_id'))
        payment_id=request.data.get("payment_id")
        payer_id = request.data.get("payer_id")
        payment_status=execute_paypal_payment(payment_id=payment_id, payer_id=payer_id)
        print(payment_status)
        if payment_status:
            # your business logic 
             
            return Response({"success":True,"msg":"payment improved"},status=200)
        else:
            return Response({"success":False,"msg":"payment failed or cancelled"},status=200)
