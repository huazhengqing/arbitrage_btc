#!/usr/bin/python

import os
import sys
import time
import logging
import asyncio
import ccxt.async as ccxt
import numpy as np
sys.path.append("..")
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bz_conf
import util


symbol = "ETH/BTC"

if len(sys.argv) >= 2:
    symbol = sys.argv[1]
print(symbol)


exchange_ids = [
    #'binance', 
    #'huobipro', 
    #'bitfinex',     # 可空, 门槛 $10000
    #'bitfinex2',     # 可空, 门槛 $10000
    'bitstamp', 
    #'bitstamp1', 
    #'bittrex',
    'bitz',
    #'cex',
    #'exmo', 
    'gdax', 
    #'gemini', 
    #'itbit',
    #'kraken',       # 可空, 
    'kucoin', 
    #'okcoinusd',     # 可空, 
    'okex',     # 可空,  server不稳定
    'poloniex',    # 可空
    #'quadrigacx', 
    #'wex',
    "zb", 
    ]

exc_data_list = []
for exc_id in exchange_ids:
    exc = util.find_exchange_from_id(exc_id)
    exc_data = util.exchange_data(symbol, exc)
    exc_data_list.append(exc_data)

db_symbol = util.db_banzhuan(util.symbol_2_string(symbol), bz_conf.db_dir)

mm_list = []
size = len(exc_data_list)
for i in range(0, size):
    for j in range(0, size):
        if j > i:
            m = util.calc_stat_arb(symbol, exc_data_list[i], exc_data_list[j], db_symbol)
            mm_list.append(m)

tasks = []
for mm in mm_list:
    tasks.append(asyncio.ensure_future(mm.do_it()))

pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))

