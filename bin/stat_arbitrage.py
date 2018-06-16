#!/usr/bin/python

import os
import sys
import time
import asyncio

dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
import util.db_base
import util.stat_arbitrage
from util.exchange_base import exchange_base



symbols = ["LTC/BTC"]
ids = [
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
db_base = util.db_base.db_base()
db_base.init_sqlite3(conf.conf.dir_db, 'db_ticker')
util.stat_arbitrage.do_stat_arbitrage(symbols, ids, db_base)

