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


symbol = 'BTC/USD'
exchange1 = bz_conf.okcoinusd
exchange2 = bz_conf.kraken
db_symbol = util.db_banzhuan(util.symbol_2_string(symbol), bz_conf.db_dir)


mm = util.calc_stat_arb(symbol, exchange1, exchange2, db_symbol)
mm.do_it()



