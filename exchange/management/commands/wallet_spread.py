from django.core.management.base import BaseCommand
from datetime import datetime
from decimal import Decimal
from oper.models import simple_task
import json
import traceback
from django.core.management import call_command
from wallet.models import get_full_data
from exchange.models import PoolAccounts
from decimal import Decimal

from sdk.factory import CryptoFactory

class Command(BaseCommand):
    help = "simple task wrapper for background execute"

    def add_arguments(self, parser):
        parser.add_argument("--currency", nargs="+", type=str)
        parser.add_argument("--address", nargs="+", type=str)
        parser.add_argument("--amnt", nargs="+", type=str)

    def handle(self, *args, **options):
        self.stdout.write(str(options))
        currency = options["currency"]
        address = options["address"]
        amnt = Decimal(options["amnt"])
        self.stdout.write("from %s  %s %s" % (address, amnt, currency))

        full_data = get_full_data(address)
        poolobj = PoolAccounts.objects.get(address=address)
        if currency != "usdt":
            self.stdout.write("do nothing it's just for usdt")
            return

        if poolobj.currency_provider.title == "erc20":
            factory = CryptoFactory("eth")

        if poolobj.currency_provider.title == "tron":
            factory = CryptoFactory("tron")

        balance = factory.get_balance(address, show_normal=True)
        l = PoolAccounts.objects.filter(currency__title=currency,
                                        currency_provider=poolobj.currency_provider)
        if balance < amnt:
            self.stdout.write("i cannot do it the balance is %s and less the %s " % (balance, amnt))

        amnt4send = amnt/len(l)
        for item in l:
                try:
                    amnt2send = int(amnt4send * factory.prec)
                    res = factory.sweep_address_to(full_data["key"], full_data["address"], item.account, amnt2send)
                    if res:
                        self.stdout.write(res["txid"])
                    else:
                        raise Exception("error durng send transaction")
                except:
                    traceback.print_exc()




