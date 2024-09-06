import time
import requests
import json
from os import getenv

def make_paypal_payment(amount, currency, return_url, cancel_url):
    # Set up PayPal API credentials
    client_id = getenv("PAYPAL_CLIENT_ID")
    secret = getenv("PAYPAL_SECRET")
    url =getenv("PAYPAL_BASE_URL")
    # Set up API endpoints
    base_url = url
    token_url = base_url + '/v1/oauth2/token'
    payment_url = base_url + '/v1/payments/payment'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)
    if token_response.status_code != 200:
        return False,"Failed to authenticate with PayPal API",None

    access_token = token_response.json()['access_token']
    # Create payment payload
    payment_payload = {
        'intent': 'sale',
        'payer': {'payment_method': 'paypal'},
        'transactions': [{
            'amount': {'total': str(amount), 'currency': currency},
            # 'description': 'Echoease Pay',
            
        }],
        'redirect_urls': {
            'return_url': return_url,
            'cancel_url': cancel_url
        },
        'application_context':{
            
            'shipping_preference': 'NO_SHIPPING',
        }
    }

    # Create payment request
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_response = requests.post(payment_url, data=json.dumps(payment_payload), headers=payment_headers)
    if payment_response.status_code != 201:
        return False , 'Failed to create PayPal payment.',None

    payment_id = payment_response.json()['id']
    approval_url = next(link['href'] for link in payment_response.json()['links'] if link['rel'] == 'approval_url')

    return True,payment_id, approval_url
   

def execute_paypal_payment(payment_id, payer_id):
    # Set up PayPal API credentials
    client_id = getenv("PAYPAL_CLIENT_ID")
    secret = getenv("PAYPAL_SECRET")
    url = getenv("PAYPAL_BASE_URL")

    # Set up API endpoints
    execute_url = f'{url}/v1/payments/payment/{payment_id}/execute'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(
        f'{url}/v1/oauth2/token',
        auth=(client_id, secret),
        data=token_payload,
        headers=token_headers
    )

    if token_response.status_code != 200:
        raise Exception('Failed to authenticate with PayPal API.')

    access_token = token_response.json()['access_token']

    # Execute the payment
    execute_payload = {'payer_id': payer_id}
    execute_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    execute_response = requests.post(execute_url, json=execute_payload, headers=execute_headers)

    if execute_response.status_code == 200:
        return True
    else:
        return False

def send_paypal_payout(amount, recipient_email, currency="USD", note="Payout note"):
    # Set up PayPal API credentials
    client_id = getenv("PAYPAL_CLIENT_ID")
    secret = getenv("PAYPAL_SECRET")
    base_url = getenv("PAYPAL_BASE_URL")

    # Get an access token
    token_url = f"{base_url}/v1/oauth2/token"
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)
    if token_response.status_code != 200:
        return False, "Failed to authenticate with PayPal API"

    access_token = token_response.json()['access_token']

    # Create Payouts payload
    payout_payload = {
        "sender_batch_header": {
            "sender_batch_id": "batch_" + str(int(time.time())),  # Unique batch ID
            "email_subject": "You have a payout!",
            "email_message": "You have received a payout from Echoease!"
        },
        "items": [{
            "recipient_type": "EMAIL",
            "amount": {
                "value": str(amount),
                "currency": currency
            },
            "receiver": recipient_email,
            "note": note,
            "sender_item_id": "item_1"  # Unique item ID
        }]
    }

    payout_url = f"{base_url}/v1/payments/payouts"
    payout_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Send the payout request
    payout_response = requests.post(payout_url, data=json.dumps(payout_payload), headers=payout_headers)

    if payout_response.status_code != 201:
        return False, payout_response.json()

    return True, payout_response.json()

