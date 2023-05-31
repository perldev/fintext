from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import Invoice, CHECKOUT_STATUS_FREE, Trans, CheckAml
from oper.models import context_vars
from sdk.factory import CryptoFactory
from datetime import datetime
from decimal import Decimal
import json
import traceback
import requests
import hashlib
from exchange.controller import tell_aml_check, tell_trans_check


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
        for aml_trans in CheckAml.objects.filter(status='created'):
            trans = aml_trans.trans

            asset = None
            if trans.currency_provider.title == "tron":
                asset = "TRX"

            if trans.currency_provider.title == "erc20":
                asset = "ETH"

            if trans.currency.title in ("eth", "btc"):
                asset = trans.currency.title.upper()

            def_risk_accepted = context_vars.objects.get(name="risk" + trans.currency.title)
            def_risk_accepted = float(def_risk_accepted.value)

            signature = trans.txid + ":" + AML_ACCESSTOKEN + ":" + AML_ACCESSID
            params = {"direction": "deposit",
                      "hash": trans.txid,
                      "address": trans.account,
                      "asset": asset,
                      "accessId": AML_ACCESSID,
                      "token": generate_token(signature)
                      }

            resp = requests.post("https://extrnlapiendpoint.silencatech.com/", data=params)
            try:
                aml_trans.aml_check = resp.text
                aml_trans.status = "processed"
                js = resp.json()
                if not js["result"]:
                    raise BaseException("some error during security check")
                else:
                    if js["data"]["riskscore"] > def_risk_accepted:
                        trans.status = "wait_secure"
                    else:
                        trans.status = "processed"

                    aml_trans.result = js["data"]["riskscore"]
                    aml_trans.save()
                    tell_aml_check("aml_check_process", aml_trans)
                    trans.save()
                    tell_trans_check("aml_check_process", trans)

            except:
                aml_trans.status = "failed"
                aml_trans.aml_check = resp.text
                aml_trans.save()
                tell_aml_check("aml_check_process", aml_trans)

                print(resp.text)
                traceback.print_exc()
                return


def generate_token(string):
    d = hashlib.md5()
    s = string.encode()
    d.update(s)
    return d.hexdigest()


