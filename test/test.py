#!/usr/bin/python
import os
import sys
import math
import time
import numpy
import logging
import asyncio
import traceback
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
import util.db_base
import util.exchange_data
from util.exchange_base import exchange_base
logger = util.util.get_log(__name__)




async def fun0():
    print("fun0()  111")
    await asyncio.sleep(1)
    print("fun0()  222")


def fun1():
    print("fun1()  111")
    loop2 = asyncio.new_event_loop()
    task = loop2.create_task(fun0())  
    loop2.run_until_complete(task)
    loop2.close()
    print("fun1()  222")



async def fun2():
    print("fun2()  111")
    await asyncio.sleep(1)
    print("fun2()  222")
    t = threading.Thread(target=fun1, args=())
    t.start()
    t.join()
    print("fun2()  333")



tasks = []
tasks.append(asyncio.ensure_future(fun2()))
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))
loop.close()










