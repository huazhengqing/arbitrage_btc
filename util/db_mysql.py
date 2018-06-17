#!/usr/bin/python

import os
import sys
import time
import logging
import traceback
import configparser
import pymysql
import pymysql.cursors
import DBUtils.PooledDB
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
logger = util.util.get_log(__name__)


class db_mysql():
    __pool = None
    def __init__(self, host, port, user, password, db_name = None):
        self.db_host = host
        self.db_port = int(port)
        self.user = user
        self.password = str(password)
        self.db = db_name
        self.mincached = 1
        self.maxcached = 30
        self.conn = None
        self.cursor = None

    def get_conn(self):
        if db_mysql.__pool is None:
            db_mysql.__pool = DBUtils.PooledDB(creator = pymysql,
                mincached = self.mincached,
                maxcached = self.maxcached,
                host = self.db_host,
                port = self.db_port,
                user = self.user,
                passwd = self.password,
                db = self.db,
                use_unicode = False,
                charset = "utf8",
                cursorclass = pymysql.cursors
                )
        if self.conn is None:
            self.conn = db_mysql.__pool.connection()
        if self.cursor is None:
            self.cursor = self.conn.cursor()
        if not self.cursor:
            logger.info('数据库连接不上')
            raise "数据库连接不上"
        else:
            return self.cursor

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
            logger.debug(sql)
            try:
                self.get_conn()
                if param is None:
                    count = self.cursor.execute(sql)
                else:
                    count = self.cursor.execute(sql, param)
                self.conn.commit()
                self.close()
            except Exception as e:
                self.close()
                s = util.util.to_str('execute()  err=', type(e).__name__, '=', e.args)
                logger.debug(s)
                raise
        else:
            logger.info('the [{}] is empty or equal None!'.format(sql))

    def fetchall(self, sql):
        if sql is not None and sql != '':
            logger.debug(sql)
            try:
                self.get_conn()
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                self.close()
                return rows
            except Exception as e:
                self.close()
                s = util.util.to_str('fetchall()  err=', type(e).__name__, '=', e.args)
                logger.debug(s)
                raise
        return None






