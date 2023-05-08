from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import Invoice, CHECKOUT_STATUS_FREE, Trans
from sdk.factory import CryptoFactory
from datetime import datetime
from decimal import Decimal
import json
import traceback
import requests

class Command(BaseCommand):
    help = "Check incoming on transes on risk"

    def handle(self, *args, **options):

        for i in Trans.objects.filter(status='created'):
            tx_raw = json(i.tx_raw)



