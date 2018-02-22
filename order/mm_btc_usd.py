#!/usr/bin/python

import os
import sys
import asyncio
import ccxt.async as ccxt
#import cfscrape

sys.path.append("..")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
import util.db_banzhuan as db_banzhuan
import bz_conf

currency_pair = 'BTC/USD'















