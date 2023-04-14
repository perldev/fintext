from django.core.management.base import BaseCommand, CommandError

from exchange.models import rate, Currency
from oper.models import context_vars

import bitstamp.client
import json
import requests



class Command(BaseCommand):
    help = "Gather stock data"

    def handle(self, *args, **options):
        print("gather information from stock")
        print("bitstamp btc_usd")

        gather_bitstamp("btc", "usd")
        print("bitstamp eth usd")

        gather_bitstamp("eth", "usd")
        print("kuna btc uah")

        gather_kuna("btc", "uah")
        print("btctradeua btc uah")

        gather_btctradeua("btc", "uah")


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


