#!/usr/bin/python

import os
import sys
import time
import asyncio
import ccxt.async as ccxt
#import cfscrape
sys.path.append("..")
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#print(sys.path)
import util
import bz_conf



symbol = "BTC/USD"
if len(sys.argv) >= 2:
    symbol = sys.argv[1]
print(symbol)


exchanges = bz_conf.exchanges


db = util.db_banzhuan(util.symbol_2_string(symbol), bz_conf.db_dir)
list_exchanges = util.init_spider(db, exchanges)


async def get_ticker(exchange):
    err_timeout = 0
    err_ddos = 0
    err_auth = 0
    err_not_available = 0
    err_exchange = 0
    err_network = 0
    err = 0
    while True:
        try:
            s = await util.verify_symbol(exchange, symbol)
            if s == '':
                return

            ticker = await exchange.fetch_ticker(s)
            db.add_bid_ask(exchange.id, ticker['timestamp'], ticker['bid'], ticker['ask'])
            print(s, exchange.id, ticker['timestamp'], ticker['bid'], ticker['ask'])

            
            err_timeout = 0
            err_ddos = 0
            err_auth = 0
            err_not_available = 0
            err_exchange = 0
            err_network = 0
            err = 0


            '''
            # 可以取到价格和数量，没测过哪个速度快
            order_book = await exchange.fetch_order_book(s, 1)      # 取深度信息，只取1层
            dt = order_book['timestamp']
            bid1 = order_book['bids'][0][0]
            bid1_quantity = order_book['bids'][0][1]
            ask1 = order_book['asks'][0][0]
            ask1_quantity = order_book['asks'][0][1]
            db.add_bid_ask(exchange.id, dt, bid1, ask1)
            print(exchange.id, dt, bid1, ask1)
            '''
            
        except ccxt.RequestTimeout as e:
            print(type(e).__name__, '=', e.args)
            time.sleep(2)
            err_timeout = err_timeout + 1
            if err_timeout > 5:
                return
        except ccxt.DDoSProtection as e:
            print(type(e).__name__, '=', e.args)
            time.sleep(2)
            err_ddos = err_ddos + 1
            if err_ddos > 5:
                return
        except ccxt.AuthenticationError as e:
            print(type(e).__name__, '=', e.args)
            err_auth = err_auth + 1
            if err_auth > 5:
                return
        except ccxt.ExchangeNotAvailable as e:
            print(type(e).__name__, '=', e.args)
            return    # 
            err_not_available = err_not_available + 1
            if err_not_available > 5:
                return
        except ccxt.ExchangeError as e:
            print(type(e).__name__, '=', e.args)
            return    # doesn't support xxx/xxx
            err_exchange = err_exchange + 1
            if err_exchange > 5:
                return
        except ccxt.NetworkError as e:
            print(type(e).__name__, '=', e.args)
            err_network = err_network + 1
            if err_network > 5:
                return
        except Exception as e:
            print(type(e).__name__, '=', e.args)
            err = err + 1
            if err > 5:
                return


[asyncio.ensure_future(get_ticker(exchange)) for exchange in list_exchanges]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))

