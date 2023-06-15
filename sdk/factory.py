
from sdk.btc import get_current_height, get_out_trans_from, get_in_trans_from, get_sum_from, \
    get_balance, get_prec as  get_prec_btc, \
    sweep_address_to as sweep_address_to_btc, generate_address as generate_address_btc,\
    estimate_fee as estimate_fee_btc


from sdk.eth import get_current_height as heth, get_out_trans_from as outeth, get_in_trans_from as ineth, \
    get_sum_from as sumfrometh, get_balance as balanceeth, get_prec as get_prec_eth,\
    sweep_address_to as sweep_address_to_eth, setup_eth_access, generate_address as generate_address_eth,\
    estimate_fee as estimate_fee_eth

import sdk.eth

from sdk.erc20 import get_current_height as herc, get_out_trans_from as outerc, get_in_trans_from as inerc, \
    get_sum_from as sumfromerc, get_balance as balanceerc, setup_title_usdt_token as setup_erc20_usdt, \
    get_prec as get_prec_erc, sweep_address_to as sweep_address_to_erc20, generate_address as generate_address_erc20,\
    get_native_balance as erc20_native_balance


from sdk.tron import get_current_height as htron, get_out_trans_from as outtron, get_in_trans_from as intron, \
    get_sum_from as sumfromtron, get_balance as balancetron, setup_title_usdt_token as setup_tron_usdt,\
    get_prec as get_prec_tron, sweep_address_to as sweep_address_to_tron, generate_address as generate_address_tron,\
    get_native_balance as tron_native_balance


from decimal import Decimal




class CryptoFactory:

    def __init__(self, arg, network="native"):
        self.__currency = arg
        if self.__currency == "eth":
            self.__sdk = sdk.eth

        if network is None:
            network = "native"

        self.__network = network
        self.__default_address = None
        self.__dict_call = {

            "btc": {
                "get_prec": get_prec_btc,
                "estimate_fee": estimate_fee_btc,
                "get_current_height": get_current_height,
                "get_out_trans_from": get_out_trans_from,
                "get_in_trans_from": get_in_trans_from,
                "get_sum_from": get_sum_from,
                "get_balance": get_balance,
                "sweep_address_to": sweep_address_to_btc,
                "generate_address": generate_address_btc,

            },
            "eth": {
                "get_prec": get_prec_eth,
                "estimate_fee": estimate_fee_eth,
                "get_current_height": heth,
                "get_out_trans_from": outeth,
                "get_in_trans_from": ineth,
                "get_sum_from": sumfrometh,
                "get_balance": balanceeth,
                "sweep_address_to": sweep_address_to_eth,
                "generate_address": generate_address_eth
            },
        }
        if arg == "eth":
            setup_eth_access()

        if arg == "usdt" and network == "erc20":
            setup_erc20_usdt()
            self.__dict_call["usdt"] = {
                "get_prec": get_prec_erc,
                "get_current_height": herc,
                "get_out_trans_from": outerc,
                "get_in_trans_from": inerc,
                "get_sum_from": sumfromerc,
                "get_balance": balanceerc,
                "native_balance": erc20_native_balance,
                "sweep_address_to": sweep_address_to_erc20,
                "generate_address": generate_address_erc20

            }

        if arg == "usdt" and network == "tron":
            setup_tron_usdt()
            self.__dict_call["usdt"] = {
                "get_prec": get_prec_tron,
                "get_current_height": htron,
                "get_out_trans_from": outtron,
                "get_in_trans_from": intron,
                "get_sum_from": sumfromtron,
                "get_balance": balancetron,
                "native_balance": tron_native_balance,
                "sweep_address_to": sweep_address_to_tron,
                "generate_address": generate_address_tron
            }
        self.prec = self.__dict_call[arg]["get_prec"]()

    def set_default(self, addr):
        self.__default_address = addr
        return True

    def amnt_to_human(self, amnt):
        return Decimal(int(amnt)/self.prec)

    @property
    def default_address(self):
        return self.__default_address

    @property
    def currency(self):
        return self.__currency

    @property
    def network(self):
        return self.__network

    def raw_call(self, name, *args, **kwargs):
        bar = getattr(self.__sdk, name)
        return bar(*args, **kwargs)

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
        show_normal = kwargs.pop("show_normal", False)
        value = call_obj(*args, **kwargs)
        if show_normal:
            return Decimal(value/self.prec)
        else:
            return value

    def estimate_fee(self, *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["estimate_fee"]
        value = call_obj(*args, **kwargs)
        if kwargs.get("show_normal", False):
            return Decimal(value/self.prec)
        else:
            return value

    def generate_address(self,  *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["generate_address"]
        return call_obj(*args, **kwargs)
    
    def sweep_address_to(self,  *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["sweep_address_to"]
        return call_obj(*args, **kwargs)

    def native_balance(self,  *args, **kwargs):
        call_obj = self.__dict_call[self.__currency]["native_balance"]
        return call_obj(*args, **kwargs)


