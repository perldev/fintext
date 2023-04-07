from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
import requests
from fintex.common import json_true, json_500false
import traceback

from .models import rate, Orders

import json
from django.http import HttpResponse


def main(req):
    return render(req, "main.html", {})


# TODO  protect this from spam
def get_rate(req, currency_from, currency_to):
    try:
        res = requests.get("https://btc-trade.com.ua/api/ticker/%s_%s" % (currency_from.lower(), currency_to.lower()), )
        if res.status_code != 200:
            raise Exception("not avaliable")

        resj = res.json()
        return HttpResponse(json.dumps(resj), content_type = "application/json")
    except:
        traceback.print_exc()
        return json_500false(req, {"description": "not avalible"})
