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


symbol = "ETH/BTC"
exchange1_id = "binance"



exchange1 = util.find_exchange_from_id(exchange1_id)
ex1 = util.exchange_data(symbol, exchange1) 




asyncio.get_event_loop().run_until_complete(ex1.load_markets())



tasks = [
    asyncio.ensure_future(ex1.fetch_balance()),
    asyncio.ensure_future(ex1.fetch_order_book()),
]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))



print('tttt')






