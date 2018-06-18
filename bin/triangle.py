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
logger = util.util.get_log(__name__)


'''
['base=基准资产', 'quote=定价资产', 'mid=中间资产']
['XXX', 'BTC/ETH/BNB/HT/OKB/', 'USDT/USD/CNY']
['XXX', 'ETH/BNB/HT/OKB/', 'BTC']
['XXX', 'BNB/HT/OKB/', 'ETH']
'''


list_id_base_quote_mid = [
    {
        'id':'binance',
        'base':'EOS',
        'quote':'ETH',
        'mid':'BTC',
    }
    ]
util.triangle.do_triangle(list_id_base_quote_mid)



