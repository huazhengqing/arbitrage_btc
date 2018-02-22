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


list_exchanges = []
db = db_banzhuan(bz_conf.db_filename_btc_usd, bz_conf.db_dir)
for k, v in  bz_conf.exchanges_btc_usd.items():
    if v == False:
        pass
    db.create_table_exchange(k)
    if k == ccxt.bitfinex.__name__:
        list_exchanges.append(bz_conf.bitfinex)
    if k == ccxt.okcoinusd.__name__:
        list_exchanges.append(bz_conf.okcoinusd)
    if k == ccxt.okex.__name__:
        list_exchanges.append(bz_conf.okex)
    if k == ccxt.bitstamp.__name__:
        list_exchanges.append(bz_conf.bitstamp)
    if k == ccxt.gemini.__name__:
        list_exchanges.append(bz_conf.gemini)
    if k == ccxt.kraken.__name__:
        list_exchanges.append(bz_conf.kraken)
    if k == ccxt.exmo.__name__:
        list_exchanges.append(bz_conf.exmo)
    if k == ccxt.quadrigacx.__name__:
        list_exchanges.append(bz_conf.quadrigacx)
    if k == ccxt.gdax.__name__:
        list_exchanges.append(bz_conf.gdax)
    if k == ccxt.huobipro.__name__:
        list_exchanges.append(bz_conf.huobipro)



async def get_ticker(exchange):
    while True:
        try:
            ticker = await exchange.fetch_ticker(currency_pair)
            db.add_bid_ask(exchange.id, ticker['timestamp'], ticker['bid'], ticker['ask'])
            print(exchange.id, ticker['timestamp'], ticker['bid'], ticker['ask'])
        except ccxt.RequestTimeout as e:
            print('RequestTimeout=', type(e).__name__, e.args)
        except ccxt.DDoSProtection as e:
            print('DDoSProtection=', type(e).__name__, e.args)
            await asyncio.sleep(exchange.rateLimit / 1000)
        except ccxt.AuthenticationError as e:
            print('AuthenticationError=', type(e).__name__, e.args)
        except ccxt.ExchangeNotAvailable as e:
            print('ExchangeNotAvailable=', type(e).__name__, e.args)
            await asyncio.sleep(exchange.rateLimit / 1000)
        except ccxt.ExchangeError as e:
            print('ExchangeError=', type(e).__name__, e.args)
            await asyncio.sleep(exchange.rateLimit / 1000)
        except ccxt.NetworkError as e:
            print('NetworkError=', type(e).__name__, e.args)





[asyncio.ensure_future(get_ticker(exchange)) for exchange in list_exchanges]
pending = asyncio.Task.all_tasks()
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*pending))


