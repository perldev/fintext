
from sdk.btc import get_current_height, get_out_trans_from, get_in_trans_from, get_sum_from

class CryptoFactory:

    def __init__(self, arg):
        self.__currency = arg
        self.__dict_call = {
            arg:{
                "get_current_height": get_current_height,
                "get_out_trans_from": get_out_trans_from,
                "get_in_trans_from": get_in_trans_from,
                "get_sum_from": get_sum_from

            }
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
