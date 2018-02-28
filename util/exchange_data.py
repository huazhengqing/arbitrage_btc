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

        # load_markets
        self.market = None
        self.long_fee = 0.001        # 单笔交易费用 %
        self.short_fee = 0.001
        self.limits_amount_min = 0.000001    # 最小买卖数量
        self.limits_price_min = 0.000001    # 最小价格
        self.precision_amount = 8
        self.precision_price = 2
        self.support_short = False    # 是否支持作空
        self.is_ok_market = False

        # fetch_balance
        self.balance = None
        self.symbol1_free = 0
        self.symbol1_used = 0
        self.symbol1_total = 0

        self.symbol2_free = 0
        self.symbol2_used = 0
        self.symbol2_total = 0

        # fetch_order_book
        self.order_book = None
        self.buy_1_price = 0.0
        self.buy_1_quantity = 0.0
        self.sell_1_price = 0.0
        self.sell_1_quantity = 0.0
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

    # 检查是否支持 symbol，确定最小交易量，费用
    async def load_markets(self):
        if self.is_ok_market == True:
            return True
        self.symbol = await util.verify_symbol(self.ex, self.symbol)
        if self.symbol == '':
            return False
        self.symbol_1 = self.symbol.split('/')[0]       # BTC
        self.symbol_2 = self.symbol.split('/')[1]       # USD

        self.market = self.ex.markets[self.symbol]
        
        # 最小交易量
        self.limits_amount_min = self.market['limits']['amount']['min']
        self.limits_price_min = self.market['limits']['price']['min']

        # 精度
        self.precision_amount = self.market['precision']['amount']
        self.precision_price = self.market['precision']['price']

        self.support_short = True
        self.long_fee = 0.0020        # 单笔交易费用 %
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

        self.is_ok_market = True
        return True


        
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
                err_timeout = err_timeout + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_timeout))
            except ccxt.DDoSProtection as e:
                err_ddos = err_ddos + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_ddos))
                time.sleep(30.0)
            except ccxt.AuthenticationError as e:
                err_auth = err_auth + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_auth))
                if err_auth > 5:
                    return False
            except ccxt.ExchangeNotAvailable as e:
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__())
                return False
            except ccxt.ExchangeError as e:
                err_exchange = err_exchange + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_exchange))
                time.sleep(10.0)
                if err_exchange > 5:
                    return False
            except ccxt.NetworkError as e:
                err_network = err_network + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_network))
                time.sleep(10.0)
            except Exception as e:
                err = err + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__())
                if err > 5:
                    return False
                    
        self.symbol1_free = self.balance[self.symbol_1]['free']        # 已经开仓了多少
        self.symbol1_used = self.balance[self.symbol_1]['used']
        self.symbol1_total = self.balance[self.symbol_1]['total']

        self.symbol2_free = self.balance[self.symbol_2]['free']        # 还有多少钱
        self.symbol2_used = self.balance[self.symbol_2]['used']
        self.symbol2_total = self.balance[self.symbol_2]['total']

        return True

    # 取深度信息
    async def fetch_order_book(self):
        if self.symbol == '':
            return False
            
        err_timeout = 0
        err_ddos = 0
        err_auth = 0
        err_not_available = 0
        err_exchange = 0
        err_network = 0
        err = 0
        p = {}
        '''
        if self.ex.id == 'binance':
            p = {
                'recvWindow' : 30000,
            }
        '''
        while True:
            try:
                self.order_book = await self.ex.fetch_order_book(self.symbol, 5)
                #self.order_book = await self.ex.fetch_order_book(self.symbol, 5, p)
                break
            except ccxt.RequestTimeout as e:
                err_timeout = err_timeout + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_timeout))
            except ccxt.DDoSProtection as e:
                err_ddos = err_ddos + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_ddos))
                time.sleep(30.0)
            except ccxt.AuthenticationError as e:
                err_auth = err_auth + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_auth))
                if err_auth > 5:
                    return False
            except ccxt.ExchangeNotAvailable as e:
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__())
                return False
            except ccxt.ExchangeError as e:
                err_exchange = err_exchange + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_exchange))
                time.sleep(10.0)
                if err_exchange > 5:
                    return False
            except ccxt.NetworkError as e:
                err_network = err_network + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_network))
                time.sleep(10.0)
            except Exception as e:
                err = err + 1
                self.logger.info(self.ex.id + ',' + self.symbol + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__())
                if err > 5:
                    return False

        self.buy_1_price = self.order_book['bids'][0][0]
        self.buy_1_quantity = self.order_book['bids'][0][1]
        self.sell_1_price = self.order_book['asks'][0][0]
        self.sell_1_quantity = self.order_book['asks'][0][1]
        self.last_alive = int(time.time())
        return True
        
        