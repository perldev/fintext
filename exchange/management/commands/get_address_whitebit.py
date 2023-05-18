from django.core.management.base import BaseCommand
from sdk.whitebitcalls import get_address_call
from exchange.models import Invoice, Trans


class Command(BaseCommand):
    help = "Get crypto addresses from whitebit for futher transfers"

    def handle(self, *args, **options):
        processed_invoices = Invoice.objects.filter(status='processed')

        for i in processed_invoices:
            resp = get_address_call(i.currency.title.upper())
            resp_data = resp.json()
            Trans.objects.create(account=resp_data['account']['address'],
                                payment_id='',
                                currency=i.order.give_currency,
                                amnt=i.order.amnt_give,
                                order=i.order)
            print(resp_data['account']['address'])

