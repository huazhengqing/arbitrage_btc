#!/usr/bin/python

import os
import sys
import time
import logging
import asyncio
import ccxt.async as ccxt
import numpy as np
sys.path.append("..")
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bz_conf
import util



ex = util.find_exchange_from_id('binance')
ex.proxy = 'https://crossorigin.me/'
#ex.proxy = 'https://cors-anywhere.herokuapp.com/'



async def mm_three(exchange):
    t = util.three_data(exchange)
    await t.load_markets()
    while True:
        await t.fetch_balance()
        if await t.calc_token():
            print("%s \t %10.4f"%(t.token, t.profit))
            t.load_token_markets()
            await t.fetch_order_book()
            print(t.token_btc, ': bids=', t.token_btc_order_book['bids'][0][0], t.token_btc_order_book['bids'][0][1], '|asks=', t.token_btc_order_book['asks'][0][0], t.token_btc_order_book['asks'][0][1], '|spread%=', round((t.token_btc_order_book['asks'][0][0]-t.token_btc_order_book['bids'][0][0])/t.token_btc_order_book['asks'][0][0], 4))
            print(t.token_eth, ': bids=', t.token_eth_order_book['bids'][0][0], t.token_eth_order_book['bids'][0][1], '|asks=', t.token_eth_order_book['asks'][0][0], t.token_eth_order_book['asks'][0][1], '|spread%=', round((t.token_eth_order_book['asks'][0][0]-t.token_eth_order_book['bids'][0][0])/t.token_eth_order_book['asks'][0][0], 4))
            #await t.op_token()
        

async def mm_three2(exchange):
    while True:
        try:
            await mm_three(exchange)
        except ccxt.RequestTimeout as e:
            print(exchange.id, type(e).__name__, '=', e.args)
        except ccxt.DDoSProtection as e:
            print(exchange.id, type(e).__name__, '=', e.args)
        except ccxt.AuthenticationError as e:
            print(exchange.id, type(e).__name__, '=', e.args)
        except ccxt.ExchangeNotAvailable as e:
            print(exchange.id, type(e).__name__, '=', e.args)
        except ccxt.ExchangeError as e:
            print(exchange.id, type(e).__name__, '=', e.args)
        except ccxt.NetworkError as e:
            print(exchange.id, type(e).__name__, '=', e.args)
        except Exception as e:
            print(exchange.id, type(e).__name__, '=', e.args)



asyncio.get_event_loop().run_until_complete(mm_three2(ex))


