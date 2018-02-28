#!/usr/bin/python

import os
import sys
import asyncio
import ccxt.async as ccxt



root_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = root_dir + '/db/'
log_dir = root_dir + '/logs/'



acx = ccxt.acx({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
allcoin = ccxt.allcoin({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
anxpro = ccxt.anxpro({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bibox = ccxt.bibox({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
binance = ccxt.binance({
    'enableRateLimit': True,
    'rateLimit': 1000,
    'apiKey': "kHgviPR8ijyNWn0PcltvzWkOqpr3nlDzGp6wY2ZEsQNa1F7k3ePhV0C7oOq8e6Cu",
    'secret': "aqdBURqQxxk29mE31mEMIpW6zI5QsA5PKw1wf8VI7XDGG1WxJrAFWkTwEnMOJQbB",
    #'verbose': True,
})
bit2c = ccxt.bit2c({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitbay = ccxt.bitbay({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitcoincoid = ccxt.bitcoincoid({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitfinex = ccxt.bitfinex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitfinex2 = ccxt.bitfinex2({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitflyer = ccxt.bitflyer({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bithumb = ccxt.bithumb({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitlish = ccxt.bitlish({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitmarket = ccxt.bitmarket({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitmex = ccxt.bitmex({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "DPBrxuhRdVaBEUNiNaAlJOrw",
    "secret": "spMNDyhaRhEtCyQTGPSMKOwW9YIM8LYV0daWOm4ZiNSleRew",
})
bitso = ccxt.bitso({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitstamp = ccxt.bitstamp({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitstamp1 = ccxt.bitstamp1({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bittrex = ccxt.bittrex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bitz = ccxt.bitz({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "c1cf93a1182e5a38bb8a8c3458310396",
    "secret": "a7a55512ee789d6519fd005345644133",
})
bl3p = ccxt.bl3p({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bleutrade = ccxt.bleutrade({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
braziliex = ccxt.braziliex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
btcbox = ccxt.btcbox({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
btcchina = ccxt.btcchina({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
btcexchange = ccxt.btcexchange({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
btcmarkets = ccxt.btcmarkets({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
btctradeua = ccxt.btctradeua({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
btcturk = ccxt.btcturk({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
btcx = ccxt.btcx({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
bxinth = ccxt.bxinth({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
ccex = ccxt.ccex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
cex = ccxt.cex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
chbtc = ccxt.chbtc({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
chilebit = ccxt.chilebit({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
cobinhood = ccxt.cobinhood({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coincheck = ccxt.coincheck({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coinexchange = ccxt.coinexchange({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coinfloor = ccxt.coinfloor({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coingi = ccxt.coingi({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coinmarketcap = ccxt.coinmarketcap({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coinmate = ccxt.coinmate({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coinsecure = ccxt.coinsecure({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
coinspot = ccxt.coinspot({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
cryptopia = ccxt.cryptopia({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
dsx = ccxt.dsx({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
exmo = ccxt.exmo({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
flowbtc = ccxt.flowbtc({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
foxbit = ccxt.foxbit({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
fybse = ccxt.fybse({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
fybsg = ccxt.fybsg({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
gatecoin = ccxt.gatecoin({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
gateio = ccxt.gateio({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
gdax = ccxt.gdax({
    'enableRateLimit': True,
    'rateLimit': 1000,
    'apiKey': "GnFmvkkPinzOXSWM",
    'secret': "",
    'password': 'zdmj8o7byla',
})
gemini = ccxt.gemini({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
getbtc = ccxt.getbtc({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
hitbtc = ccxt.hitbtc({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "00c576eec474fab35709aeb546dcf577",
    "secret": "568e6d454ea9897b183c4ba2ff4bf598",
})
hitbtc2 = ccxt.hitbtc2({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "00c576eec474fab35709aeb546dcf577",
    "secret": "568e6d454ea9897b183c4ba2ff4bf598",
})
huobi = ccxt.huobi({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "a3a1ee7f-2e64f1bb-925f3e37-3fe72",
    "secret": "05c371ab-0d9d012f-39d3f12d-a6c68",
})
huobicny = ccxt.huobicny({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "a3a1ee7f-2e64f1bb-925f3e37-3fe72",
    "secret": "05c371ab-0d9d012f-39d3f12d-a6c68",
})
huobipro = ccxt.huobipro({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "a3a1ee7f-2e64f1bb-925f3e37-3fe72",
    "secret": "05c371ab-0d9d012f-39d3f12d-a6c68",
})
independentreserve = ccxt.independentreserve({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
itbit = ccxt.itbit({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
jubi = ccxt.jubi({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
kraken = ccxt.kraken({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
kucoin = ccxt.kucoin({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "5a92a5e003d644701f1a9c56",
    "secret": "400e8874-e3cf-43f1-8765-63e4b7f535a5",
})
kuna = ccxt.kuna({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
lakebtc = ccxt.lakebtc({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
liqui = ccxt.liqui({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
livecoin = ccxt.livecoin({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
luno = ccxt.luno({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
lykke = ccxt.lykke({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
mercado = ccxt.mercado({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
mixcoins = ccxt.mixcoins({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
nova = ccxt.nova({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
okcoincny = ccxt.okcoincny({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "63f1b985-88fe-48c1-bb91-2f6f1f086ce5",
    "secret": "896AE910647BB0911BDF27949508E065",
})
okcoinusd = ccxt.okcoinusd({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "63f1b985-88fe-48c1-bb91-2f6f1f086ce5",
    "secret": "896AE910647BB0911BDF27949508E065",
})
okex = ccxt.okex({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "7f10be5e-afd4-41a9-9c3c-fa9602996447",
    "secret": "71B22F85C687D223954FE4432B2A61B9",
})
paymium = ccxt.paymium()
poloniex = ccxt.poloniex({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "OQDZM5YM-OKX5QEUE-Z3IDJZG2-NEHLDQKS",
    "secret": "b36baf9613ab1fec64c549c2472e7b7c2b63b4f16667feb576a0601331fdd24bb1b22dda3c867e89b7beb5b2854cf66b6f2cd011d1adb8634ddeb3f7310337e1",
})
qryptos = ccxt.qryptos({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
quadrigacx = ccxt.quadrigacx({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
quoinex = ccxt.quoinex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
southxchange = ccxt.southxchange({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
surbitcoin = ccxt.surbitcoin({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
therock = ccxt.therock({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
tidex = ccxt.tidex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
urdubit = ccxt.urdubit({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
vaultoro = ccxt.vaultoro({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
vbtc = ccxt.vbtc({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
virwox = ccxt.virwox({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
wex = ccxt.wex({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
xbtce = ccxt.xbtce({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
yobit = ccxt.yobit({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
yunbi = ccxt.yunbi({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
zaif = ccxt.zaif({
    'enableRateLimit': True,
    'rateLimit': 1000,
})
zb = ccxt.zb({
    'enableRateLimit': True,
    'rateLimit': 1000,
    "apiKey": "a6fad7d3-3830-400d-8326-b1f8b3fb68ec",
    "secret": "1c5f5e7e-1c37-4cac-9bd3-029292da681a",
})

