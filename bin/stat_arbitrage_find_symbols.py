#!/usr/bin/python

import os
import sys
import time
import asyncio

dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import util.util
from util.exchange_base import exchange_base


conf_ids = ['binance', 'zb']


async def arbitrage_find_symbols(ids):
    ex = exchange_base()
    await ex.arbitrage_find_symbols(ids)


[asyncio.ensure_future(arbitrage_find_symbols(conf_ids))]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))


