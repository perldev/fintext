from django.core.management.base import BaseCommand
from sdk.whitebitcalls import get_address_call, check_balance, sell_currency, check_order
from exchange.models import Orders, Trans, WhitebitDeals
from django.core.exceptions import ObjectDoesNotExist
import uuid
import time
from decimal import Decimal
from datetime import datetime
from exchange.controller import tell_whitebit_finished
from sdk.factory import CryptoFactory


class Command(BaseCommand):
    help = "Process of selling crypto on whitebit"

    def add_arguments(self, parser):
        parser.add_argument("order_id", nargs="+", type=int)

    def handle(self, *args, **options):

        order = Orders.objects.get(id=options['order_id'][0])
        give_currency = order.give_currency
        factory = CryptoFactory(give_currency.title)
        take_currency = order.take_currency
        estimate_fee = factory.estimate_fee(show_normal=True)
        amnt_to_sell = order.amnt_give - estimate_fee

        whitebitdeal = None
        try:
            whitebitdeal = WhitebitDeals.objects.get(order=order)
            if whitebitdeal.status in ("processed", "failed"):
                print("we have already sold it")
                return

            if whitebitdeal.status in ("canceled", ):
                print("we cancel it")
                return




        except ObjectDoesNotExist:
            whitebitdeal = WhitebitDeals.objects.create(currency_give=give_currency.title,
                                                        amnt_give=order.amnt_give - estimate_fee,
                                                        client_order_id=str(uuid.uuid4()),
                                                        order=order,

                                                        )



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
        if whitebitdeal.trans is None:
            trans = Trans.objects.create(account=address,
                                         payment_id='',
                                         currency=order.give_currency,
                                         amnt=amnt_to_sell,
                                         order=order,
                                         status='processing',
                                         debit_credit='out')
            whitebitdeal.trans = trans
            whitebitdeal.save()
        else:
            trans = whitebitdeal.trans
            print('Trans is already existed')
            print(trans)

        # waite until trans will send
        working_wait = True
        while working_wait:
            tmp_trans = Trans.objects.get(id=trans.id)
            print("="*64)
            print(datetime.now())
            print("checking trans for sending ")
            print(trans)
            if tmp_trans.status == "processed":
                print("looks that we send transaction")
                print(tmp_trans)
                trans = tmp_trans
                print("wait untill block confirmation 5 minute ?!")
                time.sleep(300)

            if tmp_trans.status == "failed":
                print("looks that we sending transactions is failed")
                print("we cannot finished the task")

                return
            print("sleeping")
            time.sleep(60)



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
                # Must be <. Mistake is for testing
                if amnt_to_sell <= balance_amnt:
                    print('Success. Balance is OK.')
                    # Go to step 3: selling currency
                    resp2_status = int(resp2.status_code)
                else:
                    print('Error. Balance is NOT enough.')
                    resp2_status = 422
            else:
                resp2_status = int(resp2.status_code)
            time.sleep(30)

        # Step 3. Selling currency
        # Logic of making sell command to whitebit after successing of previous step
        resp3_status = 422
        resp3_error_statuses = [400, 422, 503]
        market = str(give_currency.title.upper()) + '_' + str(take_currency.title.upper())
        amount = str(amnt_to_sell)
        uniqueOrderId = whitebitdeal.client_order_id

        while resp3_status in resp3_error_statuses:
             resp3 = sell_currency(market, amount, uniqueOrderId)
             if resp3.status_code == 200:
                 print('Market order was placed')

                 resp3_status = int(resp3.status_code)
             else:
                 resp3_status = int(resp3.status_code)
             time.sleep(30)

        # Step 4. Checking if order is among executed ones.

        resp4_status = 422
        resp4_error_statuses = [400, 422, 503]

        while resp4_status in resp4_error_statuses:
            resp4 = check_order(uniqueOrderId)
            if resp4.status_code == 200:
                resp_data4 = resp4.json()
                dict_resp_for_step4 =  resp_data4[market][0]
                if "ftime" not in  resp_data4:
                    # order is not executed yet
                    resp4_status = 422
                else:
                    # order is executed. need futher logic for results
                    resp4_status = int(resp4.status_code)

            else:
                resp4_status = int(resp4.status_code)

            time.sleep(3)

        whitebitdeal.timestamp = datetime.fromtimestamp(dict_resp_for_step4['ftime'])
        whitebitdeal.price = dict_resp_for_step4['price']
        whitebitdeal.fee = dict_resp_for_step4['dealFee']
        whitebitdeal.status = 'processed'
        whitebitdeal.currency_take = take_currency.title
        whitebitdeal.amnt_take = dict_resp_for_step4['dealMoney']
        whitebitdeal.save()

        tell_whitebit_finished("whitebit_exchange_process",  whitebitdeal)


"""
        dict_resp_for_step4 = {
            "amount": "0.0009",               
            "price": "40000",                 
            "type": "limit",                  
            "id": 4986126152,                 
            "clientOrderId": "customId11",    
            "side": "sell",                   
            "ctime": 1597486960.311311,       
            "takerFee": "0.001",              
            "ftime": 1597486960.311332,       
            "makerFee": "0.001",              
            "dealFee": "0.041258268",         
            "dealStock": "0.0009",            
            "dealMoney": "41.258268",         
            "postOnly": False,                
            "ioc": False                      
        }
"""
