#!/usr/bin/python

import os
import sys
import time
import redis
import asyncio
import logging
import traceback
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
import util.exchange_base
import util.db_base
import util.db_mysql
import util.db_sqlite3
import util.db_redis
logger = util.util.get_log(__name__)


# 取公共数据
class exchange_data:
    def __init__(self, id):
        self.ex = util.exchange_base.exchange_base(util.util.get_exchange(id, False))
        self.db = util.db_base.db_base()
        self.db_name = ''

    def init_sqlite3(self, dir, db_name):
        self.db_name = db_name
        self.db.init_sqlite3(dir, self.db_name)

    def init_mysql(self, host, port, user, password, db_name = None):
        self.db_name = db_name
        self.db.init_mysql(host, port, user, password, db_name)


    ##########################################################################
    # market mysql/sqlite







    ##########################################################################
    # 历史数据 mysql/sqlite







    ##########################################################################
    # ticker redis
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
    # orderbook redis






##########################################################################
# ticker
'''
ccxt.exchanges
[LTC/BTC, ETH/BTC]
'''
def ticker_fetch_to_sqlite(ids, symbols):
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







