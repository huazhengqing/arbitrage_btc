#!/usr/bin/python

import os
import sys
import time
import asyncio

dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
from util.exchange_base import exchange_base
from util.db_symbol import db_symbol


symbol = "LTC/BTC"


exchanges = [
    'binance', 
    ]
    

exchanges_btc_usd = [
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


db = db_symbol(symbol)
db.init_log()

async def fetch_ticker_to_db(symbol, id):
    ex = exchange_base(util.util.get_exchange(id, False))
    ex.init_log()
    await ex.init_db_table(symbol, db)
    await ex.run(ex.fetch_ticker_to_db, symbol, db)


#[asyncio.ensure_future(fetch_ticker_to_db(symbol, id)) for id in exchanges]
[asyncio.ensure_future(fetch_ticker_to_db(symbol, 'bittrex'))]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))

