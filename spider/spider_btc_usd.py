#!/usr/bin/python

import asyncio
import ccxt.async as ccxt

import sys
sys.path.append("..")
import util.db_banzhuan as db_banzhuan


db_path_prefix = '../db/'

db_file_name = 'btc_usd'
currency_pair = 'BTC/USD'
exchange = ['kraken']


async def poll(tickers):
    i = 0
    kraken = ccxt.kraken()
    while True:
        symbol = tickers[i % len(tickers)]
        yield (symbol, await kraken.fetch_ticker(symbol))
        i += 1
        await asyncio.sleep(kraken.rateLimit / 1000)


async def main():
    db = db_banzhuan(db_file_name, db_path_prefix)
    for i in exchange:
        db.create_table_usd(i)

    async for (symbol, ticker) in poll([currency_pair]):
        print(ticker)
        db.add_bid_ask('kraken', ticker['timestamp'], ticker['bid'], ticker['ask'])


asyncio.get_event_loop().run_until_complete(main())












