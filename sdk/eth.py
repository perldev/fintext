import requests

import hashlib
import json
from decimal import Decimal
# import BasicUi
import traceback
import json
import sys
import re
from web3 import Web3, AsyncWeb3

from binascii import hexlify, unhexlify

INFURA_KEY = None
try
   from private_settings import INFURA_KEY as INF
   INFURA_KEY = INF
except:
   pass
    

class CryptoAccountERC20:
    def __init__(self):
        self.__currency = kwargs["currency"]
        self.__contract_account = kwargs["contract_account"]


class CryptoAccountETH:
    def __init__(self, **kwargs):
        self.__currency = kwargs["currency"]
        self.__api = "https://api.blockchain.info/v2/eth/data/account/"
        self.__w3 = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/%s" % kwargs["INFURA_KEY"]))

    #  https://api.blockchain.info/v2/eth/data/account/0x690b9a9e9aa1c9db991c7721a92d351db4fac990/internalTransactions?page=0&size=20
    # "https://api.blockchain.info/v2/eth/data/account/0x522211d186f8a3ffdd4cf9c83884fe8ede3aac74/tokens"
    # "https://api.blockchain.info/v2/eth/data/account/0x522211d186f8a3ffdd4cf9c83884fe8ede3aac74/wallet"

    def walletpassphrase(self, time=20):
        raise Exception("Is not implemented")

    def keypoolrefill(self, size=None):
        raise Exception("Is not implemented")

    def getrawmempool(self):
        raise Exception("Is not implemented")

    def getrawtransaction(self, txid):
        raise Exception("Is not implemented")

    def decoderawtransaction(self, hex_data):
        raise Exception("Is not implemented")

    def listaddressgroupings(self):
        raise Exception("Is not implemented")

    def walletlock(self):
        raise Exception("Is not implemented")

    def dumpwallet(self, filename):
        raise Exception("Is not implemented")

    def backupwallet(self, filename):
        raise Exception("Is not implemented")

    def dumpprivkey(self, Addr):
        raise Exception("Is not implemented")

    def getstatus(self):
        raise Exception("Is not implemented")

    def getbalance(self, address):
        return self.__w3.get_balance(address)


    def getnewaddress(self):
        raise Exception("Is not implemented")

    def listunspent(self):
        raise Exception("Is not implemented")

    def get_current_height(self):
        return self.w3.eth.get_block_number()

    def get_out_trans_from(self, acc, blockheight=0):
        resp = requests.get(self. % acc, headers=self.headers)
        respj = resp.json()
        result = []
        for trans in respj["txs"]:

            if not trans["block_height"]:
                continue

            if trans["block_height"] < blockheight:
                continue
            for i2 in trans["inputs"]:
                if i2["addr"] == acc:
                    i2["hash"] = trans["hash"]
                    result.append(i2)
        return result

    def get_in_trans_from(self, acc, blockheight=0):
        resp = requests.get("https://blockchain.info/rawaddr/%s" % acc, headers=self.def_headers)
        respj = resp.json()
        result = []
        for trans in respj["txs"]:
            if not trans["block_height"]:
                continue

            if trans["block_height"] < blockheight:
                continue
            for i2 in trans["out"]:
                if i2["addr"] == acc:
                    i2["hash"] = trans["hash"]
                    result.append(i2)
        return result

    def get_sum_from(self, acc, blockheight=0):
        in_trans = self.get_in_trans_from(acc, blockheight)
        d = 0
        for i in in_trans:
            d = d + i["value"]
        return d / PREC, in_trans


