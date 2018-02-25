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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import util
import bz_conf
import subprocess



symbols = [
    'BTC/USD', 
    'ETH/USD', 
    'ETH/BTC', 
    'LTC/USD', 
    'LTC/BTC', 
    'LTC/ETH', 
    
]


py_path = os.path.dirname(os.path.abspath(__file__)) + "\\mm.py"


for symbol in symbols:
    cmd_str = "start /b   python    \"" + py_path + "\"     \"" + symbol + "\"    "
    print(cmd_str)
    os.system(cmd_str)
    

