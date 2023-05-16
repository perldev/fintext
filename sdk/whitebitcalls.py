import base64
import hashlib
import hmac
import json
import time
import requests
from private_settings import WHITEBIT_API_KEY, WHITEBIT_SECRET_KEY


def get_address_call(currency):
    request = '/api/v4/main-account/address'
    nonce = time.time_ns()

    data = {
        "ticker": currency,
        "request": request,
        "nonce": nonce,
        'nonceWindow': False
    }

    completeUrl = 'https://whitebit.com/api/v4/main-account/address'

    data_json = json.dumps(data, separators=(',', ':'))
    payload = base64.b64encode(data_json.encode('ascii'))
    signature = hmac.new(WHITEBIT_SECRET_KEY.encode('ascii'), payload, hashlib.sha512).hexdigest()

    headers = {
        'Content-type': 'application/json',
        'X-TXC-APIKEY': WHITEBIT_API_KEY,
        'X-TXC-PAYLOAD': payload,
        'X-TXC-SIGNATURE': signature,
    }

    resp = requests.post(completeUrl, headers=headers, data=data_json)
    return resp