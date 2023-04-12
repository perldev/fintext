from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
import requests
from fintex.common import json_true, json_500false
import traceback

from .models import rate, Orders, CashPointLocation

from datetime import datetime
from datetime import timedelta
import json 


def main(req):
    return render(req, "main.html", {})


# TODO  protect this from spam
def get_rate(req, currency_from, currency_to):
    try:
        current_time = datetime.now()
        expire_time = current_time + timedelta(minutes=15)
        currency_pair = currency_from.lower() + '_' + currency_to.lower()
        res = requests.get("https://btc-trade.com.ua/api/ticker/%s_%s" % (currency_from.lower(), currency_to.lower()), )
        if res.status_code != 200:
            raise Exception("not avaliable")

        resj = res.json()
        return json_true(req, {"result": {"rate": resj[currency_pair]["sell"], "expire": expire_time}})
    except:
        traceback.print_exc()
        return json_500false(req, {"description": "not avaliable"})
    

def get_currency_list(req):
    availiable_currencies = {
        'btc': 'Bitcoin',
        'usdt': 'Usdt',
        'eth': 'Etherium',
        'uah': 'UAH'
        }
    return json_true(req, {'currencies': availiable_currencies})


def create_exchange_request(req):
    if req.method == 'POST':
        body_unicode = req.body.decode('utf-8')
        body = json.loads(body_unicode)
        given_cur = body['given_cur']
        taken_cur = body['taken_cur']
        amount = int(float(body['amount']))
        rate = int(float(body['rate']))
        taken_amount = amount * rate
        t_link = 'https://t.me/books_extended/121'
        cashPoints = CashPointLocation.objects.all()
        cashPointsDict = {}
        for i in cashPoints:
            cashPointsDict[i.id] = i.title
        respone_data = {
            'given_cur': given_cur,
            'taken_cur': taken_cur,
            'amount': amount,
            'taken_amount': taken_amount,
            't_link': t_link,
            'cash_points': cashPointsDict,
        }
        return json_true(req, {'response': respone_data})
    else:
        return json_true(req, {'message': 'nothing to return'})
    
