from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
import requests
from fintex.common import json_true, json_500false
import traceback

from .models import rate, Orders

from datetime import datetime
from datetime import timedelta


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
