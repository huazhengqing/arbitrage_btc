#!/usr/bin/python

import os
import sys
import time
import sqlite3
import logging
import traceback
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util

logger = util.util.get_log(__name__)


class db_sqlite3:
    '''
    conf.conf.dir_db
    '''
    def __init__(self, dir, db_name):
        self.dir = dir
        self.db_name = db_name
        path = self.dir + self.db_name + '.sqlite3'
        print(path)
        self.conn = sqlite3.connect(path)
        #self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        

    def close(self):
        if self.cursor is not None:
            try:
                self.cursor.close()
            finally:
                logger.info(traceback.format_exc())
        self.cursor = None
        if self.conn is not None:
            try:
                self.conn.close()
            finally:
                logger.info(traceback.format_exc())
        self.conn = None

    def __del__(self):
        self.close()
        
    def execute(self, sql, param = None):
        if sql is not None and sql != '':
            try:
                if param is None:
                    logger.debug(sql)
                    count = self.cursor.execute(sql)
                else:
                    logger.debug(sql)
                    logger.debug(param)
                    count = self.cursor.execute(sql, param)
                self.conn.commit()
            except Exception as e:
                s = util.util.to_str('execute()  err=', type(e).__name__, '=', e.args)
                logger.debug(s)
                raise
        else:
            logger.info('the [{}] is empty or equal None!'.format(sql))

    def fetchall(self, sql):
        if sql is not None and sql != '':
            logger.debug(sql)
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                return rows
            except Exception as e:
                s = util.util.to_str('fetchall()  err=', type(e).__name__, '=', e.args)
                logger.debug(s)
                raise
        return None










