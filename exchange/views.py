from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render
import requests

from .models import rate, Orders

def main(req):
    return render(req, "exchange/detail.html", {})

#TODO protect this from spam
def get_rate(req, from_c, to_c):

    try:
        res = requests.get("https://btc-trade.com.ua/ticker/")
        if res.status_code !=200:
            raise Exception("not avaliable")

        resj = res.json()

        return
    except:
        return