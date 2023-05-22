from django.core.management.base import BaseCommand, CommandError

from exchange.models import Currency, CurrencyProvider

import bitstamp.client
import json
import requests

from wallet.models import CryptoAccounts
from exchange.models import PoolAccounts
from oper.models import chat

from datetime import datetime, timedelta as dt
from decimal import Decimal
from sdk.factory import CryptoFactory

from uuid import uuid4

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("currency", nargs="+", type=str)
        parser.add_argument("network", nargs="+", type=str)
        parser.add_argument("count", nargs="+", type=int)

    help = "Create test  order for exchange"

    def handle(self, *args, **options):
        print(options)

        c = Currency.objects.get(title=options["currency"][0])

        network = options["network"][0]
        currency_provider = CurrencyProvider.objects.get(title=network)
        factory = CryptoFactory(c.title, network)
        for i in range(0, options["count"][0]):
            respj = factory.generate_address()
            obj = CryptoAccounts.objects.using("security").create(address=respj["address"],
                                                                  raw_data=json.dumps(respj))
            d = PoolAccounts.objects.create(currency=c,
                                            address=obj.address,
                                            technical_info="0",
                                            currency_provider=currency_provider,)

            if factory.network != "native":
                d.ext_info = "0"

                d.save()










