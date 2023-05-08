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
API_HOST = "https://api.blockchain.info/v2/eth/data/account/"
def_headers = {"Content-Type": "application/json"}
PREC = 10 ** 18

INFURA_KEY = None
try:
   from private_settings import INFURA_KEY as INF
   INFURA_KEY = INF
except:
   pass
    

def get_prec():
    return PREC

def get_current_height():
    w3 = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/%s" % INFURA_KEY))
    return w3.eth.get_block_number()


def get_out_trans_from(acc, blockheight=0):

    resp1 = requests.get(API_HOST + "%s/internalTransactions?page=0&size=20" % acc,
                         headers=def_headers)

    resp2 = requests.get(API_HOST + "%s/wallet" % acc,
                         headers=def_headers)

    respj1 = resp1.json()
    respj2 = resp2.json()
    result = []

    if "internalTransactions" in respj1:
        for trans in respj1["internalTransactions"]:
            if "blockNumber" not in trans:
                continue

            if not Decimal(trans["value"]):
                continue

            if int(trans["blockNumber"]) < blockheight:
                continue

            if trans["from"] == acc:
                result.append({"hash": trans["transactionHash"],
                               "value": trans["value"],
                               "addr": acc,
                               "to": trans["to"],
                               "raw": json.dumps(trans),
                               "block_height": trans["blockNumber"]})

    if "accountTransactions" in respj2:
        for trans in respj2["accountTransactions"]:

            if "blockNumber" not in trans:
                continue

            if not Decimal(trans["value"]):
                continue

            if trans["state"] != "CONFIRMED" or  not trans["success"]:
                continue

            if int(trans["blockNumber"]) < blockheight:
                continue

            if trans["from"] == acc:
                result.append({"hash": trans["hash"],
                               "value": trans["value"],
                               "addr": acc,
                               "to": trans["to"],
                               "raw": json.dumps(trans),
                               "block_height": trans["blockNumber"]})


    return result


def get_in_trans_from(self, acc, blockheight=0):

    resp1 = requests.get(API_HOST + "%s/internalTransactions?page=0&size=20" % acc,
                         headers=def_headers)

    resp2 = requests.get(API_HOST + "%s/wallet" % acc,
                         headers=def_headers)

    respj1 = resp1.json()
    respj2 = resp2.json()
    result = []

    if "internalTransactions" in respj1:
        for trans in respj1["internalTransactions"]:
            if "blockNumber" not in trans:
                continue

            if not Decimal(trans["value"]):
                continue

            if not trans["type"] == "CALL":
                continue

            if int(trans["blockNumber"]) < blockheight:
                continue

            if trans["to"] == acc:
                result.append({"hash": trans["transactionHash"],
                               "value": trans["value"],
                               "addr": acc,
                               "from": trans["from"],
                               "raw": json.dumps(trans),
                               "block_height": trans["blockNumber"]})

    if "accountTransactions" in respj2:
        for trans in respj2["accountTransactions"]:

            if "blockNumber" not in trans:
                continue

            if not Decimal(trans["value"]):
                continue

            if trans["state"] != "CONFIRMED" or  not trans["success"]:
                continue

            if int(trans["blockNumber"]) < blockheight:
                continue

            if trans["to"] == acc:
                result.append({"hash": trans["hash"],
                               "value": trans["value"],
                               "addr": acc,
                               "from": trans["from"],
                               "raw": json.dumps(trans),
                               "block_height": trans["blockNumber"]})


    return result


def get_sum_from(acc, blockheight=0):
    in_trans = get_in_trans_from(acc, blockheight)
    d = 0
    for i in in_trans:
        d = d + i["value"]
    return d / PREC, in_trans


def get_balance(acc):
    w3 = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/%s" % INFURA_KEY))
    return Decimal(w3.get_balance(acc))/PREC

