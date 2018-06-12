#!/usr/bin/python

import os
import sys
import time
import asyncio

dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import util.util
import util.triangle


conf_triangle = [
    {
        'id':'binance',
        'base':'LTC',
        'quote':'BTC',
        'mid':'ETH',
    },
    
    {
        'id':'zb',
        'base':'LTC',
        'quote':'BTC',
        'mid':'ETH',
    },
    
]


async def mm(id, base, quote, mid):
    m = util.triangle.triangle(util.util.get_exchange(id, True), base, quote, mid)
    await m.run(m.run_strategy)

[asyncio.ensure_future(mm('binance', 'KMD', 'ETH', 'BTC'))]
#[asyncio.ensure_future(mm(target['id'], target['base'], target['quote'], target['mid'])) for target in conf_triangle]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))


