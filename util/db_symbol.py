#!/usr/bin/python

import os
import sys
import math
import time
import sqlite3
import logging
import asyncio
import traceback
import multiprocessing
import numpy as np
import ccxt.async as ccxt

import conf.conf
import util.util


class db_symbol:
    def __init__(self, symbol, dir_db = conf.conf.dir_db):
        self.symbol = symbol
        self.symbol_str = util.util.symbol_2_string(symbol)
        self.dir_db = dir_db
        path = self.dir_db + self.symbol_str + '.sqlite3'
        print(path)
        self.conn = sqlite3.connect(path)
        #self.conn = sqlite3.connect(':memory:')
        self.cu = self.conn.cursor()

        self.logger = None

    def init_log(self, name = __name__):
        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)-8s: %(message)s')
        file_handler = logging.FileHandler(conf.conf.dir_log + name + "_{0}.log".format(int(time.time())), mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    def create_table(self, sql):
        if sql is not None and sql != '':
            self.logger.debug(sql)
            self.cu.execute(sql)
            self.conn.commit()
        else:
            self.logger.info('the [{}] is empty or equal None!'.format(sql))


    def create_table_exchange(self, exchange):
        sql = "CREATE TABLE IF NOT EXISTS `" + exchange + "` (Datetime DATETIME NOT NULL, bid DECIMAL(20, 12), ask DECIMAL(20, 12));"
        return self.create_table(sql)

    def create_table_spread(self, exchange1, exchange2):
        sql = "CREATE TABLE IF NOT EXISTS `" + exchange1 + "_" + exchange2 + "` (Datetime DATETIME NOT NULL, exchange1_bid_exchange2_ask DECIMAL(20, 12), exchange2_bid_exchange1_ask DECIMAL(20, 12));"
        return self.create_table(sql)

    def close_all(self):
        try:
            if self.cu is not None:
                self.cu.close()
        finally:
            if self.cu is not None:
                self.cu.close()
        self.conn.close()

    def __del__(self):
        self.close_all()

    def save(self, sql, data):
        if sql is not None and sql != '':
            if data is not None:
                for d in data:
                    self.cu.execute(sql, d)
                    self.conn.commit()
        else:
            self.logger.info('the [{}] is empty or equal None!'.format(sql))

    def add_bid_ask(self, ex_id, datetime, bid, ask):
        save_sql = 'INSERT INTO ' + ex_id + ' values (?, ?, ?)'
        dt = int(float(datetime))
        data = [(dt, bid, ask)]
        self.save(save_sql, data)

    def fetch(self, ex_id, dt):
        sql = 'select * from ' + ex_id + ' where  Datetime >= ' + str(dt)
        self.logger.debug(sql)
        try:
            self.cu.execute(sql)
            rows = self.cu.fetchall() 
            return rows
        except Exception as e:
            s = util.util.to_str('fetch_one() sqlite3 err=', type(e).__name__, '=', e.args)
            self.logger.debug(s)
        return None

    def fetch_one(self, ex_id, dt):
        sql = 'select * from ' + ex_id + ' where  Datetime == ' + str(dt)
        self.logger.debug(sql)
        try:
            self.cu.execute(sql)
            rows = self.cu.fetchall()
            return rows
        except Exception as e:
            s = util.util.to_str('fetch_one() sqlite3 err=', type(e).__name__, '=', e.args)
            self.logger.debug(s)
        return None

            

