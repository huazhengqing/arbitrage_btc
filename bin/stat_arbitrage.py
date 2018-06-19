#!/usr/bin/python
import os
import sys
import math
import time
import logging
import asyncio
import traceback
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
import util.db_base
import util.triangle
import util.exchange_data
import util.exchange_base
import util.stat_arbitrage
#logger = util.util.get_log(__name__)


symbols = ["ETH/BTC"]
ids = ['okex', 'binance']
db_base = util.db_base.db_base()
db_base.init_sqlite3(conf.conf.dir_db, 'db_ticker')
util.stat_arbitrage.do_stat_arbitrage(symbols, ids, db_base)



