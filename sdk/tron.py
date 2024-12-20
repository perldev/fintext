from tronpy import Tron
from tronpy.tron import Transaction
from tronpy.keys import PrivateKey
import json
import requests
from Crypto.Hash import keccak
import hashlib
import base58
import base64
from decimal import Decimal
import tronpy.providers.http
import traceback

ACCESS = None


API_KEY = None
try:
    from private_settings import TRONKEY
    API_KEY = TRONKEY
except:
    pass


API_URL_BASE = 'https://api.trongrid.io/'
# API_URL_BASE = 'https://api.shasta.trongrid.io/'
# API_URL_BASE = 'https://api.nileex.io/'

# 70a08231: balanceOf(address)
METHOD_BALANCE_OF = 'balanceOf(address)'

# a9059cbb: transfer(address,uint256)
METHOD_TRANSFER = 'transfer(address,uint256)'

DEFAULT_FEE_LIMIT = 1_000_000  # 1 TRX

PREC = 1_000_000
verbose = True


def address_to_parameter(addr):
    return "0" * 24 + base58.b58decode_check(addr)[1:].hex()


def amount_to_parameter(amount):
    return '%064x' % amount

TOKEN_CONTRACT = None
PREC = 1000000
ACCESS = None
CONTRACT = None


def keccak256(data: bytes) -> bytes:
    hasher = keccak.new(digest_bits=256)
    hasher.update(data)
    return hasher.digest()


def setup_title_usdt_token():
    setup_title("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")


def setup_title(token_contract):
    global TOKEN_CONTRACT, ACCESS
    TOKEN_CONTRACT = token_contract
    # HACK install my api key
    ACCESS = CryptoAccountTron(contract=TOKEN_CONTRACT)
    return True


def get_current_height():
    global ACCESS
    resp = ACCESS.getblock()
    return resp["block_header"]["raw_data"]["timestamp"]


def sweep_address_to(priv, acc, to, amnt):
    return ACCESS.transfer_of_contract(acc, to, amnt,  private_key=priv)


def generate_address():
    resp = ACCESS.getnewaddress()
    resp["address"] = resp["base58check_address"]
    resp["key"] = resp["private_key"]
    return resp


def get_out_trans_from(acc, blockheight=0, blockto="latest"):
    global ACCESS, TOKEN_CONTRACT
    if blockto == "latest":
        blockto = get_current_height()

    else:
        blockto = "0x%0.2X" % blockto

    resp = ACCESS.get_trc20_trasactions4account(TOKEN_CONTRACT, acc)
    result = []
    for trans in resp["data"]:
        if trans["from"] == acc:

            if int(trans["block_timestamp"]) < blockheight:
                continue

            result.append({"hash": trans["transaction_id"],
                            "value": int(trans["value"]),
                            "addr": acc,
                           "to": trans["to"],
                           "raw": json.dumps(trans),
                            "block_height": trans["block_timestamp"]})

    return result


def sendtoaddress(priv, acc, to, amnt):
    return ACCESS.sendtoaddress(acc, to, amnt,  private_key=priv)


def get_in_trans_from(acc, blockheight=0, blockto="latest"):
    global ACCESS, TOKEN_CONTRACT, verbose
    if blockto == "latest":
        blockto = get_current_height()

    else:
        blockto = "0x%0.2X" % blockto

    resp = ACCESS.get_trc20_trasactions4account(TOKEN_CONTRACT, acc)
    result = []
    if verbose:
        print(resp)

    for trans in resp["data"]:
        if trans["to"] == acc:

            if int(trans["block_timestamp"]) < blockheight:
                continue

            result.append({"hash": trans["transaction_id"],
                           "value": int(trans["value"]),
                           "addr": acc,
                           "from": trans["from"],
                           "raw": json.dumps(trans),
                           "block_height": trans["block_timestamp"]})

    return result


def get_sum_from(acc, blockheight=0, blockto="latest"):
    in_trans = get_in_trans_from(acc, blockheight, blockto)
    d = 0
    for i in in_trans:
        d = d + i["value"]
    return d / PREC, in_trans


def get_prec():
    return PREC


def get_native_balance(acc):
    global ACCESS
    return ACCESS.getbalance(acc)

def get_balance(acc):
    global ACCESS
    return ACCESS.get_trc20_balance(TOKEN_CONTRACT, acc)


class CryptoAccountTron(object):

    def __init__(self, contract=None, wallet=None):
        currency = "TRX"
        self.__currency = currency
        self.__wallet = None
        self.__contract = contract
        tronpy.providers.http.DEFAULT_API_KEYS = [API_KEY]
        self.__access = Tron(network='mainnet')
        if not contract is None:
            self.__contract = self.get_contract(contract)



    def walletpassphrase(self, time=20):
        raise Exception("not Implemented")

    def keypoolrefill(self, size=None):
        raise Exception("not Implemented")

    def listaccounts(self):
        raise Exception("not Implemented")

    def getrawmempool(self):
        raise Exception("not Implemented")

    def getrawtransaction(self, txid):
        raise Exception("not Implemented")

    def gettransaction(self, txid: str) -> dict:
        return self.__access.get_transaction(txid)

    def decoderawtransaction(self, hex_data):
        raise Exception("not Implemented")

    def listaddressgroupings(self):
        raise Exception("not Implemented")

    def validateaddress(self, address):
        raise Exception("not Implemented")

    def settxfee(self, amnt):
        self.limit_fee = amnt
        return True

    def listsinceblock(self, hashblcok):
        raise Exception("not Implemented")

    def getblockcount(self):
        b = self.__access.get_latest_solid_block()
        return b["block_header"]["raw_data"]["number"]

    def getblockhash(self, hs):
        raise Exception("not Implemented")

    def getblock(self, hs=None):
        if hs is None:
            return self.__access.get_latest_block()
        else:
            return self.__access.get_block(hs)

    def walletlock(self):
        raise Exception("not Implemented")

    def dumpwallet(self, filename):
        raise Exception("not Implemented")

    def backupwallet(self, filename):
        if self.__wallet is None:
            raise Exception("no wallet")

    def createrawtransaction(self, from_acc, addr, amnt, memo="", comis=1000000):

        txn = (self.__access.trx.transfer(from_acc, addr, amnt)
               .memo(memo)
               .build()
               )
        return txn

    def dumpprivkey(self, Addr):
        raise Exception("not Implemented")

    def getinfo(self):
        return self.__access.get_node_info()

    def getbalance(self, address=None):
        try:
            if address is None:
                return str(self.__access.get_account_balance(self.__acc))
            else:
                return str(self.__access.get_account_balance(address))
        except tronpy.exceptions.AddressNotFound:
            return str("0")


    def load_contract_default(self, contract_address):
        cntr = self.__access.get_contract(contract_address)
        print(dir(cntr.functions))
        self.__contract = cntr
        return True

    def unload_contract_default(self):
        self.__contract = None
        return True

    def get_contract(self, contract_address):
        cntr = self.__access.get_contract(contract_address)
        return cntr

    def balanceOf_on_contract(self, addr, contract=None):
        if contract is None:
            contract = self.__contract

        precision = contract.functions.decimals()
        return contract.functions.balanceOf(addr) / (10 ** precision)

    def transfer_of_contract(self, from_addr, to_addr, amnt,  private_key=None):
            contract = self.__contract
            if self.__wallet is None and private_key is None:
                raise Exception("private key is needed")
            if private_key is None:
                data = self.__wallet.filter(address=from_addr)
                private_key  = data.private

            priv_key = PrivateKey(bytes.fromhex(private_key))

            txn = (
                contract.functions.transfer(to_addr, amnt)
                .with_owner(from_addr)  # address of the private key
                .fee_limit(100 * PREC)
                .build()
                .sign(priv_key)
                .broadcast()
            )
            return txn["txid"]

    def addr2base58(self, pub):
        primitive_addr = b"\x41" + keccak256(pub)[-20:]
        addr = base58.b58encode_check(primitive_addr)
        return {"result": addr.decode()}

    def getnewaddress(self):
        """Generate a random address."""
        priv = PrivateKey.random()
        resp = {
            "base58check_address": priv.public_key.to_base58check_address(),
            "hex_address": priv.public_key.to_hex_address(),
            "private_key": priv.hex(),
            "public_key": priv.public_key.hex(),
        }

        if self.__wallet is not None:
            self.__wallet.insert(
                address=priv.public_key.to_base58check_address(),
                private=priv.hex(),
                raw=json.dumps(resp))
        return resp

    def listunspent(self):
        raise Exception("not Implemented")

    def sendmany(self, to_addr):
        raise Exception("not Implemented")

    def listtransactions(self):
        raise Exception("not Implemented")

    def get_trc20_balance(self, CONTRACT, address):
        ADDRESS = address
        url = API_URL_BASE + 'wallet/triggerconstantcontract'
        payload = {
            'owner_address': base58.b58decode_check(ADDRESS).hex(),
            'contract_address': base58.b58decode_check(CONTRACT).hex(),
            'function_selector': METHOD_BALANCE_OF,
            'parameter': address_to_parameter(address),
        }
        resp = requests.post(url, json=payload)
        data = resp.json()

        if data['result'].get('result', None):
            print(data['constant_result'])
            val = data['constant_result'][0]
            return int(val, 16)

        else:
            print('error:', bytes.fromhex(data['result']['message']).decode())

    def get_trc20_trasactions4account(self, CONTRACT, ADDRESS, from_timestamp=0):
        #  https://api.trongrid.io/v1/accounts/TKhVAgZQXrWiFJU4qES2eZ6fhwDVW7ZKAo/transactions/trc20?limit=100&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&only_confirmed=true
        url = API_URL_BASE + "v1/accounts/%s/transactions/trc20?limit=100&contract_address=%s&only_confirmed=true&&only_to=true&min_timestamp=%s" % (
        ADDRESS, CONTRACT, from_timestamp)
        print(url)
        resp = requests.get(url)
        return resp.json()

    def create_trc20_transaction(self, CONTRACT, ADDRESS, to, amount, memo=""):
        url = API_URL_BASE + 'wallet/triggersmartcontract'
        payload = {
            'owner_address': base58.b58decode_check(ADDRESS).hex(),
            'contract_address': base58.b58decode_check(CONTRACT).hex(),
            'function_selector': METHOD_TRANSFER,
            'parameter': address_to_parameter(to) + amount_to_parameter(amount),
            "fee_limit": DEFAULT_FEE_LIMIT,
            'extra_data': base64.b64encode(memo.encode()).decode(),  # TODO: not supported yet
        }
        resp = requests.post(url, json=payload)
        data = resp.json()

        if data['result'].get('result', None):
            transaction = data['transaction']
            return transaction

        else:
            print('error:', bytes.fromhex(data['result']['message']).decode())
            raise RuntimeError


    # Amount of TRX (in SUN) to stake.	Integer
    # duration	Length in Days to stake TRX for. Minimum of 3 days.	Integer
    # resource	Resource that you're staking TRX in order to obtain. Must be either "BANDWIDTH" or "ENERGY".	String
    # ownerAddress (optional)	Address of the owner of the TRX to be staked (defaults to caller's default address).
    def freezeBalance(self, amnt, ownerAdress, duration=3, resources="ENERGY", receive_adress=None):
        data = self.__wallet.filter(address=ownerAdress)
        priv_key = PrivateKey(bytes.fromhex(data.private))
        txn = None
        trx = self.__access.trx
        txn = (trx.freeze_balance(ownerAdress, amnt, resources, receiver=receive_adress)
               .fee_limit(DEFAULT_FEE_LIMIT)
               .build()
               .sign(priv_key)
               .broadcast()
               )
        return txn

    def sendtoaddress(self, from_acc, addr, amnt, private=None, memo="", fee_limit=100):
        if self.__wallet is None and private is None:
            raise Exception("cant't send without wallet")

        if  self.__wallet is not None:
            data = self.__wallet.filter(address=from_acc)
            private = data.private

        priv_key = PrivateKey(bytes.fromhex(data.private))
        txn = (self.__access.trx.transfer(from_acc, addr, amnt)
               .memo(memo)
               .fee_limit(fee_limit * PREC)
               .build()
               .inspect()
               .sign(priv_key)
               .broadcast()
               )
        return txn

    def sendto(self, to_addr, amnt, minconf=3, comment=None):
        raise Exception("not Implemented")

    def getaccount(self, addr):
        raise Exception("not Implemented")

    def setaccount(self, addr, acc):
        raise Exception("not Implemented")

    def getaddressinfo(self, addr):
        raise Exception("not Implemented")

    def access(self):
        return self.__access





