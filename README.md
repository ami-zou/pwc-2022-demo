# pwc-2022-demo
Python Web Conference 2022 [NFT Talk Demo](https://2022.pythonwebconf.com/presentations/stop-burning-down-rainforests-how-to-mint-nfts-using-python-and-the-xrp-ledger)

## Overview
This simple Flask app allows you to create and mint an NFT directly on XRPL NFT-devnet, and the transaction is signed by XUMM. It also shows you account info and minted NFT details. [Here](https://github.com/ami-zou/pwc-2022-demo/blob/main/demo.gif) is a quick demo gif.

## Pre-requisites 
### XUMM App NFT-devnet node
This app uses XUMM, a non-custodial wallet, for signing the transaction. Native NFT support on XRPL, [XLS-20d](https://github.com/XRPLF/XRPL-Standards/discussions/46), is still in development and is only available on NFT-devnet at the moment (intended release on mainnet/sidechain is June 2022). To access NFT-devnet via XUMM, you'll have to add a customized node. Please scan this [QR code](https://nnwqrfc.dlvr.cloud/XLS20-QR.png) using XUMM app (scanning it directly with Camera app doesn't work) to add NFT-devnet to your XUMM. Then in `Settings > Advanced > Node` you can switch it to `xls20-sandbox.rippletest.net:51233` (NFT-devnet). It is recommended to also turn on `Develper mode`


### XUMM App integration
To integrate with XUMM, you will need to [register an XAPP](https://xumm.readme.io/docs/register-your-app). Please save the XUMM api key and secret into a file called `xumm_creds.json` :
```
{
    "x-api-key": {XUMM api key},
    "x-api-secret": {XUMM api-secret}
}
```

### NFT-Devnet address
To test the transaction, you will also need to [create an account on NFT-devnet](https://xrpl.org/xrp-testnet-faucet.html). Please select `Generate NFT-devnet credentials` and save the address in a file called `creds.json`:
```
{
    "address": {address}
}
```
Then import this account (using its seed/secret) to XUMM. Make sure XUMM is switched to the `NFT-devnet` node, otherwise it would give you an error saying the account is not activated.

## Running the app
1. Start a virtual environment using venv: `$python3 -m venv venv`
2. Activate the virtual env: `$source venv/bin/activate`
3. Install dependencies: `$python -m pip install -r requirements.txt`
4. Start the server: `$flask run`

## Using the app

`/` endpoint returns a simple Hello World response

`/mint` page allows you to input the NFT information for minting; Once `submit` button is hit, it will redirect you to a QR code with the transaction details. Open your XUMM app to scan that transaction, and you will be redirected to the `/account` page for more info on the transaction

`/account` page has the details of the account including balance, and account NFT details
