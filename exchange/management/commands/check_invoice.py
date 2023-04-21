from django.core.management.base import BaseCommand
from sdk.btc import get_sum_from
from exchange.models import Invoice


class Command(BaseCommand):
    help = "Check BTC invoices"

    def handle(self, *args, **options):
        active_invoices = Invoice.objects.filter(status='created')
        for i in active_invoices:
            if i.currency_id == 3:
                sum = get_sum_from(str(i.crypto_payments_details), i.block_height)
                # data_from_api = get_in_trans_from(str(i.crypto_payments_details), i.block_height)
                sum_for_camparing = sum / 100000000
                if i.sum == sum_for_camparing:
                    i.status = 'paid'
                    i.save()
    
