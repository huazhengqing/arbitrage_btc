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

        # load_markets
        self.token_btc_market = None
        self.token_btc_limits_amount_min = 0.000001    # 最小买卖数量
        self.token_btc_limits_price_min = 0.000001    # 最小价格
        self.token_btc_precision_amount = 8
        self.token_btc_precision_price = 2
        
        self.token_eth_market = None
        self.token_eth_limits_amount_min = 0.000001    # 最小买卖数量
        self.token_eth_limits_price_min = 0.000001    # 最小价格
        self.token_eth_precision_amount = 8
        self.token_eth_precision_price = 2
        
        self.token_usdt_market = None
        self.token_usdt_limits_amount_min = 0.000001    # 最小买卖数量
        self.token_usdt_limits_price_min = 0.000001    # 最小价格
        self.token_usdt_precision_amount = 8
        self.token_usdt_precision_price = 2
        
        self.token_usd_market = None
        self.token_usd_limits_amount_min = 0.000001    # 最小买卖数量
        self.token_usd_limits_price_min = 0.000001    # 最小价格
        self.token_usd_precision_amount = 8
        self.token_usd_precision_price = 2

        # fetch_balance
        self.balance = None
        self.btc_free = 0
        self.btc_used = 0
        self.btc_total = 0

        self.eth_free = 0
        self.eth_used = 0
        self.eth_total = 0

        self.usdt_free = 0
        self.usdt_used = 0
        self.usdt_total = 0

        self.usd_free = 0
        self.usd_used = 0
        self.usd_total = 0

        # fetch_order_book
        self.token_btc_order_book = None
        self.token_btc_buy_1_price = 0.0
        self.token_btc_buy_1_quantity = 0.0
        self.token_btc_sell_1_price = 0.0
        self.token_btc_sell_1_quantity = 0.0

        self.token_eth_order_book = None
        self.token_eth_buy_1_price = 0.0
        self.token_eth_buy_1_quantity = 0.0
        self.token_eth_sell_1_price = 0.0
        self.token_eth_sell_1_quantity = 0.0
        
        self.token_usdt_order_book = None
        self.token_usdt_buy_1_price = 0.0
        self.token_usdt_buy_1_quantity = 0.0
        self.token_usdt_sell_1_price = 0.0
        self.token_usdt_sell_1_quantity = 0.0
        
        self.token_usd_order_book = None
        self.token_usd_buy_1_price = 0.0
        self.token_usd_buy_1_quantity = 0.0
        self.token_usd_sell_1_price = 0.0
        self.token_usd_sell_1_quantity = 0.0

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



    # 检查是否支持 symbol，确定最小交易量，费用
    def load_markets(self):
        self.token_btc_market = self.ex.markets[self.token_btc]
        self.token_btc_limits_amount_min = self.token_btc_market['limits']['amount']['min']    # 最小交易量
        self.token_btc_limits_price_min = self.token_btc_market['limits']['price']['min']
        self.token_btc_precision_amount = self.token_btc_market['precision']['amount']    # 精度
        self.token_btc_precision_price = self.token_btc_market['precision']['price']

        self.token_eth_market = self.ex.markets[self.token_eth]
        self.token_eth_limits_amount_min = self.token_eth_market['limits']['amount']['min']
        self.token_eth_limits_price_min = self.token_eth_market['limits']['price']['min']
        self.token_eth_precision_amount = self.token_eth_market['precision']['amount']
        self.token_eth_precision_price = self.token_eth_market['precision']['price']
        '''
        self.token_usdt_market = self.ex.markets[self.token_usdt]
        
        self.token_usd_market = self.ex.markets[self.token_usd]
        '''
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
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_timeout))
            except ccxt.DDoSProtection as e:
                err_ddos = err_ddos + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_ddos))
                time.sleep(30.0)
            except ccxt.AuthenticationError as e:
                err_auth = err_auth + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_auth))
                if err_auth > 5:
                    return False
            except ccxt.ExchangeNotAvailable as e:
                err_not_available = err_not_available + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_not_available))
                time.sleep(30.0)
                if err_not_available > 5:
                    return False
            except ccxt.ExchangeError as e:
                err_exchange = err_exchange + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_exchange))
                time.sleep(30.0)
                if err_exchange > 5:
                    return False
            except ccxt.NetworkError as e:
                err_network = err_network + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_network))
                time.sleep(10.0)
            except Exception as e:
                err = err + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_balance()' + type(e).__name__ + '=' + e.args.__str__())
                time.sleep(10.0)
                if err > 5:
                    return False

        self.btc_free = self.balance['BTC']['free']
        self.btc_used = self.balance['BTC']['used']
        self.btc_total = self.balance['BTC']['total']

        self.eth_free = self.balance['ETH']['free']
        self.eth_used = self.balance['ETH']['used']
        self.eth_total = self.balance['ETH']['total']

        self.usdt_free = self.balance['USDT']['free']
        self.usdt_used = self.balance['USDT']['used']
        self.usdt_total = self.balance['USDT']['total']
        '''
        self.usd_free = self.balance['USD']['free']
        self.usd_used = self.balance['USD']['used']
        self.usd_total = self.balance['USD']['total']
        '''
        return True

    # 取深度信息
    async def fetch_order_book(self):
        err_timeout = 0
        err_ddos = 0
        err_auth = 0
        err_not_available = 0
        err_exchange = 0
        err_network = 0
        err = 0
        '''
        p = {}
        if self.ex.id == 'binance':
            p = {
                'recvWindow' : 30000,
            }
        '''
        while True:
            try:
                self.token_btc_order_book = await self.ex.fetch_order_book(self.token_btc, 5)
                self.token_btc_buy_1_price = self.token_btc_order_book['bids'][0][0]
                self.token_btc_buy_1_quantity = self.token_btc_order_book['bids'][0][1]
                self.token_btc_sell_1_price = self.token_btc_order_book['asks'][0][0]
                self.token_btc_sell_1_quantity = self.token_btc_order_book['asks'][0][1]

                self.token_eth_order_book = await self.ex.fetch_order_book(self.token_eth, 5)
                self.token_eth_buy_1_price = self.token_eth_order_book['bids'][0][0]
                self.token_eth_buy_1_quantity = self.token_eth_order_book['bids'][0][1]
                self.token_eth_sell_1_price = self.token_eth_order_book['asks'][0][0]
                self.token_eth_sell_1_quantity = self.token_eth_order_book['asks'][0][1]

                self.token_usdt_order_book = await self.ex.fetch_order_book(self.token_usdt, 5)

                self.token_usd_order_book = await self.ex.fetch_order_book(self.token_usd, 5)

                break
            except ccxt.RequestTimeout as e:
                err_timeout = err_timeout + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_timeout))
            except ccxt.DDoSProtection as e:
                err_ddos = err_ddos + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_ddos))
                time.sleep(30.0)
            except ccxt.AuthenticationError as e:
                err_auth = err_auth + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_auth))
                if err_auth > 5:
                    return False
            except ccxt.ExchangeNotAvailable as e:
                err_not_available = err_not_available + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_not_available))
                time.sleep(30.0)
                if err_not_available > 5:
                    return False
            except ccxt.ExchangeError as e:
                err_exchange = err_exchange + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_exchange))
                time.sleep(30.0)
                if err_exchange > 5:
                    return False
            except ccxt.NetworkError as e:
                err_network = err_network + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_network))
                time.sleep(10.0)
            except Exception as e:
                err = err + 1
                self.logger.info(self.ex.id + ',' + self.token + ',fetch_order_book()' + type(e).__name__ + '=' + e.args.__str__())
                if err > 5:
                    return False

        self.last_alive = int(time.time())
        return True



    # 计算
    async def calc_token(self):
        
        self.profit = 0.0

        self.token = ''
        self.token_btc = ''
        self.token_eth = ''
        self.token_usdt = ''
        self.token_usd = ''

        err_timeout = 0
        err_ddos = 0
        err_auth = 0
        err_not_available = 0
        err_exchange = 0
        err_network = 0
        err = 0
        while True:
            try:
                allcoin = await self.ex.request('ticker/price', 'v3')
                break
            except ccxt.RequestTimeout as e:
                err_timeout = err_timeout + 1
                self.logger.info(self.ex.id + ',' + self.token + ',calc_token()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_timeout))
            except ccxt.DDoSProtection as e:
                err_ddos = err_ddos + 1
                self.logger.info(self.ex.id + ',' + self.token + ',calc_token()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_ddos))
                time.sleep(30.0)
            except ccxt.AuthenticationError as e:
                err_auth = err_auth + 1
                self.logger.info(self.ex.id + ',' + self.token + ',calc_token()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_auth))
                if err_auth > 5:
                    return False
            except ccxt.ExchangeNotAvailable as e:
                err_not_available = err_not_available + 1
                self.logger.info(self.ex.id + ',' + self.token + ',calc_token()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_not_available))
                time.sleep(30.0)
                if err_not_available > 5:
                    return False
            except ccxt.ExchangeError as e:
                err_exchange = err_exchange + 1
                self.logger.info(self.ex.id + ',' + self.token + ',calc_token()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_exchange))
                time.sleep(30.0)
                if err_exchange > 5:
                    return False
            except ccxt.NetworkError as e:
                err_network = err_network + 1
                self.logger.info(self.ex.id + ',' + self.token + ',calc_token()' + type(e).__name__ + '=' + e.args.__str__() + ',c=' + str(err_network))
                time.sleep(10.0)
            except Exception as e:
                err = err + 1
                self.logger.info(self.ex.id + ',' + self.token + ',calc_token()' + type(e).__name__ + '=' + e.args.__str__())
                if err > 5:
                    return False

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






