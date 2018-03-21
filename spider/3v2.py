#!/usr/bin/python

import os
import sys
import time
import logging
import asyncio
import ccxt.async as ccxt
import numpy as np
sys.path.append("..")
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bz_conf
import util



ex = util.find_exchange_from_id('binance')
ex.proxy = 'https://crossorigin.me/'
#ex.proxy = 'https://cors-anywhere.herokuapp.com/'



async def mm_three(exchange):
    t = util.three_data(exchange)
    await util.load_markets(exchange)
    await t.fetch_balance()
    while True:
        if await t.calc_token():
            print("%s \t %10.4f"%(t.token, t.profit))
            t.load_markets()
        

        
asyncio.get_event_loop().run_until_complete(mm_three(ex))


