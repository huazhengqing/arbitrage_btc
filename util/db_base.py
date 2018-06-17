#!/usr/bin/python

import os
import sys
import time
import redis
import logging
import traceback
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
import util.db_mysql
import util.db_sqlite3
import util.db_redis
logger = util.util.get_log(__name__)


class db_base:
    def __init__(self):
        self.db = None
        self.db_name = ''
        self.table = ''
    
    def init_sqlite3(self, dir, db_name):
        self.db = util.db_sqlite3.db_sqlite3(dir, db_name)
        self.db_name = db_name

    def init_mysql(self, host, port, user, password, db_name = None):
        self.db = util.db_mysql.db_mysql(host, port, user, password, db_name)
        self.db_name = db_name

    def close(self):
        self.db.close()

    def __del__(self):
        self.close()
        
    def execute(self, sql, param = None):
        return self.db.execute(sql, param)

    def fetchall(self, sql):
        return self.db.fetchall(sql)

    def save(self, sql, data):
        if data is not None:
            for d in data:
                self.execute(sql, d)

    ##########################################################################
    # market mysql/sqlite
    '''
    CREATE TABLE IF NOT EXISTS db_market.t_exchange_info(
        exchange TEXT NOT NULL,
        fee DOUBLE NOT NULL
        );
    CREATE TABLE IF NOT EXISTS db_market.t_exchange(
        exchange TEXT NOT NULL,
        symbol TEXT NOT NULL,
        vol INT UNSIGNED NOT NULL, 
        dt DATETIME NOT NULL,
        PRIMARY KEY(exchange, symbol)
        );
    '''










    ##########################################################################
    # 历史数据 mysql/sqlite













    ##########################################################################
    # tciker redis
    '''
    CREATE TABLE IF NOT EXISTS db_ticker.t_symbol_exchange(
        symbol TEXT NOT NULL,
        exchange TEXT NOT NULL,
        dt INT UNSIGNED NOT NULL, 
        bid DECIMAL(20, 12), 
        ask DECIMAL(20, 12),
        PRIMARY KEY(symbol, exchange, dt)
        );
    '''
    def ticker_get_table_name(self, db_name, symbol, exchange):
        self.db_name = db_name
        #self.table = db_name + ".t_" + util.util.symbol_2_string(symbol) + "_" + exchange
        self.table = "t_" + util.util.symbol_2_string(symbol) + "_" + exchange
        return self.table

    def ticker_create_table(self, db_name, symbol, exchange):
        self.ticker_get_table_name(db_name, symbol, exchange)
        sql = "CREATE TABLE IF NOT EXISTS " + self.table + " ( \
            symbol TEXT NOT NULL, \
            exchange TEXT NOT NULL, \
            dt INT UNSIGNED NOT NULL, \
            bid DECIMAL(20, 12), \
            ask DECIMAL(20, 12), \
            PRIMARY KEY(symbol, exchange, dt) \
            );"
        return self.execute(sql)

    def ticker_insert(self, db_name, symbol, exchange, dt, bid, ask):
        self.ticker_get_table_name(db_name, symbol, exchange)
        save_sql = 'REPLACE INTO ' + self.table + ' VALUES (?, ?, ?, ?, ?)'
        data = [(symbol, exchange, int(float(dt)), bid, ask)]
        self.save(save_sql, data)

    def ticker_select(self, db_name, symbol, exchange, dt):
        self.ticker_get_table_name(db_name, symbol, exchange)
        sql = 'select * from ' + self.table + ' where  dt == ' + str(dt)
        return self.fetchall(sql)

    ##########################################################################
    # orderbook redis
























