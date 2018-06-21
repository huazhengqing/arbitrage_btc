#!/usr/bin/python
import io
import os
import sys
import uuid
import math
import time
import redis
import sqlite3
import asyncio
import logging
import datetime
import traceback
import pandas as pd
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import util.util
import util.exchange_data
#logger = util.util.get_log(__name__)




ids = ['binance', 'okex']
symbols = util.exchange_data.get_common_symbols(ids)

symbols = ['XLM/ETH']
util.exchange_data.ticker_fetch_to_sqlite(ids, symbols)




