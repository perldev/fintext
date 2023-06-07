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
from eth_account import Account

from binascii import hexlify, unhexlify
API_HOST = "https://api.blockchain.info/v2/eth/data/account/"
def_headers = {"Content-Type": "application/json"}
PREC = 10 ** 18
ACCESS = None
verbose = True
INFURA_KEY = None
try:
   from private_settings import INFURA_KEY as INF
   INFURA_KEY = INF
except:
   pass
    

def get_prec():
    return PREC


def setup_eth_access():
    global ACCESS
    ACCESS = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/%s" % INFURA_KEY))


def get_current_height():
    w3 = ACCESS
    return w3.eth.get_block_number()


def get_out_trans_from(acc, blockheight=0):
    acc = acc.upper()
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
                               "value": int(trans["value"]),
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

            if trans["state"] != "CONFIRMED" or not trans["success"]:
                continue

            if int(trans["blockNumber"]) < blockheight:
                continue

            if trans["from"].upper() == acc:
                result.append({"hash": trans["hash"].upper(),
                               "value": int(trans["value"]),
                               "addr": acc,
                               "to": trans["to"].upper(),
                               "raw": json.dumps(trans),
                               "block_height": trans["blockNumber"]})

    return result


def get_normal_fee():
    global ACCESS
    return ACCESS.eth.gas_price


def estimate_fee(*kargs, **kwargs):
    global ACCESS
    gas = ACCESS.eth.gas_price
    return gas*21000


def sweep_address_to(priv, acc, to, amnt, gas=21000):

    global ACCESS
    w3 = ACCESS
    try:
        gasPrice = get_normal_fee()
        key = priv
        nonce = w3.eth.get_transaction_count(acc)
        #print(amnt)
        legacy_transaction = {
            # Note that the address must be in checksum format or native bytes:
            'to': to,
            'value': amnt,
            'gas': gas,
            'gasPrice': gasPrice,
            'nonce': nonce,
            'chainId': 1
        }

        signed = Account.sign_transaction(legacy_transaction, key)
        #print(signed)
        w3.eth.send_raw_transaction(signed["rawTransaction"])
        return {"txid": Web3.to_hex(signed["hash"]),"raw": signed.rawTransaction}
    except:
        traceback.print_exc()
        return False


def generate_address():
    new_addr = Account.create()
    return {"address": new_addr.address, "key":  Web3.to_hex(new_addr.key)}


def get_in_trans_from(
                      acc,
                      blockheight=0):
    resp1 = requests.get(API_HOST + "%s/internalTransactions?page=0&size=20" % acc,
                         headers=def_headers)

    resp2 = requests.get(API_HOST + "%s/wallet" % acc,
                         headers=def_headers)
    acc = acc.upper()
    if verbose:
        print(resp2.text)
        print(resp1.text)

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
                               "value": int(trans["value"]),
                               "addr": acc,
                               "from": trans["from"],
                               "raw": json.dumps(trans),
                               "block_height": trans["blockNumber"]})

    if "accountTransactions" in respj2:
        for trans in respj2["accountTransactions"]:
            if verbose:
                print(trans)

            if "blockNumber" not in trans:
                continue

            if not Decimal(trans["value"]):
                continue

            if trans["state"] != "CONFIRMED" or  not trans["success"]:
                continue

            if int(trans["blockNumber"]) < blockheight:
                continue

            if trans["to"].upper() == acc:
                result.append({"hash": trans["hash"],
                               "value": int(trans["value"]),
                               "addr": acc,
                               "from": trans["from"].upper(),
                               "raw": json.dumps(trans),
                               "block_height": trans["blockNumber"]})

    return result


def get_sum_from(acc, blockheight=0):
    in_trans = get_in_trans_from(acc, blockheight)
    d = 0
    for i in in_trans:
        d = d + i["value"]
    return d / PREC, in_trans


def get_balance(acc, *kargs, **kwargs):
    global ACCESS
    w3 = ACCESS
    return Decimal(w3.eth.get_balance(acc))/PREC

