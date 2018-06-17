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
logger = util.util.get_log(__name__)



class db_redis:
    __pool = None
    def __init__(self, host, port, password):
        self.db_host = host
        self.db_port = int(port)
        self.password = str(password)
        self.max_connections = 64
        self.redis = self.get_conn()

    def get_conn(self):
        if db_redis.__pool is None:
            db_redis.__pool = redis.ConnectionPool(
                host = self.db_host,
                port = self.db_port,
                password = self.password,
                max_connections = self.max_connections,
                decode_responses = True     # for debug
                )
        self.redis = redis.StrictRedis(connection_pool = db_redis.__pool)
        logger.debug(self.redis.client_list())
        return self.redis

    def set(self, key, value, ex=None):
        logger.debug(key + '=' + value + ',' + ex)
        return self.redis.set(key, value, ex)

    def get(self, key):
        return self.redis.get(key)

    def delete(self, key):
        return self.redis.delete(key) 


