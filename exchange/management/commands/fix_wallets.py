from django.core.management.base import BaseCommand, CommandError

from exchange.models import Currency, CurrencyProvider

import bitstamp.client
import json
from wallet.models import CryptoAccounts
from exchange.models import PoolAccounts
from oper.models import chat

from datetime import datetime, timedelta as dt
from decimal import Decimal
from sdk.factory import CryptoFactory
import json
from uuid import uuid4
from web3 import Web3
from eth_account import Account

class Command(BaseCommand):

    def handle(self, *args, **options):
        print(options)

        for obj in  CryptoAccounts.objects.using("security").filter(address__startswith="0x"):
            j = json.loads(obj.raw_data)
            k = eval(j["key"])
            new_key = Web3.to_hex(k)
            print(obj.address)
            print(Account.from_key(new_key).address)
            print(new_key)
            print("="*64)
            j["key"] = new_key
            obj.raw_data = json.dumps(j)
            obj.save(using="security")







