#!/usr/bin/python

import os
import sys
import time
import logging
import datetime
import asyncio
#import ccxt.async as ccxt
import ccxt


def test(exchange):
    allcoin = exchange.request('ticker/price', 'v3')

    btc_coin = dict()
    eth_coin = dict()
    for item in allcoin:
        coin = item["symbol"][:-3]
        quote = item["symbol"][-3:]
        if quote == "BTC":
            btc_coin[coin] = item
        if quote == "ETH":
            eth_coin[coin] = item

    ethprice = float(btc_coin["ETH"]["price"])

    print("币种------ETH记价---ETH/BTC价---转成BTC价---直接BTC价--价差比")
    for k, v in btc_coin.items():
        if k in eth_coin:
            coin2btc = float(ethprice) * float(eth_coin[k]["price"])
            btcbuy  = float(btc_coin[k]["price"]) #BTC买一
            profit = round((btcbuy - coin2btc) / coin2btc, 4)
            if abs(profit) > 0.008:
                print("%s\t%10.8f  %10.8f  %10.8f  %10.8f  %s"%(k, float(eth_coin[k]["price"]), round(ethprice,8), round(coin2btc, 8), btcbuy, profit))


ex = getattr(ccxt, 'binance')()
ex.proxy = 'https://crossorigin.me/'
#ex.proxy = 'https://cors-anywhere.herokuapp.com/'



while True:
    test(ex)

