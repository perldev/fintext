"""
WSGI config for fintex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import traceback()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintex.settings')
import bitstamp.client
from exchange.models import rate, Currency
import json
import requests



def gather_kuna(t1, t2):
    resp = requests.get("https://api.kuna.io/v3/tickers?symbols=%s%s" % (t1,t2))

    give_currency = Currency.objects.get(title=t1)
    take_currency = Currency.objects.get(title=t1)
    result = resp.json()[0]

    r = rate(source="kuna", edit_user_id=1,
             raw_data=json.dumps(resp.text),
             give_currency=give_currency,
             take_currency=take_currency,
             rate=result[7])

    r.save()
    r.pk = None
    r.give_currency = take_currency
    r.take_currency = give_currency
    r.rate = result[9]
    r.save()

def gather_bitstamp(t1,t2):
    p = bitstamp.client.Public()
    give_currency = Currency.objects.get(title=t1)
    take_currency = Currency.objects.get(title=t1)
    res = p.ticker_hour(t1, t2)
    r = rate(source="bitstamp", edit_user_id=1,
             raw_data=json.dumps(res),
             give_currency=give_currency,
             take_currency=take_currency,
             rate=res["low"])
    r.save()
    r.pk = None
    r.give_currency = take_currency
    r.take_currency = give_currency
    r.rate = res["high"]
    r.save()

def gather_chanel_data(signum):
    print("gather information from stock")
    gather_bitstamp("btc", "usd")
    gather_bitstamp("eth", "usd")
    gather_kuna("btc", "uah")
    gather_kuna("eth", "uah")




try:
    import uwsgi
    uwsgi.register_signal(97, "worker1", gather_chanel_data)
    uwsgi.add_timer(97, 120)
except:
    traceback.print_exc()

application = get_wsgi_application()
