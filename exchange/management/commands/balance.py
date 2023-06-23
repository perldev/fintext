from django.core.management.base import BaseCommand
from datetime import datetime
from decimal import Decimal
import json
import traceback
from wallet.models import get_full_data
from exchange.models import PoolAccounts, Currency

from decimal import Decimal
from oper.models import context_vars
from sdk.factory import CryptoFactory

class Command(BaseCommand):
    help = "gather balance of system"

    def handle(self, *args, **options):
        self.stdout.write("starting calculated")
        btc_factory = CryptoFactory("btc")
        btc_balance = Decimal("0")
        for i in PoolAccounts.objects.filter(currency__title="btc"):
            i.technical_info = btc_factory.get_balance(i.address)
            btc_balance = btc_balance + Decimal(i.technical_info)/btc_factory.prec
            i.save()
        var, created = context_vars.objects.get_or_create(name="btc_balance")
        var.value = btc_balance
        var.save()

        eth_factory = CryptoFactory("eth")

        eth_balance = Decimal("0")
        for i in PoolAccounts.objects.filter(currency__title="eth"):
            i.technical_info = eth_factory.get_balance(i.address)
            eth_balance = eth_balance + Decimal(i.technical_info) / eth_factory.prec
            i.save()

        var, created = context_vars.objects.get_or_create(name="eth_balance")
        var.value = eth_balance
        var.save()

        erc_factory = CryptoFactory("usdt", "erc20")
        erc_balance = Decimal("0")
        for i in PoolAccounts.objects.filter(currency__title="usdt", currency_provider__title="erc20"):
            i.technical_info = erc_factory.get_balance(i.address)
            i.ext_info = erc_factory.native_balance(i.address)
            erc_balance = erc_balance + Decimal(i.technical_info) / erc_factory.prec
            i.save()

        var, created = context_vars.objects.get_or_create(name="usdt_erc20_balance")
        var.value = erc_balance
        var.save()

        tron_factory = CryptoFactory("usdt", "tron")
        tron_balance = Decimal("0")

        for i in PoolAccounts.objects.filter(currency__title="usdt", currency_provider__title="tron"):
            i.technical_info = tron_factory.get_balance(i.address)
            i.ext_info = tron_factory.native_balance(i.address)
            tron_balance = tron_balance + Decimal(i.technical_info) / tron_factory.prec
            i.save()

        var, created = context_vars.objects.get_or_create(name="usdt_tron_balance")
        var.value = tron_balance
        var.save()









