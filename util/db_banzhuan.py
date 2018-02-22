#!/usr/bin/python

import sqlite3
import os


class db_banzhuan:
    def __init__(self, currency_pair = "btc_usd", path_prefix = './'):
        self.currency_pair = currency_pair
        self.path_prefix = path_prefix
        path = self.path_prefix + self.currency_pair + '.db'
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

    def create_table_usd(self, exchange):
        sql = "CREATE TABLE IF NOT EXISTS `" + exchange + "` (Datetime DATETIME NOT NULL, bid DECIMAL(8, 2), ask DECIMAL(8, 2));"
        return self.create_table(sql)

    def create_table_btc(self, exchange):
        sql = "CREATE TABLE IF NOT EXISTS `" + exchange + "` (Datetime DATETIME NOT NULL, bid DECIMAL(20, 12), ask DECIMAL(20, 12));"
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
        data = [(datetime, bid, ask)]
        self.save(save_sql, data)

    def fetchall(self, sql):
        if sql is not None and sql != '':
            self.cu.execute(sql)
            r = self.cu.fetchall()
            if len(r) > 0:
                for e in range(len(r)):
                    print(r[e])
        else:
            print('the [{}] is empty or equal None!'.format(sql)) 

    def fetchone(self, sql, data):
        if sql is not None and sql != '':
            if data is not None:
                d = (data,) 
                self.cu.execute(sql, d)
                r = self.cu.fetchall()
                if len(r) > 0:
                    for e in range(len(r)):
                        print(r[e])
            else:
                print('the [{}] equal None!'.format(data))
        else:
            print('the [{}] is empty or equal None!'.format(sql))
