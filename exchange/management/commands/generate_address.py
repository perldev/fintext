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
from sdk.factory import CryptoFactory

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("currency", nargs="+", type=str)
        parser.add_argument("network", nargs="+", type=str)
        parser.add_argument("count", nargs="+", type=int)

    help = "Create test  order for exchange"

    def handle(self, *args, **options):
        c = Currency.objects.get(title=options["currency"])
        network = options["network"]

        factory = CryptoFactory(c.title, network)
        respj = factory.generate_address()






