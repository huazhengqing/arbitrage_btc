#!/usr/bin/python

import os
import sys
import time
import asyncio
import logging
import traceback
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import util.util
import conf.conf
from util.exchange_base import exchange_base
import util.db_base
import util.db_mysql
import util.db_sqlite3

logger = util.util.get_log(__name__)



class exchange_data:
    def __init__(self, id):
        self.ex = exchange_base(util.util.get_exchange(id, False))
        self.db = util.db_base.db_base()
        self.db_name = ''

    def init_sqlite3(self, dir, db_name):
        self.db_name = db_name
        self.db.init_sqlite3(dir, self.db_name)

    ##########################################################################
    # ticker
    async def ticker_create_table(self, symbol):
        await self.ex.load_markets()
        self.ex.check_symbol(symbol)
        self.ex.set_symbol(symbol)
        self.db.ticker_create_table(self.db_name, symbol, self.ex.ex.id)

    async def ticker_fetch_to_db(self, symbol):
        await self.ex.fetch_ticker(symbol)
        self.db.ticker_insert(self.db_name, symbol, self.ex.ex.id, self.ex.ticker_time, self.ex.ticker['bid'], self.ex.ticker['ask'])

    async def ticker_run(self, symbol):
        await self.ticker_create_table(symbol)
        await self.ex.run(self.ticker_fetch_to_db, symbol)






##########################################################################
# ticker
'''
ccxt.exchanges
[LTC/BTC, ETH/BTC]
'''
def ticker_fetch_to_db(ids, symbols):
    logger.debug(ids)
    logger.debug(symbols)
    tasks = []
    for id in ids:
        ex_data = exchange_data(id)
        ex_data.init_sqlite3(conf.conf.dir_db, 'db_ticker')
        for symbol in symbols:
            tasks.append(asyncio.ensure_future(ex_data.ticker_run(symbol)))
    pending = asyncio.Task.all_tasks()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*pending))







