
from sdk.btc import get_current_height, get_out_trans_from, get_in_trans_from, get_sum_from, get_balance


from sdk.eth import get_current_height as heth, get_out_trans_from as outeth, get_in_trans_from as ineth, \
    get_sum_from as sumfrometh, get_balance as balanceeth


from sdk.erc20 import get_current_height as herc, get_out_trans_from as outerc, get_in_trans_from as inerc, \
    get_sum_from as sumfromerc, get_balance as balanceerc



from sdk.tron import get_current_height as htron, get_out_trans_from as outtron, get_in_trans_from as intron, \
    get_sum_from as sumfromtron, get_balance as balancetron

class CryptoFactory:

    def __init__(self, arg):
        self.__currency = arg


        self.__dict_call = {
            "btc":{
                "get_current_height": get_current_height,
                "get_out_trans_from": get_out_trans_from,
                "get_in_trans_from": get_in_trans_from,
                "get_sum_from": get_sum_from,
                "get_balance": get_balance

            },
            "eth": {
                "get_current_height": heth,
                "get_out_trans_from": outeth,
                "get_in_trans_from": ineth,
                "get_sum_from": sumfrometh,
                "get_balance": balanceeth

            },
            "usdt": {
                "get_current_height": herc,
                "get_out_trans_from": outerc,
                "get_in_trans_from": inerc,
                "get_sum_from": sumfromerc,
                "get_balance": balanceerc

            },
        }

    def get_current_height(self, *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["get_current_height"]
        return  call_obj(*args, **kwargs)

    def get_out_trans_from(self, *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["get_in_trans_from"]

        return call_obj(*args, **kwargs)

    def get_in_trans_from(self, *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["get_in_trans_from"]
        return call_obj(*args, **kwargs)

    def get_sum_from(self, *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["get_sum_from"]
        return call_obj(*args, **kwargs)

    def get_balance(self,  *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["get_balance"]
        return call_obj(*args, **kwargs)


