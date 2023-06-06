from django.core.management.base import BaseCommand
from sdk.whitebitcalls import get_address_call, check_balance, sell_currency, check_order,\
    check_balance_trade, transfer_balance, deposit_history
from exchange.models import Orders, Trans, WhitebitDeals
from django.core.exceptions import ObjectDoesNotExist
import uuid
import time
from decimal import Decimal
from datetime import datetime
from exchange.controller import tell_whitebit_finished
from sdk.factory import CryptoFactory
from fintex.common import format_numbers4, format_numbers10


class Command(BaseCommand):
    help = "Process of selling crypto on whitebit"

    def add_arguments(self, parser):
        parser.add_argument("order_id", nargs="+", type=int)

    def handle(self, *args, **options):

        order = Orders.objects.get(id=options['order_id'][0])
        give_currency = order.give_currency
        factory = CryptoFactory(give_currency.title)
        take_currency = order.take_currency
        working_currency = give_currency.title.upper()

        estimate_fee = factory.estimate_fee(show_normal=True)
        amnt_to_sell = order.amnt_give - estimate_fee
        whitebitdeal = None
        try:
            whitebitdeal = WhitebitDeals.objects.get(order=order)
            if whitebitdeal.status in ("processed", "failed"):
                print("we have already sold it")
                print("but we notify about this again")
                return tell_whitebit_finished("whitebit_exchange_process",  whitebitdeal)

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
            resp1 = get_address_call(working_currency)
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
                                         payment_id='whitebit clearing',
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
            #    time.sleep(300)
                working_wait = False
                break
            if tmp_trans.status == "failed":
                print("looks that we sending transactions is failed")
                print("we cannot finished the task")

                return
            print("sleeping")
            time.sleep(60)

        # wait until transaction will arrive
        crypto_trans_exist = False
        for i in range(1, 50):
            print("checking deposit history try %i" %i)
            if check_crypto_trans(trans.txid, working_currency):
                crypto_trans_exist = True
                break
            print("wait a minute")
            time.sleep(60)

        if not crypto_trans_exist:
            print("we wait for 1 hour but cannot await transaction on whitebit")
            print("may we should check something")
            return

        amnt_to_sell = trans.amnt
        # check deposit of this transaction
        # Step 2. Checking balance
        # Logic of requesting balance until it is replenished
        # wait until transaction will arrive
        balance = wait_balance_main(working_currency)
        balance_trade = wait_balance_trade(working_currency)
        all_balance = balance_trade + balance
        print("whole balance there is %s" % all_balance)
        if not amnt_to_sell <= all_balance:
            print("something wrong with balance go panic")
            return
        else:
            # if balance is enough
            if balance_trade>= amnt_to_sell:
               print("balance of trade is enogh ok go further")
            else:
               print("balance is not enough")
               print("making transfer")
               amnt_leak = amnt_to_sell - balance_trade
               transfer_result = False
               for i in range(1, 60):
                    resp = transfer_balance(working_currency, format_numbers10(amnt_leak))
                    if resp.status_code != 200:
                        print
                        continue
                    else:
                        transfer_result = True
                        print("seems good")
                        break

        # Step 3. Selling currency
        # Logic of making sell command to whitebit after successing of previous step
        resp3_status = 422
        resp3_error_statuses = [400, 422, 503]
        market = str(give_currency.title.upper()) + '_' + str(take_currency.title.upper())
        amount = amnt_to_sell
        uniqueOrderId = whitebitdeal.client_order_id

        #check order before
        resp4 = check_order(uniqueOrderId)
        dict_resp_for_step4 = {}
        if resp4.status_code == 200:
            resp_data4 = resp4.json()
            print("got info on order  %s " % uniqueOrderId)
            print(resp_data4)
            if len(resp_data4) > 0:
                dict_resp_for_step4 = resp_data4[market][0]
                if "ftime" in dict_resp_for_step4:
                    print("order is  executed yet")
                    dict_resp_for_step4["executed"] = True
            else:
                # order is executed. need further logic for results
                print("order is executed yet")
        else:
            resp4_status = int(resp4.status_code)
            print("there is no order yeat")

        if not "executed" in dict_resp_for_step4:

            while resp3_status in resp3_error_statuses:
                 print("starting selling ")
                 amount = format_numbers4(amount)
                 print(market, amount, uniqueOrderId)

                 resp3 = sell_currency(market, amount, uniqueOrderId)
                 print("got")
                 print(resp3.text)
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
                    dict_resp_for_step4 = resp_data4[market][0]
                    if "ftime" in dict_resp_for_step4:
                        # order is  executed yet
                        resp4_status = 422
                        break
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


def check_crypto_trans(txid, currency):
    resp = deposit_history(currency)
    if resp.status_code != 200:
        return False
    transes = resp.json()
    for trans in transes["records"]:
        if trans["transactionHash"] == txid: # TODO add checking amount
            return True
    return False

def wait_balance_main(currency, sleep_time=60):
    resp2_status = 422
    resp2_error_statuses = [422, 503]
    while resp2_status in resp2_error_statuses:
        print("checking balance")
        resp2 = check_balance(currency)
        print(resp2.text)
        if resp2.status_code == 200:
            resp_data2 = resp2.json()
            balance_amnt = Decimal(resp_data2['main_balance'])
            print('This is balance on whitebit: ' + str(balance_amnt))
            # Must be <. Mistake is for testing
            return balance_amnt

        else:
            resp2_status = int(resp2.status_code)
        print("sleep a while")
        time.sleep(sleep_time)

    raise Exception("cannot receive main balance")


def wait_balance_trade(currency, sleep_time=60):

    for i in  range(1, 50):
        print("#%i" % i)
        resp = check_balance_trade(currency)
        print(resp)
        print(resp.text)
        if not resp.status_code in [200, 201]:
            print("received on balance request")
            print(resp.text)
            print("goo sleep  a while")
        else:
            respj = resp.json()
            if "available" in respj:
                return Decimal(respj["available"])
            else:
                print("something wrong")
                print(respj)
                print("sleep a while")

        time.sleep(sleep_time)

    raise Exception("cannot receive trade balance")

