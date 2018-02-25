#!/usr/bin/python

import os
import sys
import time
import asyncio
import ccxt.async as ccxt
#import cfscrape
sys.path.append("..")
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import util
import bz_conf




symbols = [
    'BTC/USD', 
    'ETH/USD', 'ETH/BTC', 
    'XRP/USD', 'XRP/BTC', 'XRP/ETH', 
    'BCH/USD', 'BCH/BTC', 'BCH/ETH', 
    'LTC/USD', 'LTC/BTC', 'LTC/ETH', 
    'ADA/USD', 'ADA/BTC', 'ADA/ETH', 
    'NEO/USD', 'NEO/BTC', 'NEO/ETH', 
    'XLM/USD', 'XLM/BTC', 'XLM/ETH', 
    'EOS/USD', 'EOS/BTC', 'EOS/ETH', 
    'IOTA/USD', 'IOTA/BTC', 'IOTA/ETH', 
    'DASH/USD', 'DASH/BTC', 'DASH/ETH', 
    'XMR/USD', 'XMR/BTC', 'XMR/ETH', 
    'ETC/USD', 'ETC/BTC', 'ETC/ETH', 
    'XEM/USD', 'XEM/BTC', 'XEM/ETH', 
    'VEN/USD', 'VEN/BTC', 'VEN/ETH', 
    'TRX/USD', 'TRX/BTC', 'TRX/ETH', 
    'USDT/USD', 'USDT/BTC', 'USDT/ETH', 
    'LSK/USD', 'LSK/BTC', 'LSK/ETH', 
    'BTG/USD', 'BTG/BTC', 'BTG/ETH', 
    'QTUM/USD', 'QTUM/BTC', 'QTUM/ETH', 
    'OMG/USD', 'OMG/BTC', 'OMG/ETH', 
    'ICX/USD', 'ICX/BTC', 'ICX/ETH', 
    'ZEC/USD', 'ZEC/BTC', 'ZEC/ETH', 
    'XRB/USD', 'XRB/BTC', 'XRB/ETH', 
    'BNB/USD', 'BNB/BTC', 'BNB/ETH', 
    'STEEM/USD', 'STEEM/BTC', 'STEEM/ETH', 
    'XVG/USD', 'XVG/BTC', 'XVG/ETH', 
    'BCN/USD', 'BCN/BTC', 'BCN/ETH', 
    'PPT/USD', 'PPT/BTC', 'PPT/ETH', 
    'DGD/USD', 'DGD/BTC', 'DGD/ETH', 
    'DOGE/USD', 'DOGE/BTC', 'DOGE/ETH', 
    'STRAT/USD', 'STRAT/BTC', 'STRAT/ETH', 
    'SC/USD', 'SC/BTC', 'SC/ETH', 
    'WAVES/USD', 'WAVES/BTC', 'WAVES/ETH', 
    'HT/USD', 'HT/BTC', 'HT/ETH', 
    'WTC/USD', 'WTC/BTC', 'WTC/ETH', 
    'SNT/USD', 'SNT/BTC', 'SNT/ETH', 
    'MKR/USD', 'MKR/BTC', 'MKR/ETH', 
    'BTS/USD', 'BTS/BTC', 'BTS/ETH', 
    'ELA/USD', 'ELA/BTC', 'ELA/ETH', 
    
]


py_path = os.path.dirname(os.path.abspath(__file__)) + "\\spider_symbol.py"

for s in symbols:
    cmd_str = "start /b   python    \"" + py_path + "\"     \"" + s + "\""
    print(cmd_str)
    os.system(cmd_str)
    






