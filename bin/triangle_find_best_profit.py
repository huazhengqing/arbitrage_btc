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


async def triangle_find_best_profit(id):
    ex = exchange_base(util.util.get_exchange(id, False))
    await ex.run(ex.triangle_find_best_profit)


[asyncio.ensure_future(triangle_find_best_profit('binance'))]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))




