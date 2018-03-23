#!/usr/bin/python

import os
import sys
import time
import logging
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


exchanges = [
    'binance', 
    'huobipro', 
    'bitfinex',     # 可空, 门槛 $10000
    #'bitfinex2',     # 可空, 门槛 $10000
    'bitstamp', 
    #'bitstamp1',     # doesn't support ETH/BTC, use it for BTC/USD only
    'bittrex',
    'bitz',
    'cex',
    'exmo', 
    'gdax', 
    'gemini', 
    'itbit',    # no symbol= ETH/BTC
    'kraken',       # 可空, 
    'kucoin', 
    'okcoinusd',     # 可空, # no symbol= ETH/BTC
    'okex',     # 可空,  server不稳定
    #'poloniex',    # 可空
    'quadrigacx', 
    'wex',
    "zb", 
    ]
    

exchanges_btc_usd = [
    'binance', 
    'huobipro', 
    'bitfinex',     # 可空, 门槛 $10000
    #'bitfinex2',     # 可空, 门槛 $10000
    'bitstamp', 
    #'bitstamp1',     # doesn't support ETH/BTC, use it for BTC/USD only
    'bittrex',
    'bitz',
    'cex',
    'exmo', 
    'gdax', 
    'gemini', 
    'itbit',    # no symbol= ETH/BTC
    'kraken',       # 可空, 
    'kucoin', 
    'okcoinusd',     # 可空, # no symbol= ETH/BTC
    'okex',     # 可空,  server不稳定
    'poloniex',    # 可空
    'quadrigacx', 
    'wex',
    "zb", 
    ]




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
    ex = util.exchange_data(symbol, exchange)
    while True:
        try:
            if await ex.fetch_ticker():
                db.add_bid_ask(ex.ex.id, ex.ticker_time, ex.ticker['bid'], ex.ticker['ask'])
                print(ex.symbol, ex.ex.id, ex.ticker_time, ex.ticker['bid'], ex.ticker['ask'])

            err_timeout = 0
            err_ddos = 0
            err_auth = 0
            err_not_available = 0
            err_exchange = 0
            err_network = 0
            err = 0
        except ccxt.RequestTimeout as e:
            err_timeout = err_timeout + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_timeout)
        except ccxt.DDoSProtection as e:
            err_ddos = err_ddos + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_ddos)
            time.sleep(30.0)
        except ccxt.AuthenticationError as e:
            err_auth = err_auth + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_auth)
            if err_auth > 5:
                return
        except ccxt.ExchangeNotAvailable as e:
            err_not_available = err_not_available + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_not_available)
            time.sleep(30.0)
            if err_not_available > 5:
                return
        except ccxt.ExchangeError as e:
            err_exchange = err_exchange + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_exchange)
            time.sleep(30.0)
            if err_exchange > 5:
                return
        except ccxt.NetworkError as e:
            err_network = err_network + 1
            print(exchange.id, type(e).__name__, '=', e.args, 'c=', err_network)
            time.sleep(10.0)
            if err_network > 5:
                return
        except Exception as e:
            err = err + 1
            print(exchange.id, type(e).__name__, '=', e.args)
            if err > 5:
                return


[asyncio.ensure_future(get_ticker(exchange)) for exchange in list_exchanges]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))

