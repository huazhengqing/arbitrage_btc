#!/usr/bin/python

import sqlite3
import os
import time


class db_banzhuan:
    def __init__(self, symbol_str = "BTC_USD", db_dir = './'):
        self.symbol_str = symbol_str
        self.db_dir = db_dir
        path = self.db_dir + self.symbol_str + '.db'
        print(path)
        self.conn = sqlite3.connect(path)
        #self.conn = sqlite3.connect(':memory:')
        self.cu = self.conn.cursor()

    def create_table(self, sql):
        if sql is not None and sql != '':
            self.cu.execute(sql)
            self.conn.commit()
        else:
            print('the [{}] is empty or equal None!'.format(sql))

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
            print('the [{}] is empty or equal None!'.format(sql))

    def add_bid_ask(self, exchange, datetime, bid, ask):
        save_sql = 'INSERT INTO ' + exchange + ' values (?, ?, ?)'
        dt = int(float(datetime))
        data = [(dt, bid, ask)]
        self.save(save_sql, data)

    def fetch(self, exchange, sql_condition):
        sql = 'select * from ' + exchange + ' where  Datetime >= ' + sql_condition
        self.cu.execute(sql)
        rows = self.cu.fetchall() 
        return rows

    def fetch_one(self, exchange, sql_condition):
        sql = 'select * from ' + exchange + ' where  Datetime == ' + sql_condition
        self.cu.execute(sql)
        rows = self.cu.fetchall()
        return rows

            

