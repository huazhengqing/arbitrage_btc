#!/usr/bin/python

import os
import sys
import time
import asyncio
import ccxt.async as ccxt
import numpy as np
import util

'''
交易费率
币安网   0.1% 交易手续费。（扣除收取到的资产）
'''


class exchange_data():
    def __init__(self, symbol, exchange):
        self.symbol = symbol         # BTC/USD
        self.ex = exchange
        
        self.symbol_1 = self.symbol.split('/')[0]       # BTC
        self.symbol_2 = self.symbol.split('/')[1]       # USD

        # load_markets
        self.market = None
        self.long_fee = 0.001        # 单笔交易费用 %
        self.short_fee = 0.001
        self.limits_amount_min = 0.000001    # 最小买卖数量
        self.limits_price_min = 0.000001    # 最小价格
        self.support_short = False    # 是否支持作空

        # fetch_balance
        self.balance = None
        self.symbol1_free = 0
        self.symbol1_used = 0
        self.symbol1_total = 0

        self.symbol2_free = 0
        self.symbol2_used = 0
        self.symbol2_total = 0

        # fetch_order_book
        self.order_book1 = None
        self.buy_1_price = 0.0
        self.buy_1_quantity = 0.0
        self.sell_1_price = 0.0
        self.sell_1_quantity = 0.0
        self.last_alive = 0

    # 检查是否支持 symbol，确定最小交易量，费用
    async def load_markets(self):
        self.symbol = await util.verify_symbol(self.ex, self.symbol)
        if self.symbol == '':
            return
        self.symbol_1 = self.symbol.split('/')[0]       # BTC
        self.symbol_2 = self.symbol.split('/')[1]       # USD

        self.market = self.ex.markets[self.symbol]
        self.long_fee = 0.0010        # 单笔交易费用 %
        self.short_fee = 0.0010  
        
        # 最小交易量
        self.limits_amount_min = self.market['limits']['amount']['min']
        self.limits_price_min = self.market['limits']['price']['min']

        self.support_short = True

        if self.ex.id == 'binance':
            self.long_fee = 0.0010    # %
            self.short_fee = 0.0010    # %
            self.support_short = False


        
    #  查看余额
    async def fetch_balance(self):
        err_timeout = 0
        err_ddos = 0
        err_auth = 0
        err_not_available = 0
        err_exchange = 0
        err_network = 0
        err = 0
        
        p = {}
        if self.ex.id == 'binance':
            p = {
                'recvWindow' : 60000,
            }
        while True:
            try:
                self.balance = await self.ex.fetch_balance(p)
                break
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
                return
            except ccxt.ExchangeNotAvailable as e:
                print(type(e).__name__, '=', e.args)
                return
            except ccxt.ExchangeError as e:
                print(type(e).__name__, '=', e.args)
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
        self.symbol1_free = self.balance[self.symbol_1]['free']        # 已经开仓了多少
        self.symbol1_used = self.balance[self.symbol_1]['used']
        self.symbol1_total = self.balance[self.symbol_1]['total']

        self.symbol2_free = self.balance[self.symbol_2]['free']        # 还有多少钱
        self.symbol2_used = self.balance[self.symbol_2]['used']
        self.symbol2_total = self.balance[self.symbol_2]['total']

    # 取深度信息，只取1层
    async def fetch_order_book(self):
        if self.last_alive >= int(time.time()):
            return True
        err_timeout = 0
        err_ddos = 0
        err_auth = 0
        err_not_available = 0
        err_exchange = 0
        err_network = 0
        err = 0
        p = {}
        if self.ex.id == 'binance':
            p = {
                'recvWindow' : 30000,
            }
        while True:
            try:
                self.order_book1 = await self.ex.fetch_order_book(self.symbol, 5)
                #self.order_book1 = await self.ex.fetch_order_book(self.symbol, 5, p)
                break
            except ccxt.RequestTimeout as e:
                print(type(e).__name__, '=', e.args)
                time.sleep(2)
                err_timeout = err_timeout + 1
                if err_timeout > 5:
                    return False
            except ccxt.DDoSProtection as e:
                print(type(e).__name__, '=', e.args)
                time.sleep(2)
                err_ddos = err_ddos + 1
                if err_ddos > 5:
                    return False
            except ccxt.AuthenticationError as e:
                print(type(e).__name__, '=', e.args)
                return False
            except ccxt.ExchangeNotAvailable as e:
                print(type(e).__name__, '=', e.args)
                return False
            except ccxt.ExchangeError as e:
                print(type(e).__name__, '=', e.args)
                return False
            except ccxt.NetworkError as e:
                print(type(e).__name__, '=', e.args)
                err_network = err_network + 1
                if err_network > 5:
                    return False
            except Exception as e:
                print(type(e).__name__, '=', e.args)
                err = err + 1
                if err > 5:
                    return False
        self.buy_1_price = self.order_book1['bids'][0][0]
        self.buy_1_quantity = self.order_book1['bids'][0][1]
        self.sell_1_price = self.order_book1['asks'][0][0]
        self.sell_1_quantity = self.order_book1['asks'][0][1]
        self.last_alive = int(time.time())
        return True
        
        