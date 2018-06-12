#!/usr/bin/python

import os
import sys
import time
import asyncio

dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
from util.exchange_base import exchange_base
from util.db_symbol import db_symbol


symbol = "BTC/USD"


exchange_ids = [
    #'binance', 
    #'huobipro', 
    #'bitfinex',     # 可空, 门槛 $10000
    #'bitfinex2',     # 可空, 门槛 $10000
    #'bitstamp', 
    #'bitstamp1', 
    #'bittrex',
    #'bitz',
    #'cex',
    #'exmo', 
    #'gdax', 
    #'gemini', 
    #'itbit',
    #'kraken',       # 可空, 
    #'kucoin', 
    #'okcoinusd',     # 可空, 
    'okex',     # 可空,  server不稳定
    #'poloniex',    # 可空
    #'quadrigacx', 
    #'wex',
    "zb", 
    ]


db = db_symbol(symbol)
db.init_log()

exc_data_list = []
for id in exchange_ids:
    ex = exchange_base(util.util.get_exchange(id, True))
    ex.init_log()
    #await ex.init_db_table(symbol, db)
    exc_data_list.append(ex)

mm_list = []
size = len(exc_data_list)
for i in range(0, size):
    for j in range(0, size):
        if j > i:
            m = util.stat_arbitrage.stat_arbitrage(symbol, exc_data_list[i], exc_data_list[j], db)
            m.init_log()
            mm_list.append(m)

tasks = []
for mm in mm_list:
    tasks.append(asyncio.ensure_future(mm.run(mm.run_mm)))

pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))

