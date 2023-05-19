from django.core.management.base import BaseCommand
from sdk.whitebitcalls import get_address_call, check_balance, sell_currency, check_order
from exchange.models import Orders, Trans
import time
from decimal import Decimal


class Command(BaseCommand):
    help = "Process of selling crypto on whitebit"

    def add_arguments(self, parser):
        parser.add_argument("order_id", nargs="+", type=int)

    def handle(self, *args, **options):
        order = Orders.objects.get(id=options['order_id'][0])
        give_currency = order.give_currency
        take_currency = order.take_currency
        amnt_to_sell = order.amnt_give

        # Step 1. Requesting for address
        # Logic of calling for address from whitebit
        resp1_status = 400
        resp1_error_statuses = [400, 503]
        while resp1_status in resp1_error_statuses:
            resp1 = get_address_call(give_currency.title.upper())
            if resp1.status_code == 200:
                resp_data1 = resp1.json()
                address = resp_data1['account']['address']
                print('This is crypto address from whitebit: ' + resp_data1['account']['address'])
                resp1_status = int(resp1.status_code)
            else:
                resp1_status = int(resp1.status_code)
            time.sleep(3)


        # Creating Trans with address from prev step if it's not existed
        order_transes = Trans.objects.filter(order=order, currency=give_currency)
        if not order_transes:
            Trans.objects.create(account=address,
                                 payment_id='',
                                 currency=order.give_currency,
                                 amnt=amnt_to_sell,
                                 order=order)
        else:
            print('Trans is already existed')


        # Step 2. Checking balance
        # Logic of requesting balance until it is replenished
        resp2_status = 422
        resp2_error_statuses = [422, 503]
        while resp2_status in resp2_error_statuses:
            resp2 = check_balance(give_currency.title.upper())
            if resp2.status_code == 200:
                resp_data2 = resp2.json()
                balance_amnt = Decimal(resp_data2['main_balance'])
                print('This is balance on whitebit: ' + str(balance_amnt))
                if (amnt_to_sell > balance_amnt):
                    print('Success. Balance is OK.')
                    # Go to step 3: selling currency
                    resp2_status = int(resp2.status_code)
                else:
                    print('Error. Balance is NOT enough.')
                    resp2_status = 422
            else:
                resp2_status = int(resp2.status_code)
            time.sleep(3)


        # Step 3. Selling currency
        # Logic of making sell command to whitebit after successing of previous step
        resp3_status = 422
        resp3_error_statuses = [400, 422, 503]
        market = str(give_currency.title.upper()) + '_' + str(take_currency.title.upper())
        amount = str(amnt_to_sell)
        uniqueOrderId = str(order.id) + str(int(time.time() * 1000)) # need to save this somewhere
        while resp3_status in resp3_error_statuses:
            resp3 = sell_currency(market, amount, uniqueOrderId)
            if resp3.status_code == 200:
                print('Market order was placed')
                resp3_status = int(resp3.status_code)
            else:
                resp3_status = int(resp3.status_code)
            time.sleep(3)

    
        # Step 4. Checking if order is among executed ones.
        resp4_status = 422
        resp4_error_statuses = [400, 422, 503]
        while resp4_status in resp4_error_statuses:
            resp4 = check_order(uniqueOrderId)
            if resp4.status_code == 200:
                resp_data4 = resp4.json()
                if not resp_data4:
                    # order is not executed yet
                    resp4_status = 422
                else:
                    # order is executed. need futher logic for results
                    resp4_status = int(resp4.status_code)
            else:
                resp4_status = int(resp4.status_code)
            time.sleep(3)


