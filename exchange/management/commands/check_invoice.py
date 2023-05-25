from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import Invoice, CHECKOUT_STATUS_FREE, Trans, CheckAml
from fintex.settings import FIAT_CURRENCIES, CRYPTO_CURRENCY
from sdk.factory import CryptoFactory
from datetime import datetime
from decimal import Decimal
import json
import traceback
from exchange.controller import tell_invoice_check
import pytz


class Command(BaseCommand):
    help = "Check all invoices"

    def handle(self, *args, **options):
        active_invoices = Invoice.objects.filter(status='created')
        nw = datetime.now()
        print("start working %s" % nw)
        utc = pytz.UTC

        for i in active_invoices:

            if i.currency.title not in CRYPTO_CURRENCY:
                continue

            print("=" * 64)
            print("check invoice")
            print("%s %s -> %s %s expiring at %s" %
                  (i.pub_date, i.crypto_payments_details.address, i.sum, i.currency.title, i.expire_date))

            factory = CryptoFactory(i.currency.title,
                                    i.crypto_payments_details.currency_provider.title)
            new_balance = factory.get_balance(i.crypto_payments_details.address)

            # tricky, because we should remember this during sweeping to the cold
            # we do checking the balance in order to avoid more weighty checking the list of transactions
            # very tricky logic

            if Decimal(new_balance) > Decimal(i.crypto_payments_details.technical_info):

                actual_sum, transes = factory.get_sum_from(i.crypto_payments_details.address,
                                                           i.block_height)

                # data_from_api = get_in_trans_from(str(i.crypto_payments_details), i.block_height)
                # TODO TO FACTORY
                if i.sum >= actual_sum:
                    # if could not save the transes that is mean that we could contact to developer
                    try:
                        for trans in transes:

                            trans_obj = Trans.objects.create(account=i.crypto_payments_details.address,
                                                             currency=i.currency,
                                                             debit_credit="in",
                                                             order=i.order,
                                                             amnt=Decimal(trans["value"]/factory.prec),
                                                             txid=trans["hash"],
                                                             tx_raw=json.dumps(trans),
                                                             currency_provider=i.crypto_payments_details.currency_provider
                                                             )
                            CheckAml.objects.create(trans=trans_obj)

                    except:
                        traceback.print_exc()
                        continue

                    # next step is checking aml
                    i.status = 'processing'
                    i.save()
                    tell_invoice_check("check_invoice_process", i)

                    i.crypto_payments_details.status = CHECKOUT_STATUS_FREE
                    # update balance in technical info field
                    i.crypto_payments_details.technical_info = new_balance
                    i.crypto_payments_details.save()
                    continue

                if utc.localize(i.expire_date) < nw:
                    i.status = 'expired'
                    i.save()
                    i.crypto_payments_details.status = CHECKOUT_STATUS_FREE
                    i.crypto_payments_details.technical_info = new_balance
                    i.crypto_payments_details.save()
                    tell_invoice_check("check_invoice_process", i)


    
