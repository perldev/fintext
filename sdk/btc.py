import traceback

from bitcoinutils.setup import setup
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import SIGHASH_ALL, SIGHASH_NONE, SIGHASH_SINGLE, SIGHASH_ANYONECANPAY


import requests
import json
from json import load

def_headers = {"content-type": "application/json"}
PREC = 10000000


def get_prec():
    return PREC

def get_current_height():
    resp = requests.get("https://blockchain.info/latestblock", headers=def_headers)
    respj = resp.json()
    return respj["height"]


def get_out_trans_from(acc, blockheight=0):
    resp = requests.get("https://blockchain.info/rawaddr/%s" % acc, headers=def_headers)
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
                i2["block_height"] = trans["block_height"]
                result.append(i2)
    return result


def generate_address():
    setup('mainnet')
    # create a private key (deterministically)
    priv = PrivateKey()
    # compressed is the default
    priv_wif = priv.to_wif(compressed=True)

    pub = priv.get_public_key()
    # compressed is the default
    address = pub.get_address()
    # print the address and hash160 - default is compressed address

    return {"key": priv_wif,
            "address": address.to_string(),
            "hash160": address.to_hash160()}


# TODO calculate this more accurate
def get_normal_fee( prev_out_index):
    return 230 * 240


def sweep_address_to(wif_priv, acc, destination):
    try:
        resp = requests.get("https://blockchain.info/unspent?active=%s" % acc, headers=def_headers)
        respj = resp.json()
        prev_tx_id, prev_out_index, amnt = [],[], 0
        inputs = []
        for item in respj["unspent_outputs"]:
            inputs.append(TxInput(TxInput(item["tx_hash"], item["tx_output_n"])))
            amnt = amnt + item["value"]

        addr = P2pkhAddress(destination)
        myfee = get_normal_fee(prev_out_index)
        amnt2send = amnt - myfee
        txout = TxOutput(amnt2send, Script(['OP_DUP', 'OP_HASH160', addr.to_hash160(),
                                                   'OP_EQUALVERIFY', 'OP_CHECKSIG']))

        tx = Transaction(inputs, [txout])
        sk = PrivateKey(wif_priv)

        from_addr = P2pkhAddress(acc)
        sig = sk.sign_input(tx, 0, Script(['OP_DUP', 'OP_HASH160',
                                           from_addr.to_hash160(), 'OP_EQUALVERIFY',
                                           'OP_CHECKSIG']),
                            SIGHASH_ALL | SIGHASH_ANYONECANPAY)

        # get public key as hex
        pk = sk.get_public_key()
        pk = pk.to_hex()
        txin = inputs[0]
        # set the scriptSig (unlocking script)
        txin.script_sig = Script([sig, pk])
        signed_tx = tx.serialize()
        resp_push = requests.post("https://blockchain.info/pushtx", data={"tx": signed_tx})
        if resp_push.status_code != 200:
            raise Exception("Cannot send")

        return tx.get_txid()
    except:
        traceback.print_exc()
        return False


def get_in_trans_from(acc, blockheight=0):
    resp = requests.get("https://blockchain.info/rawaddr/%s" % acc, headers=def_headers)
    respj = resp.json()
    result = []
    for trans in respj["txs"]:
        if not trans["block_height"]:
            continue

        if trans["block_height"]<blockheight:
            continue
        for i2 in trans["out"]:
            if i2["addr"] == acc:
                i2["hash"] = trans["hash"]
                i2["block_height"] = trans["block_height"]
                result.append(i2)
    return result
                  

def get_sum_from(acc, blockheight=0):
    in_trans = get_in_trans_from(acc, blockheight)
    d = 0
    for i in in_trans:
        d = d + i["value"]
    return d/PREC, in_trans


def get_balance(acc):
    resp = requests.get("https://blockchain.info/balance?active=%s" % acc, headers=def_headers)
    respj = resp.json()
    return respj[acc]["final_balance"]