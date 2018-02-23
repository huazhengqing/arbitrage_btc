#!/usr/bin/python

import os
import sys
import time
import ccxt.async as ccxt
import bz_conf


def symbol_2_string(symbol):
    symbol_1 = symbol.split('/')[0]       # BTC
    symbol_2 = symbol.split('/')[1]       # USD
    s = symbol_1 + '_' + symbol_2
    return s

async def verify_symbol(exchange, symbol):
    symbol_1 = symbol.split('/')[0]       # BTC
    symbol_2 = symbol.split('/')[1]       # USD
    if symbol_2 != 'USD':
        return symbol
    await exchange.load_markets()
    if symbol not in exchange.markets:         # 没有 xxx/usd，只有 xxx/usdt
        symbol_2 = 'USDT'
        s = symbol_1 + '/' + symbol_2
        return s
    return symbol

def init_spider(db, exchanges):
    list_exchanges = []
    for k in exchanges:
        db.create_table_exchange(k)
        if k == bz_conf.bitfinex.id:
            list_exchanges.append(bz_conf.bitfinex)
        if k == bz_conf.okcoinusd.id:
            list_exchanges.append(bz_conf.okcoinusd)
        if k == bz_conf.okex.id:
            list_exchanges.append(bz_conf.okex)
        if k == bz_conf.bitstamp.id:
            list_exchanges.append(bz_conf.bitstamp)
        if k == bz_conf.gemini.id:
            list_exchanges.append(bz_conf.gemini)
        if k == bz_conf.kraken.id:
            list_exchanges.append(bz_conf.kraken)
        if k == bz_conf.exmo.id:
            list_exchanges.append(bz_conf.exmo)
        if k == bz_conf.quadrigacx.id:
            list_exchanges.append(bz_conf.quadrigacx)
        if k == bz_conf.gdax.id:
            list_exchanges.append(bz_conf.gdax)
        if k == bz_conf.huobipro.id:
            list_exchanges.append(bz_conf.huobipro)
    return list_exchanges

    





