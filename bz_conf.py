#!/usr/bin/python

import os
import sys
import asyncio
import ccxt.async as ccxt


exchanges_btc_usd = {
    'bitfinex': True,
    'okcoinusd': True,
    'bitstamp': True,
    'gemini': True,
    'kraken': True,
    'exmo': True,
    'quadrigacx': True,
    'gdax': True,
    'poloniex': False,
    'CEX.IO': False,
    'WEX': False,
    'itBit': False,
    'Bittrex': False,
    'Binance': False,
}

exchanges_btc_cny = {
    'bitfinex': False,
    'okcoinusd': True,
    'bitstamp': False,
    'gemini': False,
    'kraken': False,
    'exmo': False,
    'quadrigacx': False,
    'gdax': False,
    'huobipro': False,
    'poloniex': False,
    'CEX.IO': False,
    'WEX': False,
    'itBit': False,
    'Bittrex': False,
    'Binance': False,
}

exchanges_eth_btc = {
    'bitfinex': True,
    'okcoinusd': True,
    'bitstamp': True,
    'gemini': True,
    'kraken': True,
    'exmo': True,
    'quadrigacx': True,
    'gdax': True,
    'huobipro': True,
    'poloniex': False,
    'CEX.IO': False,
    'WEX': False,
    'itBit': False,
    'Bittrex': False,
    'Binance': False,
}



_1broker = ccxt._1broker()
_1btcxe = ccxt._1btcxe()
acx = ccxt.acx()
allcoin = ccxt.allcoin()
anxpro = ccxt.anxpro()
bibox = ccxt.bibox()
binance = ccxt.binance()
bit2c = ccxt.bit2c()
bitbay = ccxt.bitbay()
bitcoincoid = ccxt.bitcoincoid()
bitfinex = ccxt.bitfinex()
#bitfinex = ccxt.bitfinex({
#    'apiKey': "4FlEDtxDl35gdEiobnfZ72vJeZteE4Bb7JdvqzjIjHq",
#    'secret': "D4DXM8DZdHuAq9YptUsb42aWT1XBnGlIJgLi8a7tzFH",
#s})
bitfinex2 = ccxt.bitfinex2()
bitflyer = ccxt.bitflyer()
bithumb = ccxt.bithumb()
bitlish = ccxt.bitlish()
bitmarket = ccxt.bitmarket()
bitmex = ccxt.bitmex()
bitso = ccxt.bitso()
bitstamp = ccxt.bitstamp()
bitstamp1 = ccxt.bitstamp1()
bittrex = ccxt.bittrex()
#bittrex = ccxt.bittrex({
#    'apiKey': "c5af1d0ceeaa4729ad87da1b05d9dfc3",
#    'secret': "d055d8e47fdf4c3bbd0ec6c289ea8ffd",
#})
bitz = ccxt.bitz()
bl3p = ccxt.bl3p()
bleutrade = ccxt.bleutrade()
braziliex = ccxt.braziliex()
btcbox = ccxt.btcbox()
btcchina = ccxt.btcchina()
btcexchange = ccxt.btcexchange()
btcmarkets = ccxt.btcmarkets()
btctradeua = ccxt.btctradeua()
btcturk = ccxt.btcturk()
btcx = ccxt.btcx()
bxinth = ccxt.bxinth()
ccex = ccxt.ccex()
cex = ccxt.cex()
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
gdax = ccxt.gdax()
#gdax = ccxt.gdax({
#    'apiKey': "a43edfe629bc5991acc83a536ac6358e",
#    'secret': "xOvq+iH8NT07TheFB/fmY3GcnMZMwP7Xct9zwWtAZxsCbJh8rxeEe/0BGxfbV2em7P9iqQD7/TJGqmsDO8B/kw==",
#    'password': 'zdmj8o7byla',
#})
gemini = ccxt.gemini()
getbtc = ccxt.getbtc()
hitbtc = ccxt.hitbtc()
hitbtc2 = ccxt.hitbtc2()
huobi = ccxt.huobi()
huobicny = ccxt.huobicny()
huobipro = ccxt.huobipro()
independentreserve = ccxt.independentreserve()
itbit = ccxt.itbit()
jubi = ccxt.jubi()
kraken = ccxt.kraken()
#kraken = ccxt.kraken({
#    'apiKey': "hEvQNMDIeoCJbr7W/ZBb5CGOrx3G0lWF5B3zqa1JBxdZlEaL8EK+D0Mw",
#    'secret': "JaE9wI6Nwgh5oRxiHcVxurwzwBxwc05W/qv/k1srGg4s3EYuXPpNkLLM5NYbbWpM8rCyijIeDavRuqWbU0ZV9A==",
#})
kucoin = ccxt.kucoin()
kuna = ccxt.kuna()
lakebtc = ccxt.lakebtc()
liqui = ccxt.liqui()
livecoin = ccxt.livecoin()
luno = ccxt.luno()
lykke = ccxt.lykke()
mercado = ccxt.mercado()
mixcoins = ccxt.mixcoins()
nova = ccxt.nova()
okcoincny = ccxt.okcoincny()
okcoinusd = ccxt.okcoinusd()
paymium = ccxt.paymium()
poloniex = ccxt.poloniex()
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
wex = ccxt.wex()
xbtce = ccxt.xbtce()
yobit = ccxt.yobit()
yunbi = ccxt.yunbi()
zaif = ccxt.zaif()
zb = ccxt.zb()


