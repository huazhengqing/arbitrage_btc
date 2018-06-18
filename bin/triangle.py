#!/usr/bin/python
import os
import sys
import math
import time
import logging
import asyncio
import traceback
import multiprocessing
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
import util.db_base
import util.triangle
import util.exchange_data
import util.exchange_base
logger = util.util.get_log(__name__)



list_id_base_quote_mid = [
    {
        'id':'binance',
        'base':'LTC',
        'quote':'BTC',
        'mid':'ETH',
    },
    {
        'id':'zb',
        'base':'LTC',
        'quote':'BTC',
        'mid':'ETH',
    },
    ]
util.triangle.do_triangle(list_id_base_quote_mid)



