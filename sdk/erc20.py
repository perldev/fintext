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

TOKEN_TITLE = None
TOKEN_CONTRACT = None

API_HOST = "https://api.blockchain.info/v2/eth/data/account/"
def_headers = {"Content-Type": "application/json"}
PREC = 10 ** 6

INFURA_KEY = None
try:
    from private_settings import INFURA_KEY as INF

    INFURA_KEY = INF
except:
    pass

#TODO create singleton class
w3 = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/%s" % INFURA_KEY))
ABI = [
    # Transfer event
    {
        "name": "Transfer",
        "type": "event",
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address",
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address",
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256",
            },
        ],
    },
]
def setup_title(token_title, token_contract):
    global TOKEN_CONTRACT, TOKEN_TITLE
    TOKEN_CONTRACT = token_contract
    TOKEN_TITLE = token_title


def get_current_height():
    global w3
    return w3.eth.get_block_number()


def get_out_trans_from(acc, blockheight=0, blockto="latest"):
    global w3
    if blockto == "latest":

        blockto = get_current_height()

    else:
        blockto = "0x%0.2X" % blockto

    contract = w3.eth.contract(TOKEN_CONTRACT, abi=ABI)
    first_block = blockheight
    for i in range(blockheight+1, blockto+1):
        fromb = "0x%0.2X" % first_block
        tob = "0x%0.2X" % first_block + 1
        first_block = i
        events = contract.events.Transfer.getLogs(fromBlock=fromb, toBlock=tob)
        result = []
        for item in events:
            trans = item["args"]
            if trans["from"] == acc:
                result.append({"hash": item["transactionHash"],
                               "value": trans["value"],
                               "addr": acc,
                               "block_height": item["blockNumber"]})

    return result


def get_in_trans_from(self, acc, blockheight=0, blockto="latest"):
    global w3
    if blockto == "latest":

        blockto = get_current_height()

    else:
        blockto = "0x%0.2X" % blockto

    contract = w3.eth.contract(TOKEN_CONTRACT, abi=ABI)
    first_block = blockheight
    for i in range(blockheight + 1, blockto + 1):
        fromb = "0x%0.2X" % first_block
        tob = "0x%0.2X" % first_block + 1
        first_block = i
        events = contract.events.Transfer.getLogs(fromBlock=fromb, toBlock=tob)
        result = []
        for item in events:
            trans = item["args"]
            if trans["to"] == acc:
                result.append({"hash": item["transactionHash"],
                               "value": trans["value"],
                               "addr": acc,
                               "block_height": item["blockNumber"]})

    return result

def get_sum_from(acc, blockheight=0, blockto="latest"):
    in_trans = get_in_trans_from(acc, blockheight, blockto)
    d = 0
    for i in in_trans:
        d = d + i["value"]
    return d / PREC, in_trans


def get_balance(acc):

    resp = requests.get(API_HOST + "%s/tokenAccounts" % acc,
                        headers=def_headers)

    respj = resp.json()
    if not "tokenAccounts" in respj:
        raise Exception(resp.text)

    for i in respj["tokenAccounts"]:
        if i["tokenHash"] == TOKEN_CONTRACT:
            return Decimal(i["balance"])/Decimal(10 ** i["decimals"])

    return Decimal("0.0")
