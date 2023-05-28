from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import PoolAccounts, CHECKOUT_STATUS_FREE, Trans, CheckAml
from oper.models import context_vars
from fintex.settings import NATIVE_CRYPTO_CURRENCY
from sdk.factory import CryptoFactory
from wallet.models import get_full_data
from datetime import datetime
from decimal import Decimal
import json
import traceback
from exchange.controller import tell_trans_check



class Command(BaseCommand):
    help = "transaction for out payment accoroding with deal"

    def handle(self, *args, **options):

        transes4send = Trans.objects.filter(debit_credit='out',
                                            currency__title_in=NATIVE_CRYPTO_CURRENCY,
                                            status="processing",
                                            order__take_currency__title_in=NATIVE_CRYPTO_CURRENCY
                                            )
        for i in transes4send:
            i.status = "processing2"
            i.save()
            order = i.order
            factory = CryptoFactory(i.currency.title,
                                    "native")
            address4 = context_vars.objects.get(name=i.currency.title + "_" + i.currency_provider.title + "_forpayment")
            address4 = address4.value
            amnt_sweep = factory.get_balance(address4, show_normal=True)

            if amnt_sweep < i.amnt:
                print("i cannot provide a payment")
                i.status = "processing"
                i.save()
                # TODO tell about this to dispetcher
                return

            resp = get_full_data(address4)
            try:

                txid = factory.sweep_address_to(resp["key"], resp["address"], i.account, i.amnt)

            except:
                i.status = "failed"
                i.save()
                var = traceback.format_exc()
                tell_trans_check("make_payment4deal", i, error=var)
                continue

            i.txid = txid
            i.status = "processed"
            i.save()
            tell_trans_check("make_payment4deal", i)

            # save balance for address
            crypto_payments_details = PoolAccounts.objects.get(address=address4)
            crypto_payments_details.technical_info = factory.get_balance(address4)
            crypto_payments_details.save()


