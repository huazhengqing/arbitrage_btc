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


class three_data():
    def __init__(self, exchange):
        self.ex = exchange
        
        self.long_fee = 0.001        # 单笔交易费用 %
        self.short_fee = 0.001

        '''
        self.token_btc_market['limits']['amount']['min']    # 最小交易量
        self.token_btc_market['limits']['price']['min']
        self.token_btc_market['precision']['amount']    # 精度
        self.token_btc_market['precision']['price']
        '''
        # load_markets
        self.eth_btc_market = None
        self.token_btc_market = None
        self.token_eth_market = None
        self.token_usdt_market = None
        self.token_usd_market = None

        '''
        self.balance['BTC']['free']
        self.balance['BTC']['used']
        self.balance['BTC']['total']
        '''
        # fetch_balance
        self.balance = None

        '''
        self.token_btc_order_book['bids'][0][0]    # buy_1_price
        self.token_btc_order_book['bids'][0][1]    # buy_1_quantity
        self.token_btc_order_book['asks'][0][0]    # sell_1_price
        self.token_btc_order_book['asks'][0][1]    # sell_1_quantity
        '''
        # fetch_order_book
        self.eth_btc_order_book = None
        self.token_btc_order_book = None
        self.token_eth_order_book = None
        self.token_usdt_order_book = None
        self.token_usd_order_book = None
        self.last_alive = 0

        # log
        self.logger = logging.getLogger(__name__)
        self.formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
        self.file_handler = logging.FileHandler(bz_conf.log_dir + "/mm.log")
        self.file_handler.setFormatter(self.formatter)
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.formatter = self.formatter
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
        self.logger.setLevel(logging.INFO)

        self.profit = 0.0

        self.token = ''
        self.token_btc = ''
        self.token_eth = ''
        self.token_usdt = ''
        self.token_usd = ''

    async def load_markets(self):
        await self.ex.load_markets()
        self.eth_btc_market = self.ex.markets['ETH/BTC']
        
        self.long_fee = 0.0020        # 单笔交易费用
        self.short_fee = 0.0020

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

    def load_token_markets(self):
        self.token_btc_market = self.ex.markets[self.token_btc]
        self.token_eth_market = self.ex.markets[self.token_eth]
        #self.token_usdt_market = self.ex.markets[self.token_usdt]
        #self.token_usd_market = self.ex.markets[self.token_usd]

    #  查看余额
    async def fetch_balance(self):
        p = {}
        if self.ex.id == 'binance':
            p = {
                'recvWindow' : 60000,
            }
        self.balance = await self.ex.fetch_balance(p)

    # 取深度信息
    async def fetch_order_book(self):
        self.eth_btc_order_book = await self.ex.fetch_order_book('ETH/BTC', 5)
        self.token_btc_order_book = await self.ex.fetch_order_book(self.token_btc, 5)
        self.token_eth_order_book = await self.ex.fetch_order_book(self.token_eth, 5)
        #self.token_usdt_order_book = await self.ex.fetch_order_book(self.token_usdt, 5)
        #self.token_usd_order_book = await self.ex.fetch_order_book(self.token_usd, 5)
        self.last_alive = int(time.time())

    # 计算
    async def calc_token(self):
        self.profit = 0.0
        self.token = ''
        self.token_btc = ''
        self.token_eth = ''
        self.token_usdt = ''
        self.token_usd = ''
        allcoin = await self.ex.request('ticker/price', 'v3')
        btc_coin = dict()
        eth_coin = dict()
        coin_profit = dict()
        for item in allcoin:
            coin = item["symbol"][:-3]
            quote = item["symbol"][-3:]
            if quote == "BTC":
                btc_coin[coin] = item
            if quote == "ETH":
                eth_coin[coin] = item

        ethprice = float(btc_coin["ETH"]["price"])

        for k, v in btc_coin.items():
            if k in eth_coin:
                coin2btc = float(ethprice) * float(eth_coin[k]["price"])
                btcbuy  = float(btc_coin[k]["price"])
                profit = (btcbuy - coin2btc) / coin2btc
                if abs(profit) > 0.008:
                    coin_profit[k] = profit
                    if abs(profit) > abs(self.profit):
                        self.token = k
                        self.profit = profit
        
        if abs(self.profit) > 0.0:
            self.token_btc = self.token + '/BTC'
            self.token_eth = self.token + '/ETH'
            self.token_usdt = self.token + '/USDT'
            self.token_usd = self.token + '/USD'
            return True

        return False

    '''
    # 订单结构
    {
        'id': str(order['id']),
        'timestamp': timestamp,
        'datetime': self.iso8601(timestamp),
        'status': status,
        'symbol': symbol,
        'type': order['ord_type'],
        'side': order['side'],
        'price': float(order['price']),
        'amount': float(order['volume']),
        'filled': float(order['executed_volume']),
        'remaining': float(order['remaining_volume']),
        'trades': None,
        'fee': None,
        'info': order,
    }
    '''
    async def op_token(self):
        if (self.profit) > 0.0:
            # 买入 ETH/BTC -> 买入 xxx/ETH -> 卖出 xxx/BTC
            token_amount = self.token_btc_order_book['bids'][0][1] / 5
            buy_amount = token_amount * self.token_eth_order_book['asks'][0][0] * self.eth_btc_order_book['asks'][0][0]

            ret1 = await self.ex.create_order('ETH/BTC', 'market', 'buy', buy_amount, None, {'leverage': 1})
            if ret1['remaining'] > 0:
                self.ex.cancel_order(ret1['id'])
            if ret1['filled'] <= 0:
                return

            ret2 = await self.ex.create_order(self.token_eth, 'market', 'buy', ret1['filled'], None, {'leverage': 1})
            token_filled = ret2['filled']
            while ret2['remaining'] > 0:
                ret2 = await self.ex.create_order(self.token_eth, 'market', 'buy', ret2['remaining'], None, {'leverage': 1})
                token_filled += ret2['filled']

            ret3 = await self.ex.create_order(self.token_btc, 'market', 'sell', token_filled, None, {'leverage': 1})
            while ret3['remaining'] > 0:
                ret3 = await self.ex.create_order(self.token_btc, 'market', 'sell', ret3['remaining'], None, {'leverage': 1})

        elif (self.profit) < 0.0:
            # 买入 xxx/BTC -> 卖出 xxx/ETH -> 卖出 ETH/BTC
            token_amount = self.token_btc_order_book['bids'][0][1] / 5











