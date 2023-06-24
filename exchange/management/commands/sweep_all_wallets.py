from django.core.management.base import BaseCommand
from datetime import datetime
from decimal import Decimal
from oper.models import simple_task, context_vars
import json
import traceback
from django.core.management import call_command
from wallet.models import get_full_data
from exchange.models import PoolAccounts
from decimal import Decimal

from sdk.factory import CryptoFactory

# TODO add special for BTC

class Command(BaseCommand):
    help = "simple task wrapper for background execute"

    def add_arguments(self, parser):
        parser.add_argument("--currency", nargs="+", type=str)
        parser.add_argument("--currency_provider", nargs="+", type=str)
        parser.add_argument("--min_amnt", nargs="+", type=str)

    def handle(self, *args, **options):
        self.stdout.write(str(options))
        currency = options["currency"]
        currency_provider = options["currency_provider"]
        min_amnt = Decimal(options["min_amnt"])
        self.stdout.write("gether %s  %s %s" % (currency, currency_provider, min_amnt))
        factory = CryptoFactory(currency, currency_provider)
        var = context_vars.objects.get(name="%s_%s_forpayment" % (currency, currency_provider))
        sweep_address = var.value
        for item in PoolAccounts.objects.filter(currency__title=currency,
                                                currency_provider__title=currency_provider):
                amnt = factory.get_balance(item.address, show_normal=True)
                if amnt<min_amnt:
                    self.stdout.write("not enough for send")
                    continue

                item.refresh_from_db()

                #possible race condition with invoices

                if item.status == "processing":
                    self.stdout.write("address in work we cannot do this")
                    continue

                full_data = get_full_data(item.address)
                try:
                    amnt2send = int(amnt * factory.prec)
                    res = factory.sweep_address_to(full_data["key"], full_data["address"], sweep_address, amnt2send)
                    if res:
                        self.stdout.write(res["txid"])
                    else:
                        raise Exception("error durng send transaction")
                    item.technical_info = "0"
                    item.save()

                    ##if transaction wrong then balance will update this
                except:
                    traceback.print_exc()




