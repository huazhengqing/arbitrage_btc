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
from util.exchange_base import exchange_base
import util.db_base
import util.db_mysql
import util.db_sqlite3
import util.db_redis
logger = util.util.get_log(__name__)


# 取公共数据
class exchange_data(exchange_base):
    def __init__(self, id):
        #exchange_base.__init__(self, util.util.get_exchange(id, False))
        super(exchange_data, self).__init__(util.util.get_exchange(id, False))
        self.db = util.db_base.db_base()
        self.db_name = ''

    def to_string(self):
        return "exchange_data[{0}] ".format(self.ex.id)

    def init_sqlite3(self, dir, db_name):
        #logger.debug(self.to_string() + "init_sqlite3({0}, {1}) start".format(dir, db_name))
        self.db_name = db_name
        self.db.init_sqlite3(dir, self.db_name)
        #logger.debug(self.to_string() + "init_sqlite3({0}, {1}) end".format(dir, db_name))

    def init_mysql(self, host, port, user, password, db_name = None):
        #logger.debug(self.to_string() + "init_mysql({0}, {1}) start".format(host, port))
        self.db_name = db_name
        self.db.init_mysql(host, port, user, password, db_name)
        #logger.debug(self.to_string() + "init_mysql({0}, {1}) end".format(host, port))


    ##########################################################################
    # markets mysql/sqlite
    



    ##########################################################################
    # 历史数据 mysql/sqlite







    ##########################################################################
    # ticker redis
    async def ticker_create_table(self, symbol):
        #logger.debug(self.to_string() + "ticker_create_table({0}) start".format(symbol))
        await exchange_base.load_markets(self)
        exchange_base.check_symbol(self, symbol)
        exchange_base.set_symbol(self, symbol)
        self.db.ticker_create_table(self.db_name, symbol, self.ex.id)
        #logger.debug(self.to_string() + "ticker_create_table({0}) end".format(symbol))

    async def ticker_fetch_to_db(self, symbol):
        #logger.debug(self.to_string() + "ticker_fetch_to_db({0}) start".format(symbol))
        await exchange_base.fetch_ticker(self, symbol)
        self.db.ticker_insert(self.db_name, symbol, self.ex.id, self.ticker_time, self.ticker['bid'], self.ticker['ask'])
        #logger.debug(self.to_string() + "ticker_fetch_to_db({0}) end".format(symbol))

    async def ticker_run(self, symbol):
        #logger.debug(self.to_string() + "ticker_run({0}) start".format(symbol))
        await self.ticker_create_table(symbol)
        await exchange_base.run(self, self.ticker_fetch_to_db, symbol)
        #logger.debug(self.to_string() + "ticker_run({0}) end".format(symbol))


    ##########################################################################
    # orderbook redis






##########################################################################
# ticker
'''
ccxt.exchanges
[LTC/BTC, ETH/BTC]
'''
def ticker_fetch_to_sqlite(ids, symbols):
    logger.info("ticker_fetch_to_sqlite({0}, {1}) start".format(ids, symbols))
    tasks = []
    for id in ids:
        logger.info("ticker_fetch_to_sqlite({0}, {1}) id={2}".format(ids, symbols, id))
        ex_data = exchange_data(id)
        ex_data.init_sqlite3(conf.conf.dir_db, 'db_ticker')
        for symbol in symbols:
            logger.info("ticker_fetch_to_sqlite({0}, {1}) id={2},symbol={3}".format(ids, symbols, id, symbol))
            tasks.append(asyncio.ensure_future(ex_data.ticker_run(symbol)))
    pending = asyncio.Task.all_tasks()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*pending))
    logger.info("ticker_fetch_to_sqlite({0}, {1}) end".format(ids, symbols))




# 找出 交易所共同支持的 交易对
def get_common_symbols(ids):
    exchanges = {}
    tasks = []
    for id in ids:
        exchanges[id] = exchange_data(id)
        tasks.append(asyncio.ensure_future(exchanges[id].load_markets()))
    pending = asyncio.Task.all_tasks()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*pending))
    tasks = []
    for id in ids:
        tasks.append(asyncio.ensure_future(exchanges[id].ex.close()))
    pending = asyncio.Task.all_tasks()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*pending))

    allSymbols = [symbol for id in ids for symbol in exchanges[id].ex.symbols]
    uniqueSymbols = list(set(allSymbols))
    arbitrableSymbols = sorted([symbol for symbol in uniqueSymbols if allSymbols.count(symbol) > 1])

    s = util.util.to_str(' symbol          | ' + ''.join([' {:<15} | '.format(id) for id in ids]))
    logger.info(s)
    s = util.util.to_str(''.join(['-----------------+-' for x in range(0, len(ids) + 1)]))
    logger.info(s)

    for symbol in arbitrableSymbols:
        string = ' {:<15} | '.format(symbol)
        for id in ids:
            string += ' {:<15} | '.format(id if symbol in exchanges[id].ex.symbols else '')
        logger.info(string)

    return arbitrableSymbols





