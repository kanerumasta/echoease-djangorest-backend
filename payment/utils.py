import xendit
from xendit.apis import BalanceApi
from pprint import pprint
from django.conf import settings
import time
from xendit.apis import PayoutApi
from xendit.payout.model.create_payout_request import CreatePayoutRequest
from xendit.payout.model.get_payouts200_response_data_inner import GetPayouts200ResponseDataInner
from xendit.payout.model.error import Error

xendit.set_api_key(settings.XENDIT_SECRET_KEY)

client = xendit.ApiClient()
api_instance = PayoutApi(client)

def send_payout(reference_id,booking, channel_code, artist, amount, description):
    idempotence_key = f'{booking.pk}-payout'
    create_payout_request = {
        "reference_id": str(reference_id),
        "channel_code":channel_code,
        "currency": "PHP",
        "channel_properties":{
            "account_holder_name":artist.account_holder_name,
            "account_number":artist.get_account_number(),
        },
        "amount":amount,
        "description":description
    }
    pprint(create_payout_request)
    try:
        api_response = api_instance.create_payout(idempotency_key=idempotence_key, create_payout_request=create_payout_request)
        pprint(api_response)
    except xendit.XenditSdkException as e:
        print('XenditSdkException: ',e)
