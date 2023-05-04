from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import Invoice, CHECKOUT_STATUS_FREE
from fintex.settings import FIAT_CURRENCIES
from sdk.factory import CryptoFactory
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = "Check BTC invoices"

    def handle(self, *args, **options):
        active_invoices = Invoice.objects.filter(status='created')
        nw = datetime.now()
        for i in active_invoices:
            if i.currency.title not in FIAT_CURRENCIES:
                factory = CryptoFactory(i.currency.title)
                new_balance = factory.get_balance(i.crypto_payments_details.address)

                # tricky, because we should remember this during sweeping to the cold
                # we doing checking the balance in order to avoid more weighty checking the list of transactions
                if Decimal(new_balance) > Decimal(i.crypto_payments_details.technical_info):

                    actual_sum, transes = factory.get_sum_from(i.crypto_payments_details.address,
                                                               i.block_height)

                    # data_from_api = get_in_trans_from(str(i.crypto_payments_details), i.block_height)
                    # TODO TO FACTORY
                    if i.sum >= actual_sum:
                        i.status = 'paid'
                        i.save()
                        i.crypto_payments_details.status = CHECKOUT_STATUS_FREE
                        i.crypto_payments_details.save()

                    if i.expire_date < nw:
                        i.status = 'expired'
                        i.save()
                        i.crypto_payments_details.status = CHECKOUT_STATUS_FREE
                        i.crypto_payments_details.save()

    
