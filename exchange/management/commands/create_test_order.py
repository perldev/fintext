from django.core.management.base import BaseCommand, CommandError

from exchange.models import rate, Currency
from oper.models import context_vars

import bitstamp.client
import json
import requests

from exchange.models import Orders, Currency, CurrencyProvider
from oper.models import chat

from datetime import datetime, timedelta as dt
from decimal import Decimal

class Command(BaseCommand):
    help = "Create test  order for exchange"

    def handle(self, *args, **options):
        c1 = Currency.objects.get(title="btc")
        c2 = Currency.objects.get(title="uah")
        cp = CurrencyProvider.objects.get(id=1)
        pub = datetime.now()
        expire = pub + dt(hours=2)
        rate = Decimal("1000000")
        o = Orders.objects.create(status="created",
                                  give_currency=c1,
                                  take_currency=c2,
                                  provider_give=cp,
                                  provider_take=cp,
                                  expire_date=expire,
                                  pub_date=pub,
                                  amnt_give=Decimal("0.1"),
                                  amnt_take=Decimal("0.1")*rate,
                                  rate=rate)
        c = chat.objects.create(deal=o)





