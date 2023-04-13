from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
import requests
from fintex.common import json_true, json_500false, to_time
import traceback

from .models import rate, Orders, CashPointLocation

from datetime import datetime, timedelta as dt
from datetime import timedelta
import json 

from .models import Orders, CurrencyProvider, Currency, rate


def main(req):
    return render(req, "main.html", {})


#TODO add permissions only for opers
def stock_24_hour_rate_history(req, chanel, ticker):
    [currency1, currency2] = ticker.split("_")
    give_currency = Currency.objects.get(title=currency1)
    take_currency = Currency.objects.get(title=currency2)
    from_date = datetime.now() - dt(hours=24)
    res = []
    for i in rate.objects.filter(source=chanel,
                                 give_currency=give_currency,
                                 take_currency=take_currency,
                                 pub_date__gte=from_date):
        res.append({"name": to_time(i.pub_date),
                    "value": i.rate})

    return json_true(req, {"result": res})


# TODO  protect this from spam
def get_rate(req, currency_from, currency_to):
    try:
        current_time = datetime.now()
        expire_time = current_time + timedelta(minutes=15)
        req.session['expire_deal_time'] = datetime.timestamp(expire_time)
        
        currency_pair = currency_from.lower() + '_' + currency_to.lower()
        #TODO get this value from custom formula function
        res = requests.get("https://btc-trade.com.ua/api/ticker/%s_%s" % (currency_from.lower(), currency_to.lower()), )
        if res.status_code != 200:
            raise Exception("not avaliable")

        resj = res.json()
        req.session['exchange_rate'] = resj[currency_pair]["sell"]
        return json_true(req, {"result": {"rate": resj[currency_pair]["sell"]}})
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
        rate = float(body['rate'])
        amount = float(body['amount'])
        t_link = 'https://t.me/books_extended/121'
        cashPoints = CashPointLocation.objects.all()
        cashPointsDict = {}
        for i in cashPoints:
            cashPointsDict[i.id] = i.title

        if 'expire_deal_time' in req.session:
            expire_deal_time = req.session['expire_deal_time']
            current_time = datetime.now()
            if datetime.timestamp(current_time) > expire_deal_time:
                new_rate_request = get_rate(req, given_cur, taken_cur)
                data = json.loads(new_rate_request.content.decode('utf-8'))
                new_rate = float(data['result']['rate'])
                if new_rate == rate:
                    taken_amount = amount * rate
                    respone_data = {
                        'given_cur': given_cur,
                        'taken_cur': taken_cur,
                        'amount': amount,
                        'taken_amount': taken_amount,
                        't_link': t_link,
                        'cash_points': cashPointsDict,
                        'message_to_user': 'You exchange request is created'
                    }
                    if (given_cur != 'uah'):
                        provider_give = CurrencyProvider.objects.get(id=1)
                        provider_take = CurrencyProvider.objects.get(id=2)
                    else:
                        provider_give = CurrencyProvider.objects.get(id=2)
                        provider_take = CurrencyProvider.objects.get(id=1)
                    
                    # give_currency and take_currency are NOW HARDCODED
                    Orders.objects.create(amnt_give=amount, amnt_take=taken_amount,
                                          rate=rate,
                                          provider_give=provider_give,
                                          provider_take=provider_take,
                                          give_currency_id=1,
                                          take_currency_id=2)
                    return json_true(req, {'response': respone_data})
                else:
                    respone_data = {
                        'is_expired': 'true',
                        'message_to_user': 'Time of your request is expired. Try one more time please.'
                    }
                    return json_true(req, {'response': respone_data})  
            else:
                taken_amount = amount * rate
                respone_data = {
                    'given_cur': given_cur,
                    'taken_cur': taken_cur,
                    'amount': amount,
                    'taken_amount': taken_amount,
                    't_link': t_link,
                    'cash_points': cashPointsDict,
                    'message_to_user': 'You exchange request is created'
                }
                if (given_cur != 'uah'):
                    provider_give = CurrencyProvider.objects.get(id=1)
                    provider_take = CurrencyProvider.objects.get(id=2)
                else:
                    provider_give = CurrencyProvider.objects.get(id=2)
                    provider_take = CurrencyProvider.objects.get(id=1)
                
                # give_currency and take_currency are NOW HARDCODED
                Orders.objects.create(amnt_give=amount, amnt_take=taken_amount, rate=rate, provider_give=provider_give, provider_take=provider_take, give_currency_id=1, take_currency_id=2)
                return json_true(req, {'response': respone_data})

    else:
        return json_true(req, {'message': 'nothing to return'})
    
