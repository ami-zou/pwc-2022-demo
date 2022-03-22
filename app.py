import json
from pathlib import Path
import requests

# Flask dependencies
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

# XRPL Python and helper dependencies
from xrpl.account import get_account_info
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountNFTs
from xrpl.models.transactions import Memo, NFTokenMint
from xrpl.utils import drops_to_xrp, hex_to_str, str_to_hex

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
	return render_template("hello.html")

creds = json.loads(Path("creds.json").read_text())

@app.route("/account")
def account_info():
    client = JsonRpcClient("http://xls20-sandbox.rippletest.net:51234")
    address = creds["address"]
    try:
        result = get_account_info(address, client).result
    except:
        flash("Could not find the account - not a xls20 NFT-Devnet account?")
        return redirect(url_for("index"))

    info = {
        "address": address,
        "minted": result["account_data"].get("MintedTokens", 0),
        "balance_xrp": str(drops_to_xrp(result["account_data"].get("Balance", 0))),
        "balance_drops": result["account_data"].get("Balance", 0),
    }

    result = client.request(AccountNFTs(account=address, limit=150)).result
    print("\n account NFTs")
    print(json.dumps(result, indent=2))

    info["nft_count"] = len(result["account_nfts"])
    nfts = []

    for n in result["account_nfts"]:
        # We could look up offers here, but it's slow - round trip to the ledge for each NFT
        # offers = client.request(NFTSellOffers(tokenid=n["TokenID"])).result
        nfts.append(
            {
                "issuer": n["Issuer"],
                "id": n["TokenID"],
                "fee": n["TransferFee"],
                "uri": hex_to_str(n["URI"]),
                "serial": n["nft_serial"],
            }
        )
    return render_template("account.html", info=info, nfts=nfts)


@app.route("/mint", methods=["GET", "POST"])
def mint():
    if request.method == "GET":
        return render_template("mint_nft.html")
    elif request.json:
        print(request.json)
        return jsonify({"ok": True})
    else:
        # Call the XUM API to have the signing handled there
        memoes = [Memo.from_dict({"memo_data": str_to_hex("Minted by PWC 2022. ")})]
        if "memo" in request.form and request.form["memo"]:
            memoes.append(
                Memo.from_dict({"memo_data": str_to_hex(request.form["memo"])})
            )

        fee = int(request.form["fee"])
        mint_args = {
            "account": creds["address"],
            "flags": 8,
            "uri": str_to_hex(request.form["uri"]),
            "memos": memoes,
            # "transfer_fee": TransferFee.from_percent(int(request.form["fee"])).value, ## Library might be wrong - off by 10x
            "transfer_fee": fee*100,
            "token_taxon": 0,
        }
        print(mint_args)

        mint = NFTokenMint.from_dict(mint_args)
        mint_result_json = mint.to_xrpl()
        
        print(json.dumps(mint_result_json, indent=2))
        
        r = submit_xumm_transaction(mint.to_xrpl())
        xumm_data = r.json()
        print(json.dumps(xumm_data, indent=2))

        return render_template(
            "mint_nft.html",
            qr=xumm_data["refs"]["qr_png"],
            url=xumm_data["next"]["always"],
            ws=xumm_data["refs"]["websocket_status"],
        )

def submit_xumm_transaction(transaction):
    url = "https://xumm.app/api/v1/platform/payload"
    xumm_creds = json.loads(Path("xumm_creds.json").read_text())
    headers = {
        "Accept": "application/json", 
        "Content-Type": "application/json", 
        "X-API-Key":xumm_creds["x-api-key"], 
        "X-API-Secret":xumm_creds["x-api-secret"]
    }

    xumm_payload = {}
    xumm_payload["txjson"] = transaction

    print(headers)
    print(xumm_payload)
    response = requests.request("POST", url, headers=headers, json=xumm_payload)
    response.raise_for_status()
    return response
