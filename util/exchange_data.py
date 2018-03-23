#!/usr/bin/python

import os
import sys
import time
import logging
import asyncio
import numpy as np
import ccxt.async as ccxt
import util
import bz_conf


class exchange_data():
    def __init__(self, symbol, exchange):
        self.symbol = symbol         # BTC/USD
        self.ex = exchange
        
        self.symbol_1 = self.symbol.split('/')[0]       # BTC
        self.symbol_2 = self.symbol.split('/')[1]       # USD

        '''
        self.market['limits']['amount']['min']    # 最小买卖数量    0.000001
        self.market['limits']['price']['min']    # 最小价格    0.000001
        self.market['precision']['amount']    # 精度    8
        self.market['precision']['price']     # 精度    2
        '''
        # load_markets
        self.market = None
        self.long_fee = 0.001        # 单笔交易费用 %
        self.short_fee = 0.001
        self.support_short = False    # 是否支持作空

        '''
        self.balance[self.symbol_1]['free']       # 已经开仓了多少
        self.balance[self.symbol_1]['used']
        self.balance[self.symbol_1]['total']

        self.balance[self.symbol_2]['free']       # 还有多少钱
        self.balance[self.symbol_2]['used']
        self.balance[self.symbol_2]['total']
        '''
        # fetch_balance
        self.balance = None
        self.balance_symbol1 = None
        self.balance_symbol2 = None

        '''
        self.order_book['bids'][0][0]    # buy_1_price
        self.order_book['bids'][0][1]    # buy_1_quantity
        self.order_book['asks'][0][0]    # sell_1_price
        self.order_book['asks'][0][1]    # sell_1_quantity
        '''
        # fetch_order_book
        self.order_book = None
        self.order_book_time = 0

        self.buy_1_price = 0
        self.buy_1_quantity = 0
        self.sell_1_price = 0
        self.sell_1_quantity = 0

        # spider
        self.ticker = None
        self.ticker_time = 0

    # 检查是否支持 symbol，确定最小交易量，费用
    async def load_markets(self):
        if not self.market is None:
            return True
        await self.ex.load_markets()
        if self.symbol in self.ex.markets:
            self.market = self.ex.markets[self.symbol]
        else:
            # 不支持此 symbol
            # 没有 xxx/usd，只有 xxx/usdt
            if self.symbol_2 == 'USD':
                ret_s = self.symbol_1 + '/USDT'
                if ret_s in self.ex.markets:
                    self.symbol = ret_s
                    self.symbol_2 = 'USDT'
                    self.market = self.ex.markets[self.symbol]
                else:
                    return False
            else:
                return False
        
        if self.ex.id == 'binance':
            self.long_fee = 0.0010    # %
            self.short_fee = 0.0010    # %
            self.support_short = False
        elif self.ex.id == 'huobipro':
            self.long_fee = 0.0020    # %
            self.short_fee = 0.0020    # %
            self.support_short = True
        elif self.ex.id == 'okcoinusd' or self.ex.id == 'okcoin' or self.ex.id == 'okcoincny':
            self.long_fee = 0.0020    # %
            self.short_fee = 0.0020    # %
            self.support_short = False
        elif self.ex.id == 'okex':
            self.long_fee = 0.0020    # %
            self.short_fee = 0.0020    # %
            self.support_short = True
        elif self.ex.id == 'bitfinex':
            self.long_fee = 0.0020    # %
            self.short_fee = 0.0020    # %
            self.support_short = True
        elif self.ex.id == 'bittrex':
            self.long_fee = 0.0020    # %
            self.short_fee = 0.0020    # %
            self.support_short = True

        return True
    
    #  查看余额
    async def fetch_balance(self):
        if await self.load_markets():
            p = {}
            if self.ex.id == 'binance':
                p = {
                    'recvWindow' : 60000,
                }
            self.balance = await self.ex.fetch_balance(p)
            self.balance_symbol1 = self.balance[self.symbol_1]
            self.balance_symbol2 = self.balance[self.symbol_2]
            return True
        return False

    # 取深度信息
    async def fetch_order_book(self):
        if await self.load_markets():
            self.order_book = await self.ex.fetch_order_book(self.symbol, 5)
            self.order_book_time = int(time.time())
            self.buy_1_price = self.order_book['bids'][0][0]    # buy_1_price
            self.buy_1_quantity = self.order_book['bids'][0][1]    # buy_1_quantity
            self.sell_1_price = self.order_book['asks'][0][0]    # sell_1_price
            self.sell_1_quantity = self.order_book['asks'][0][1]    # sell_1_quantity
            return True
        return False

    '''
    {
        'symbol': symbol,
        'timestamp': timestamp,
        'datetime': iso8601,
        'high': self.safe_float(ticker, 'highPrice'),
        'low': self.safe_float(ticker, 'lowPrice'),
        'bid': self.safe_float(ticker, 'bidPrice'),
        'bidVolume': self.safe_float(ticker, 'bidQty'),
        'ask': self.safe_float(ticker, 'askPrice'),
        'askVolume': self.safe_float(ticker, 'askQty'),
        'vwap': self.safe_float(ticker, 'weightedAvgPrice'),
        'open': self.safe_float(ticker, 'openPrice'),
        'close': self.safe_float(ticker, 'prevClosePrice'),
        'first': None,
        'last': self.safe_float(ticker, 'lastPrice'),
        'change': self.safe_float(ticker, 'priceChange'),
        'percentage': self.safe_float(ticker, 'priceChangePercent'),
        'average': None,
        'baseVolume': self.safe_float(ticker, 'volume'),
        'quoteVolume': self.safe_float(ticker, 'quoteVolume'),
        'info': ticker,
    }
    '''
    async def fetch_ticker(self):
        if await self.load_markets():
            self.ticker = await self.ex.fetch_ticker(self.symbol)
            self.ticker_time = int(time.time())
            return True
        return False



