from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import Invoice, CHECKOUT_STATUS_FREE, Trans, CheckAml
from fintex.settings import NATIVE_CRYPTO_CURRENCY
from sdk.factory import CryptoFactory
from wallet.models import get_full_data
from datetime import datetime
from decimal import Decimal
import json
import traceback


class Command(BaseCommand):
    help = "check out transes for send checking order and invoice here should be transes only" \
           " for orders on whitebit exchange"

    def handle(self, *args, **options):

        transes4send = Trans.objects.filter(debit_credit='out',
                                            currency__title_in=NATIVE_CRYPTO_CURRENCY,
                                            status="created"
                                            )
        for i in transes4send:
            i.status = "processing"
            i.save()

            order = i.order
            if not order.give_currency.title in NATIVE_CRYPTO_CURRENCY:
                print("this is trans that are not affected by this process")
                continue

            # only for native

            factory = CryptoFactory(i.currency.title,
                                    "native")
            invoice = Invoice.objects.get(order=order)
            resp = get_full_data(invoice.crypto_payments_details.address)
            txid = factory.sweep_address_to(resp["key"], resp["address"], i.account, i.amnt)
            i.txid = txid
            i.status = "processed"
            i.save()
