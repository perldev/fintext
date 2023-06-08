from django.core.management.base import BaseCommand, CommandError

from exchange.models import rate, Currency
from oper.models import context_vars

import bitstamp.client
import json
import requests

from sdk.factory import CryptoFactory

class Command(BaseCommand):
    help = "Gather stock data"

    def handle(self, *args, **options):
        print("gather comission info for ETH")

        gather_eth_comission()

        print("gather information from stock")
        print("bitstamp btc_usd")

        gather_bitstamp("btc", "usd")
        print("bitstamp eth usd")

        gather_bitstamp("eth", "usd")
        print("kuna btc uah")

        gather_kuna("btc", "uah")
        print("btctradeua btc uah")

        gather_btctradeua("btc", "uah")

        print("gather whitebit btc uah, eth uah, usdt uah")
        gather_whitebit("BTC", "UAH")
        gather_whitebit("USDT", "UAH")
        gather_whitebit("ETH", "UAH")


def gather_eth_comission():
    give_currency = Currency.objects.get(title="eth")

    factory = CryptoFactory(give_currency.title,
                            "native")
    gas_price = factory.raw_call("get_normal_fee")
    print(gas_price)
    r = rate(source="etherscan21000",
             edit_user_id=1,
             raw_data=gas_price,
             give_currency=give_currency,
             take_currency=give_currency,
             rate=(21000*gas_price)/factory.prec)

    context_var, created = context_vars.objects.get_or_create(name="context_etherscan21000_eth_eth")
    context_var.value = r.rate
    context_var.save()
    r.save()


def gather_btctradeua(t1, t2):
    resp = requests.get("https://btc-trade.com.ua/api/ticker/%s_%s" % (t1, t2))

    give_currency = Currency.objects.get(title=t1)
    take_currency = Currency.objects.get(title=t2)
    result = resp.json()["%s_%s" % (t1, t2)]

    r = rate(source="btctradeua", edit_user_id=1,
             raw_data=json.dumps(resp.text),
             give_currency=give_currency,
             take_currency=take_currency,
             rate=result["buy"])

    r.save()
    # save context var for rate builder
    #TODO move to decorator
    context_var, created = context_vars.objects.get_or_create(name="context_btctradeua_%s_%s" % (t1, t2))
    context_var.value = r.rate
    context_var.save()

    r.pk = None
    r.give_currency = take_currency
    r.take_currency = give_currency
    r.rate = result["sell"]
    r.save()


def gather_kuna(t1, t2):
    resp = requests.get("https://api.kuna.io/v3/tickers?symbols=%s%s" % (t1, t2))

    give_currency = Currency.objects.get(title=t1)
    take_currency = Currency.objects.get(title=t2)
    result = resp.json()[0]

    r = rate(source="kuna", edit_user_id=1,
             raw_data=json.dumps(resp.text),
             give_currency=give_currency,
             take_currency=take_currency,
             rate=result[7])

    r.save()
    # save context var for rate builder
    #TODO move to decorator
    context_var, created = context_vars.objects.get_or_create(name="context_kuna_%s_%s" % (t1, t2))
    context_var.value = r.rate
    context_var.save()

    r.pk = None
    r.give_currency = take_currency
    r.take_currency = give_currency
    r.rate = result[9]
    r.save()


def gather_bitstamp(t1, t2):
    p = bitstamp.client.Public()
    give_currency = Currency.objects.get(title=t1)
    take_currency = Currency.objects.get(title=t2)
    res = p.ticker_hour(t1, t2)
    r = rate(source="bitstamp", edit_user_id=1,
             raw_data=json.dumps(res),
             give_currency=give_currency,
             take_currency=take_currency,
             rate=res["low"])
    r.save()
    #save context var for rate builder
    #TODO move to decorator
    context_var, created = context_vars.objects.get_or_create(name="context_bitstamp_%s_%s" % (t1, t2))
    context_var.value = r.rate
    context_var.save()

    r.pk = None
    r.give_currency = take_currency
    r.take_currency = give_currency
    r.rate = res["high"]
    r.save()


def gather_whitebit(t1, t2):
    resp = requests.get("https://whitebit.com/api/v2/public/ticker")
    currency_pair = t1 + '_' + t2
    result = resp.json()
    res = None
    sell_rate = None
    buy_rate = None
    give_currency = Currency.objects.get(title=t1.lower())
    take_currency = Currency.objects.get(title=t2.lower())
    for i in result["result"]:      
        if i["tradingPairs"] == currency_pair:
            res = i
            sell_rate = i["lowestAsk"]
            buy_rate = i["highestBid"]
            break
    
    r = rate(source="whitebit", 
             edit_user_id=1,
             raw_data=json.dumps(res),
             give_currency=give_currency,
             take_currency=take_currency,
             rate=sell_rate)
    r.save()

    context_var, created = context_vars.objects.get_or_create(name="context_whitebit_%s_%s" % (t1.lower(), t2.lower()))
    context_var.value = r.rate
    context_var.save()

    r.pk = None
    r.give_currency = take_currency
    r.take_currency = give_currency
    r.rate = buy_rate
    r.save()
