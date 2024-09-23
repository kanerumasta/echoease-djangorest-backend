import time
import requests
import json
from os import getenv
from pydantic import BaseModel, ValidationError
from typing import Optional
import base64


class PaypalAccessTokenResult(BaseModel):
    data:Optional[str]
    error : Optional[str]

class PaypalEndpoints(BaseModel):
    client_id:str
    secret : str
    base_url : str

class Result (BaseModel):
    success : bool
    error : Optional[str] = None
    data:Optional[str] = None

class AuthorizationData(BaseModel):
    authorization_id : str 
    amount : str
class AuthorizationResult(BaseModel):
    success:bool
    error:Optional["str"] = None
    data : Optional[AuthorizationData] = None

class PaypalPaymentResult(BaseModel):
    success : bool
    payment_id:Optional[str] = None
    approval_url :Optional[str] = None
    error : Optional[str] = None

class CreateOrderResult(BaseModel):
    success:bool
    order_id:Optional[str] = None
    error:Optional[str] = None
    payer_action_link : Optional[str] = None

class CapturePaymentResult (BaseModel):
    capture_id : Optional[str] = None
    success:bool
    booking_id: Optional[str] = None
    gross_amount : Optional[str] = None
    net_amount : Optional[str] = None
    paypal_fee:Optional[str] = None





def get_paypal_endpoints() -> PaypalEndpoints:
    client_id = getenv('PAYPAL_CLIENT_ID')
    secret = getenv('PAYPAL_SECRET')
    base_url = getenv('PAYPAL_BASE_URL')

    return PaypalEndpoints(client_id=client_id, secret=secret, base_url=base_url) # type: ignore
    



def get_access_token()->PaypalAccessTokenResult:
    paypal_endpoints = get_paypal_endpoints()

    if not all([paypal_endpoints.client_id, paypal_endpoints.secret, paypal_endpoints.base_url]):
        raise ValueError("Missing Paypal Endpoints (client_id,secret, base_url)")

    token_url = f'{paypal_endpoints.base_url}/v1/oauth2/token'
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    
    token_response = requests.post(token_url, auth=(paypal_endpoints.client_id, paypal_endpoints.secret), data=token_payload, headers=token_headers)
    
    if token_response.status_code != 200:
        return PaypalAccessTokenResult(data=None, error="Failed to Authenticate with paypal API")
    access_token = token_response.json().get('access_token')
    return PaypalAccessTokenResult(data=access_token, error = None)




def create_paypal_order(booking_id,amount, currency_code, return_url, cancel_url)->CreateOrderResult:

    endpoints= get_paypal_endpoints()
    token_result = get_access_token()

    if not token_result.data:
        return CreateOrderResult(success=False, error=token_result.error)
    
    

    order_payload ={ 
        "intent": "CAPTURE",
        "purchase_units": [
            {
            "reference_id":booking_id,
            "amount": {
                "currency_code": currency_code,
                "value": str(amount)
            }
            }
        ],
        "payment_source": {
            "paypal": {
            "experience_context": {
                "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                "brand_name": "Echoease",
                "locale": "en-US",
                "landing_page": "LOGIN",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url
            }
            }
        }
    }
    
    order_url = f'{endpoints.base_url}/v2/checkout/orders'
    order_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token_result.data}'
    }

    # Create payment request
    order_response = requests.post(order_url, data=json.dumps(order_payload), headers=order_headers)
  
    if order_response.status_code != 200:
        return CreateOrderResult(success=False, error='Failed to create PayPal payment.', order_id=None)

    order_id = order_response.json().get('id')

    payer_action_link = next(link['href'] for link in order_response.json()['links'] if link['rel'] == 'payer-action')
    return CreateOrderResult(success=True, order_id=order_id, error=str(order_response.status_code), payer_action_link=payer_action_link)

def capture_payment(order_id):
    
    token =get_access_token()
    paypal_endpoints = get_paypal_endpoints()
    base_url = paypal_endpoints.base_url

    if not token.data:
        return CapturePaymentResult(success=False)
    if not base_url:
        return CapturePaymentResult(success=False)

    #capture
    capture_url = f'{base_url}/v2/checkout/orders/{order_id}/capture'
    capture_headers = {
        'Content-Type':'application/json',
        'Authorization':f'Bearer {token.data}'
    }   

    capture_response = requests.post(url=capture_url, headers=capture_headers)

    if capture_response.status_code != 201:
        return CapturePaymentResult(success=False)

    capture = capture_response.json()['purchase_units'][0]['payments']['captures'][0]
    capture_id = capture['id']
    capture_amount = capture['amount']['value']
    net_amount = capture['seller_receivable_breakdown']['net_amount']['value']
    paypal_fee = capture['seller_receivable_breakdown']['paypal_fee']['value']

    print('capture id', capture_id)
    print('amount', capture_amount)

    print('net', net_amount)
    print('fee', paypal_fee)

    booking_reference_id = capture_response.json()['purchase_units'][0]['reference_id']

    return CapturePaymentResult(success=True,booking_id=booking_reference_id, paypal_fee=paypal_fee, capture_id=capture_id,net_amount=net_amount,gross_amount=capture_amount)


def get_base64_key(secret_key):
    key_with_colon = f'{secret_key}:'
    return base64.b64encode(key_with_colon.encode()).decode()


def create_paymongo_payment_link(amount):
    url = "https://api.paymongo.com/v1/links"

    auth_key = get_base64_key("sk_test_1X9wP8JRD8Dhoc5GZga1m2gj") #ENV THIS

    headers = {'accept':'application/json','content-type':'application/json', 'authorization':f'Basic {auth_key}'}
    payload = { "data": { "attributes": {
            "amount": amount * 100,
            "description": "sdoifu",
            "remarks": "34"
        } } }
    res = requests.post(url=url, json=payload, headers=headers)
    return True,res.json()['data']['attributes']['checkout_url']
