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

from web3 import Web3, AsyncWeb3

from eth_account import Account
from web3.middleware import construct_sign_and_send_raw_middleware
TOKEN_TITLE = None
TOKEN_CONTRACT = None
ACCESS = None
API_HOST = "https://api.blockchain.info/v2/eth/data/account/"
def_headers = {"Content-Type": "application/json"}
PREC = 10 ** 6

verbose = True

INFURA_KEY = None
try:
    from private_settings import INFURA_KEY as INF

    INFURA_KEY = INF
except:
    pass

#TODO create singleton class
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


def get_normal_fee( prev_out_index):
    global ACCESS
    return ACCESS.eth.generate_gas_price()


def generate_address():
    new_addr = Account.create()
    return {"address": new_addr.address, "key": Web3.to_hex(new_addr.key)}


def sweep_address_to(private_key, acc, destination, amnt):
    global ACCESS, TOKEN_CONTRACT, ABI
    w3 = ACCESS
    contract = w3.eth.contract(TOKEN_CONTRACT, abi=ABI)
    account = Account.from_key(private_key)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    account = Account.from_key(private_key)
    tx_hash = contract.functions.transfer(destination, amnt).transact({'from': account.address})
    return tx_hash


def setup_title_usdt_token():
    setup_title("usdt", "0xdac17f958d2ee523a2206206994597c13d831ec7")


def setup_title(token_title, token_contract):
    global TOKEN_CONTRACT, TOKEN_TITLE
    TOKEN_CONTRACT = token_contract
    TOKEN_TITLE = token_title
    global ACCESS
    ACCESS = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/%s" % INFURA_KEY))


def get_prec():
    return PREC


def get_current_height():
    global ACCESS
    w3 = ACCESS
    return w3.eth.get_block_number()


def get_out_trans_from(acc, blockheight=0, blockto="latest"):
    global ACCESS
    w3 = ACCESS
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
                               "to": trans["to"],
                               "raw": json.dumps(trans),
                               "block_height": item["blockNumber"]})

    return result


def get_in_trans_from(self, acc, blockheight=0, blockto="latest"):
    global ACCESS
    w3 = ACCESS

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
                               "from": trans["from"],
                               "raw": json.dumps(trans),
                               "block_height": item["blockNumber"]})

    return result


def get_sum_from(acc, blockheight=0, blockto="latest"):
    in_trans = get_in_trans_from(acc, blockheight, blockto)
    d = 0
    for i in in_trans:
        d = d + i["value"]
    return d / PREC, in_trans


def get_native_balance(acc):
    global ACCESS
    w3 = ACCESS

    return Decimal(w3.eth.get_balance(acc)) / PREC


def get_balance(acc):
    global verbose
    url = API_HOST + "%s/tokenAccounts" % acc
    resp = requests.get(url, headers=def_headers)
    if resp.status_code == 404:
        return Decimal("0.0")

    if resp.status_code != 200:
        raise Exception(resp.text)

    if verbose:
        print(url)
        print(resp.text)

    respj = resp.json()

    if not "tokenAccounts" in respj:
        raise Exception(resp.text)

    for i in respj["tokenAccounts"]:
        if i["tokenHash"] == TOKEN_CONTRACT:
            return Decimal(i["balance"])/Decimal(10 ** i["decimals"])

    return Decimal("0.0")
