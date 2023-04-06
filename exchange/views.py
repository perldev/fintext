from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
import requests
from fintex.common import json_true, json_500false
import traceback

from .models import rate, Orders


def main(req):
    return render(req, "exchange/detail.html", {})


# TODO  protect this from spam
def get_rate(req, from_c, to_c):
    try:
        res = requests.get("https://btc-trade.com.ua/ticker/%s_%s" % (from_c.lower(), to_c.lower()), )
        if res.status_code != 200:
            raise Exception("not avaliable")

        resj = res.json()
        return json_true(req, {"result": {"rate": resj["sell"]}})
    except:
        traceback.print_exc()
        return json_500false(req, {"description": "not avalible"})
