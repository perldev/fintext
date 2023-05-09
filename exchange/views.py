from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
import requests
from fintex.common import json_true, json_500false, to_time, get_telechat_link
import traceback

import random


from datetime import datetime, timedelta as dt
from datetime import timedelta
import json
from django.core import serializers
from oper.models import rates_direction
from .models import Orders, CurrencyProvider, Currency, rate, CashPointLocation, Invoice,\
    Trans, PoolAccounts, FiatAccounts, CHECKOUT_STATUS_PROCESSING, CHECKOUT_STATUS_FREE
from oper.models import get_rate as exchange_get_rate, chat
from fintex.common import date_to_str

from fintex.settings import FIAT_CURRENCIES
import time
from sdk.btc import get_in_trans_from, get_sum_from, get_current_height
from sdk.factory import CryptoFactory

from sdk.functions import validate_credit_card


def main(req):
    return render(req, "main.html", {})


# TODO add permissions only for opers
def stock_24_hour_rate_history(req, chanel, ticker):
    [currency1, currency2] = ticker.split("_")
    give_currency = Currency.objects.get(title=currency1)
    take_currency = Currency.objects.get(title=currency2)
    from_date = datetime.now() - dt(hours=24)
    res = []
    q = rate.objects.filter(source=chanel,
                            give_currency=give_currency,
                            take_currency=take_currency,
                            pub_date__gte=from_date,
                            rate__gte=0)
    for i in q:
        res.append({"name": to_time(i.pub_date),
                    "value": i.rate})

    return json_true(req, {"result": res})


# TODO  protect this from spam
def get_rate(req, currency_from, currency_to):
    try:
        current_time = datetime.now()
        expire_time = current_time + timedelta(minutes=15)
        req.session['expire_deal_time'] = datetime.timestamp(current_time)
        currency_pair = currency_from.lower() + '_' + currency_to.lower()

        exchange_rate = exchange_get_rate(currency_from.lower(), currency_to.lower())
        req.session['exchange_rate'] = exchange_rate
        return json_true(req, {"result": {"rate": exchange_rate, "expire_time": date_to_str(expire_time)}})
    except:
        traceback.print_exc()
        return json_500false(req, {"description": "not avaliable"})
    

def get_currency_list(req):
    availiable_currencies = {}
    all_currencies = Currency.objects.all()
    for i in all_currencies:
        availiable_currencies[i.title] = i.title
    return json_true(req, {'currencies': availiable_currencies})


def create_exchange_request(req):
    if req.method == 'POST':
        body_unicode = req.body.decode('utf-8')
        body = json.loads(body_unicode)
        given_cur = body['given_cur']
        taken_cur = body['taken_cur']
        rate = float(body['rate'])
        amount = float(body['amount'])
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

                    # providers are cash of crypto
                    if (given_cur != 'uah'):
                        provider_give = CurrencyProvider.objects.get(title='native')
                        provider_take = CurrencyProvider.objects.get(title='cash')
                    else:
                        provider_give = CurrencyProvider.objects.get(title='cash')
                        provider_take = CurrencyProvider.objects.get(title='native')
                    
                    give_currency = Currency.objects.get(title=given_cur)
                    take_currency = Currency.objects.get(title=taken_cur)

                    order = Orders.objects.create(amnt_give=amount, amnt_take=taken_amount,
                                                  rate=rate,
                                                  provider_give=provider_give,
                                                  provider_take=provider_take,
                                                  give_currency=give_currency,
                                                  take_currency=take_currency)
                    
                    req.session['order_id'] = order.id

                    cash_points_arr = CashPointLocation.objects.all()
                    cash_points = {}
                    for i in cash_points_arr:
                        cash_points[i.pk] = i.title
     
                    respone_data = {
                        'given_cur': given_cur,
                        'taken_cur': taken_cur,
                        'amount': amount,
                        'taken_amount': taken_amount,
                        'cash_points': json.dumps(cash_points),
                        'message_to_user': 'Ваша заявка создана, для завершения заполните данные оплаты'
                    }
                    c = chat.objects.create(deal=order)
                    tele_link = get_telechat_link(order)
                    respone_data["t_link"] = tele_link
                    return json_true(req, {'response': respone_data})
                else:
                    respone_data = {
                        'is_expired': 'true',
                        'message_to_user': 'Время ожидания истекло, нужно сгенерировать новый курс'
                    }
                    return json_true(req, {'response': respone_data})  
            else:
                taken_amount = amount * rate

                if (given_cur != 'uah'):
                    provider_give = CurrencyProvider.objects.get(title='native')
                    provider_take = CurrencyProvider.objects.get(title='cash')
                else:
                    provider_give = CurrencyProvider.objects.get(title='cash')
                    provider_take = CurrencyProvider.objects.get(title='native')

                give_currency = Currency.objects.get(title=given_cur)
                take_currency = Currency.objects.get(title=taken_cur)

                order = Orders.objects.create(amnt_give=amount, amnt_take=taken_amount,
                                        rate=rate,
                                        provider_give=provider_give,
                                        provider_take=provider_take,
                                        give_currency=give_currency,
                                        take_currency=take_currency)
                
                req.session['order_id'] = order.id

                cash_points_arr = CashPointLocation.objects.all()
                cash_points = {}
                for i in cash_points_arr:
                    cash_points[i.pk] = i.title
                
                respone_data = {
                    'given_cur': given_cur,
                    'taken_cur': taken_cur,
                    'amount': amount,
                    'taken_amount': taken_amount,
                    'cash_points': json.dumps(cash_points),
                    'message_to_user': 'Ваша заявка создана, для завершения заполните данные оплаты'
                }
                # CREATE chat for deal
                c = chat.objects.create(deal=order)
                tele_link = get_telechat_link(order)
                respone_data["t_link"] = tele_link
                
                return json_true(req, {'response': respone_data})

    else:
        return json_true(req, {'message': 'nothing to return'})
    

def create_invoice(req):
    if req.method == 'POST':
        body_unicode = req.body.decode('utf-8')
        body = json.loads(body_unicode)
        payment_details = body['payment_details']
        is_cash = int(body['is_cash'])
        usd_net = body['usdt_net']

        order = Orders.objects.get(id=req.session['order_id'])
        t_link = get_telechat_link(order)
        isFiatPaymentDetailsValid = True

        if (order.take_currency.title == 'uah' and is_cash == False):
            isFiatPaymentDetailsValid = validate_credit_card(payment_details.replace(" ", ""))
        elif (order.take_currency.title == 'uah' and is_cash == True):
            cash_point_id = int(payment_details)
            if not CashPointLocation.objects.filter(id=cash_point_id).exists():
                isFiatPaymentDetailsValid = False

        if isFiatPaymentDetailsValid:
            if order.give_currency.title not in FIAT_CURRENCIES:
                factory = CryptoFactory(order.give_currency.title, usd_net)
                currency_id = order.give_currency_id
                last_added_crypto_address = PoolAccounts.objects.filter(currency_id=currency_id,
                                                                        status=CHECKOUT_STATUS_FREE).order_by('-pub_date').first()

                print(last_added_crypto_address)
                asum = order.amnt_give
                block_height = 0
                block_height = factory.get_current_height()
                new_invoice = Invoice(order=order,
                                      currency_id=currency_id,
                                      crypto_payments_details_id=last_added_crypto_address.id,
                                      sum=asum,
                                      block_height=block_height)
                payment_details_give = last_added_crypto_address.address
                last_added_crypto_address.status = CHECKOUT_STATUS_PROCESSING
                if order.give_currency.title == 'usdt':
                    currency_provider = CurrencyProvider.objects.get(title=usd_net)
                    last_added_crypto_address.currency_provider = currency_provider
                # last_added_crypto_address.technical_info = factory.get_balance()
                last_added_crypto_address.save()

            else:
                asum = order.amnt_give
                currency_id = order.give_currency_id
                credit_card_number = PoolAccounts.objects.filter(currency_id=currency_id,
                                                                 status=CHECKOUT_STATUS_FREE).order_by('-pub_date').first()
                credit_card_number.status = CHECKOUT_STATUS_PROCESSING
                new_invoice = Invoice(order=order,
                                      currency=order.give_currency,
                                      crypto_payments_details_id=credit_card_number.id,
                                      sum=asum)
                credit_card_number.save()
                payment_details_give = credit_card_number.address

            new_invoice.save()

            if is_cash:
                random_int = random.randrange(100001, 110000)
                random_secret_key = order.id + random_int
                cash_point_id = int(payment_details)
                cash_point_obj = CashPointLocation.objects.get(id=cash_point_id)
                trans = Trans.objects.create(account=cash_point_obj.title,
                                             payment_id=str(random_secret_key),
                                             currency=order.take_currency,
                                             amnt=order.amnt_take)
                order.trans = trans
                order.save()

                respone_data = {
                    'given_cur': str(order.give_currency),
                    'amount': order.amnt_give,
                    'payment_details_give': payment_details_give,
                    'secret_key': str(random_secret_key),
                    't_link': t_link,
                    'invoice_id': new_invoice.id,
                    'message': 'Ожидаем вашей оплаты'
                }
            else:
                trans = Trans.objects.create(account=payment_details,
                                             payment_id='',
                                             currency=order.take_currency,
                                             amnt=order.amnt_take)
                if order.take_currency.title == 'usdt':
                    currency_provider = CurrencyProvider.objects.get(title=usd_net)
                    trans.currency_provider = currency_provider

                trans.save()
                order.trans = trans
                order.save()
                respone_data = {
                    'given_cur': str(order.give_currency),
                    'amount': order.amnt_give,
                    'payment_details_give': payment_details_give,
                    't_link': t_link,
                    'invoice_id': new_invoice.id,
                    'message': 'Ожидаем вашей оплаты'
                }

            return json_true(req, {'response': respone_data})
        else:
            respone_data = {
                'error': 'Платежные данные для выплаты не валидны',
            }
            return json_true(req, {'response': respone_data})
    
    else:
        return json_true(req, {'message': 'nothing to return'})
    

def check_invoices(req, id_invoice):
    active_invoice = Invoice.objects.get(id=id_invoice)
    if active_invoice.currency.title not in FIAT_CURRENCIES:
        factory = CryptoFactory(active_invoice.currency.title,
                                active_invoice.crypto_payments_details.currency_provider.title)
        actual_sum, trances = factory.get_sum_from(active_invoice.crypto_payments_details.title,
                                                   active_invoice.block_height)

    return json_true(req, {"result": {"status": active_invoice.status}})


def order_details(request, pk):
    order = Orders.objects.get(pk=pk)
    print(order.invoice_order.status)
    context = {
        'order': order,
        "t_link": get_telechat_link(order)
    }
    return render(request, "order-details.html", context)


