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
from exchange.controller import tell_trans_check

class Command(BaseCommand):
    help = "check out transes for send checking order and invoice here should be transes only" \
           " for orders on whitebit exchange"

    def handle(self, *args, **options):

        transes4send = Trans.objects.filter(debit_credit='out',
                                            currency__title_in=NATIVE_CRYPTO_CURRENCY,
                                            status="processing",
                                            order__give_currency__title_in=NATIVE_CRYPTO_CURRENCY
                                            )
        for i in transes4send:
            i.status = "processing2"
            i.save()

            order = i.order
            factory = CryptoFactory(i.currency.title,
                                    "native")


            invoice = Invoice.objects.get(order=order)
            resp = get_full_data(invoice.crypto_payments_details.address)
            try:
                txid = factory.sweep_address_to(resp["key"], resp["address"], i.account, i.amnt)
            except:
                i.status = "failed"
                i.save()
                var = traceback.format_exc()
                tell_trans_check("send_crypto_transes_deal", i, error=var)
                continue


            i.txid = txid

            # save balance for address
            invoice.crypto_payments_details.technical_info = factory.get_balance(i.crypto_payments_details.address)
            invoice.crypto_payments_details.save()

            i.status = "processed"
            i.save()
            tell_trans_check("send_crypto_transes_deal", i)

