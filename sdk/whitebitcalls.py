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


def check_balance(currency):
    request = '/api/v4/main-account/balance'
    nonce = time.time_ns()

    data = {
        "ticker": currency,
        "request": request,
        "nonce": nonce,
        'nonceWindow': False
    }

    completeUrl = 'https://whitebit.com/api/v4/main-account/balance'

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

#'/api/v4/trade-account/balance'
#/api/v4/main-account/transfer
#/api/v4/main-account/history


def deposit_history(currency):

    request = '/api/v4/main-account/history'
    nonce = time.time_ns()
    data = {
        "transactionMethod":1,
        "ticker": currency,
        "status": [3, 7],
        "request": request,
        "nonce": nonce
    }

    completeUrl = 'https://whitebit.com/api/v4/main-account/history'
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



def transfer_balance(currency, amnt):
    request = '/api/v4/main-account/transfer'
    nonce = time.time_ns()
    data = {
        "ticker": currency,
        "amount": amnt,
        "method": "deposit",
        "request": request,
        "nonce": nonce
    }



    completeUrl = 'https://whitebit.com/api/v4/main-account/transfer'
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

def check_balance_trade(currency):
    request = '/api/v4/trade-account/balance'
    nonce = time.time_ns()

    data = {
        "ticker": currency,
        "request": request,
        "nonce": nonce,
        #'nonceWindow': False
    }

    completeUrl = 'https://whitebit.com%s' % request

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

def  to_trade_account(amnt, currency, uniqueOrderId):
    pass

def sell_currency(market, amnt, uniqueOrderId):
    request = '/api/v4/order/market'
    nonce = time.time_ns()

    data = {
        "market": market,
        "side": "sell",
        "amount": amnt,
        "clientOrderId": uniqueOrderId,
        "request": request,
        "nonce": nonce,
        'nonceWindow': False
    }
    print(data)
    completeUrl = 'https://whitebit.com/api/v4/order/market'

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


def check_order(uniqueOrderId):
    request = '/api/v4/trade-account/order/history'
    nonce = time.time_ns()

    data = {
        "offset": 0,
        "limit": 100,    
        "clientOrderId": uniqueOrderId,
        "request": request,
        "nonce": nonce,
        'nonceWindow': False
    }

    completeUrl = 'https://whitebit.com/api/v4/trade-account/order/history'

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
