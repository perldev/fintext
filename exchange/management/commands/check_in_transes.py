from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import Invoice, CHECKOUT_STATUS_FREE, Trans
from oper.models import context_vars
from sdk.factory import CryptoFactory
from datetime import datetime
from decimal import Decimal
import json
import traceback
import requests
import hashlib

AML_ACCESSTOKEN = None
AML_ACCESSID = None

try:
    from private_settings import AML_ACCESSTOKEN as ac, AML_ACCESSID as ai
    AML_ACCESSTOKEN = ac
    AML_ACCESSID = ai

except:
    pass


class Command(BaseCommand):
    help = "Check incoming on transes on risk"

    def handle(self, *args, **options):
        for trans in Trans.objects.filter(status='created'):

            asset = None
            if trans.currency_provider.title == "tron":
                asset = "TRX"

            if trans.currency_provider.title == "erc20":
                asset = "ETH"

            if trans.currency.title in ("eth", "btc"):
                asset = trans.currency.title.upper()

            def_risk_accepted = context_vars.objects.get(name="risk"+ trans.currency.title)
            def_risk_accepted = float(def_risk_accepted.value)

            signature = trans.txid + ":" + AML_ACCESSTOKEN + ":" + AML_ACCESSID
            params = {"direction": "deposit",
                      "hash": trans.txid,
                      "address": trans["account"],
                      "asset": asset,
                      "accessId": AML_ACCESSID,
                      "token": generate_token(signature)
                      }

            resp = requests.post("https://extrnlapiendpoint.silencatech.com/", data=params)
            try:
                trans.aml_check = resp.text
                js = resp.json()
                if not js["result"]:
                    raise BaseException("some error during security check")
                else:
                    if js["data"]["riskscore"] > def_risk_accepted:
                        trans.status = "wait_secure"
                    else:
                        trans.status = "processed"

                    trans.save()
            except:
                print(resp.text)
                traceback.print_exc()
                return


def generate_token(string):
    d = hashlib.md5()
    s = string.encode()
    d.update(s)
    return d.hexdigest()


