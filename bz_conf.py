#!/usr/bin/python

import os
import sys
import asyncio
import ccxt.async as ccxt


db_dir = os.getcwd() + '/db/'
#db_dir = './db/'


acx = ccxt.acx({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
allcoin = ccxt.allcoin({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
anxpro = ccxt.anxpro({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bibox = ccxt.bibox({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
binance = ccxt.binance({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bit2c = ccxt.bit2c({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitbay = ccxt.bitbay({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitcoincoid = ccxt.bitcoincoid({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitfinex = ccxt.bitfinex({
    'enableRateLimit': True,
    'rateLimit': 10000,
#    'apiKey': "4FlEDtxDl35gdEiobnfZ72vJeZteE4Bb7JdvqzjIjHq",
#    'secret': "D4DXM8DZdHuAq9YptUsb42aWT1XBnGlIJgLi8a7tzFH",
})
bitfinex2 = ccxt.bitfinex2({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitflyer = ccxt.bitflyer({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bithumb = ccxt.bithumb({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitlish = ccxt.bitlish({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitmarket = ccxt.bitmarket({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitmex = ccxt.bitmex({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitso = ccxt.bitso({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitstamp = ccxt.bitstamp({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bitstamp1 = ccxt.bitstamp1({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bittrex = ccxt.bittrex({
    'enableRateLimit': True,
    'rateLimit': 10000,
#    'apiKey': "c5af1d0ceeaa4729ad87da1b05d9dfc3",
#    'secret': "d055d8e47fdf4c3bbd0ec6c289ea8ffd",
})
bitz = ccxt.bitz({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bl3p = ccxt.bl3p({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bleutrade = ccxt.bleutrade({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
braziliex = ccxt.braziliex({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
btcbox = ccxt.btcbox({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
btcchina = ccxt.btcchina({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
btcexchange = ccxt.btcexchange({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
btcmarkets = ccxt.btcmarkets({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
btctradeua = ccxt.btctradeua({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
btcturk = ccxt.btcturk({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
btcx = ccxt.btcx({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
bxinth = ccxt.bxinth()
ccex = ccxt.ccex({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
cex = ccxt.cex({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
chbtc = ccxt.chbtc()
chilebit = ccxt.chilebit()
cobinhood = ccxt.cobinhood()
coincheck = ccxt.coincheck()
coinexchange = ccxt.coinexchange()
coinfloor = ccxt.coinfloor()
coingi = ccxt.coingi()
coinmarketcap = ccxt.coinmarketcap()
coinmate = ccxt.coinmate()
coinsecure = ccxt.coinsecure()
coinspot = ccxt.coinspot()
cryptopia = ccxt.cryptopia()
dsx = ccxt.dsx()
exmo = ccxt.exmo()
flowbtc = ccxt.flowbtc()
foxbit = ccxt.foxbit()
fybse = ccxt.fybse()
fybsg = ccxt.fybsg()
gatecoin = ccxt.gatecoin()
gateio = ccxt.gateio()
gdax = ccxt.gdax({
    'enableRateLimit': True,
    'rateLimit': 10000,
#    'apiKey': "a43edfe629bc5991acc83a536ac6358e",
#    'secret': "xOvq+iH8NT07TheFB/fmY3GcnMZMwP7Xct9zwWtAZxsCbJh8rxeEe/0BGxfbV2em7P9iqQD7/TJGqmsDO8B/kw==",
#    'password': 'zdmj8o7byla',
})
gemini = ccxt.gemini({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
getbtc = ccxt.getbtc({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
hitbtc = ccxt.hitbtc({
    'enableRateLimit': True,
    'rateLimit': 10000,
    "apiKey": "00c576eec474fab35709aeb546dcf577",
    "secret": "568e6d454ea9897b183c4ba2ff4bf598",
})
hitbtc2 = ccxt.hitbtc2({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
huobi = ccxt.huobi({
    'enableRateLimit': True,
    'rateLimit': 10000,
    #"apiKey": "",
    #"secret": "",
})
huobicny = ccxt.huobicny({
    'enableRateLimit': True,
    'rateLimit': 10000,
    #"apiKey": "",
    #"secret": "",
})
huobipro = ccxt.huobipro({
    'enableRateLimit': True,
    'rateLimit': 10000,
    #"apiKey": "",
    #"secret": "",
})
independentreserve = ccxt.independentreserve({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
itbit = ccxt.itbit({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
jubi = ccxt.jubi({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
kraken = ccxt.kraken({
    'enableRateLimit': True,
    'rateLimit': 10000,
#    'apiKey': "hEvQNMDIeoCJbr7W/ZBb5CGOrx3G0lWF5B3zqa1JBxdZlEaL8EK+D0Mw",
#    'secret': "JaE9wI6Nwgh5oRxiHcVxurwzwBxwc05W/qv/k1srGg4s3EYuXPpNkLLM5NYbbWpM8rCyijIeDavRuqWbU0ZV9A==",
})
kucoin = ccxt.kucoin({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
kuna = ccxt.kuna({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
lakebtc = ccxt.lakebtc({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
liqui = ccxt.liqui({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
livecoin = ccxt.livecoin({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
luno = ccxt.luno({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
lykke = ccxt.lykke({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
mercado = ccxt.mercado({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
mixcoins = ccxt.mixcoins({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
nova = ccxt.nova({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
okcoincny = ccxt.okcoincny({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
okcoinusd = ccxt.okcoinusd({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
okex = ccxt.okex({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
paymium = ccxt.paymium()
poloniex = ccxt.poloniex({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
qryptos = ccxt.qryptos()
quadrigacx = ccxt.quadrigacx()
quoinex = ccxt.quoinex()
southxchange = ccxt.southxchange()
surbitcoin = ccxt.surbitcoin()
therock = ccxt.therock()
tidex = ccxt.tidex()
urdubit = ccxt.urdubit()
vaultoro = ccxt.vaultoro()
vbtc = ccxt.vbtc()
virwox = ccxt.virwox()
wex = ccxt.wex({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
xbtce = ccxt.xbtce({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
yobit = ccxt.yobit({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
yunbi = ccxt.yunbi({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
zaif = ccxt.zaif({
    'enableRateLimit': True,
    'rateLimit': 10000,
})
zb = ccxt.zb({
    'enableRateLimit': True,
    'rateLimit': 10000,
})


