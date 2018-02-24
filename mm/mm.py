#!/usr/bin/python

import os
import sys
import time
import asyncio
import ccxt.async as ccxt
import numpy as np
sys.path.append("..")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
import bz_conf
import util


symbol = "BTC/USD"
exchange1_id = "okcoinusd"
exchange2_id = "kraken"

if len(sys.argv) >= 4:
    symbol = sys.argv[1]
    exchange1_id = sys.argv[2]
    exchange2_id = sys.argv[3]
print(symbol, exchange1_id, exchange2_id)

exchange1 = util.find_exchange_from_id(exchange1_id)
exchange2 = util.find_exchange_from_id(exchange2_id)

db_symbol = util.db_banzhuan(util.symbol_2_string(symbol), bz_conf.db_dir)
mm = util.calc_stat_arb(symbol, exchange1, exchange2, db_symbol)
mm.do_it()



