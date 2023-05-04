import requests


def_headers = {"content-type": "application/json"}
PREC = 10000000


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

        if trans["block_height"]<blockheight:
            continue
        for i2 in trans["inputs"]:
            if i2["addr"] == acc:
                i2["hash"]= trans["hash"]
                result.append(i2)
    return result


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
                result.append(i2)
    return result
                  

def get_sum_from(acc, blockheight=0):
    in_trans = get_in_trans_from(acc, blockheight)
    d = 0
    for i in in_trans:
        d = d + i["value"]
    return d/PREC, in_trans


