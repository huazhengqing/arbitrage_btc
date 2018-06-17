#!/usr/bin/python

import io
import os
import sys
import uuid
import math
import time
import redis
import sqlite3
import asyncio
import logging
import datetime
import traceback
import pandas as pd
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import util.util
import util.exchange_data

logger = util.util.get_log(__name__)


'''
ids = [
    'binance', 
    'huobipro', 
    'bitfinex',     # 可空, 门槛 $10000
    #'bitfinex2',     # 可空, 门槛 $10000
    'bitstamp', 
    #'bitstamp1',     # doesn't support ETH/BTC, use it for BTC/USD only
    'bittrex',
    'bitz',
    'cex',
    'exmo', 
    'gdax', 
    'gemini', 
    'itbit',    # no symbol= ETH/BTC
    'kraken',       # 可空, 
    'kucoin', 
    'okcoinusd',     # 可空, # no symbol= ETH/BTC
    'okex',     # 可空,  server不稳定
    'poloniex',    # 可空
    'quadrigacx', 
    'wex',
    "zb", 
    ]
'''


ids = ['binance', 'bittrex']
symbols = ['LTC/BTC']
util.exchange_data.ticker_fetch_to_sqlite(ids, symbols)




