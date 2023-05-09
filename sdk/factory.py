
from sdk.btc import get_current_height, get_out_trans_from, get_in_trans_from, get_sum_from, \
    get_balance, get_prec as  get_prec_btc


from sdk.eth import get_current_height as heth, get_out_trans_from as outeth, get_in_trans_from as ineth, \
    get_sum_from as sumfrometh, get_balance as balanceeth, get_prec as get_prec_eth


from sdk.erc20 import get_current_height as herc, get_out_trans_from as outerc, get_in_trans_from as inerc, \
    get_sum_from as sumfromerc, get_balance as balanceerc, setup_title_usdt_token as setup_erc20_usdt, \
    get_prec as get_prec_erc


from sdk.tron import get_current_height as htron, get_out_trans_from as outtron, get_in_trans_from as intron, \
    get_sum_from as sumfromtron, get_balance as balancetron, setup_title_usdt_token as setup_tron_usdt,\
    get_prec as get_prec_tron


class CryptoFactory:

    def __init__(self, arg, network="native"):
        self.__currency = arg
        if network is None:
            network = "native"

        self.__network = network

        self.__dict_call = {
            "btc": {
                "get_prec": get_prec_btc,
                "get_current_height": get_current_height,
                "get_out_trans_from": get_out_trans_from,
                "get_in_trans_from": get_in_trans_from,
                "get_sum_from": get_sum_from,
                "get_balance": get_balance

            },
            "eth": {
                "get_prec": get_prec_eth,
                "get_current_height": heth,
                "get_out_trans_from": outeth,
                "get_in_trans_from": ineth,
                "get_sum_from": sumfrometh,
                "get_balance": balanceeth

            },
        }
        if arg == "usdt" and network == "erc20":
            setup_erc20_usdt()
            self.__dict_call["usdt"] = {
                "get_prec": get_prec_erc,
                "get_current_height": herc,
                "get_out_trans_from": outerc,
                "get_in_trans_from": inerc,
                "get_sum_from": sumfromerc,
                "get_balance": balanceerc
                }

        if arg == "usdt" and network == "tron":
            setup_tron_usdt()
            self.__dict_call["usdt"] = {
                "get_prec": get_prec_tron,
                "get_current_height": htron,
                "get_out_trans_from": outtron,
                "get_in_trans_from": intron,
                "get_sum_from": sumfromtron,
                "get_balance": balancetron
            }
        self.prec = self.__dict_call[arg]["get_prec"]()


    def get_current_height(self, *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["get_current_height"]
        return call_obj(*args, **kwargs)

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


