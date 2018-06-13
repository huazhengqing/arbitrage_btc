#!/usr/bin/python

import os
import sys
import math
import time
import logging
import asyncio
import traceback
import multiprocessing
import numpy as np
import ccxt.async as ccxt

import conf.conf
import util.util


class exchange_base:
    def __init__(self, exchange = None):
        self.ex = exchange

        '''
        self.ex.markets['ETH/BTC']['limits']['amount']['min']   # 最小交易量 0.000001
        self.ex.markets['ETH/BTC']['limits']['price']['min']    # 最小价格 0.000001
        self.ex.markets['ETH/BTC']['precision']['amount']   # 精度 8
        self.ex.markets['ETH/BTC']['precision']['price']    # 精度 2
        '''
        self.markets = None

        # 手续费 百分比
        self.fee_taker = 0.001

        # 是否支持作空
        self.support_short = False

        '''
        self.balance['BTC']['free']     # 还有多少钱
        self.balance['BTC']['used']
        self.balance['BTC']['total']
        '''
        self.balance = None
        
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
        self.ticker = None
        self.ticker_time = 0

        '''
        self.order_book[symbol]['bids'][0][0]    # buy_1_price
        self.order_book[symbol]['bids'][0][1]    # buy_1_quantity
        self.order_book[symbol]['asks'][0][0]    # sell_1_price
        self.order_book[symbol]['asks'][0][1]    # sell_1_quantity
        '''
        self.order_book = dict()
        self.order_book_time = 0
        self.buy_1_price = 0.0
        self.sell_1_price = 0.0
        self.slippage_value = 0.0
        self.slippage_ratio  = 0.0

        self.symbol_cur = ''
        self.base_cur = ''
        self.quote_cur = ''

        # 仓位再平衡
        self.rebalanced_position_proportion = 0.5
        
        self.logger = None

    '''
    async def __del__(self):
        if not self.ex is None:
            await self.ex.close()
    '''

    def init_log(self, name = __name__):
        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)-8s: %(message)s')
        file_handler = logging.FileHandler(conf.conf.dir_log + name + "_{0}.log".format(int(time.time())), mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    def set_symbol(self, symbol):
        self.symbol_cur = symbol         # BTC/USD
        self.base_cur = symbol.split('/')[0]       # BTC
        self.quote_cur = symbol.split('/')[1]       # USD


    '''
    self.ex.markets['ETH/BTC']['limits']['amount']['min']   # 最小交易量 0.000001
    self.ex.markets['ETH/BTC']['limits']['price']['min']    # 最小价格 0.000001
    self.ex.markets['ETH/BTC']['precision']['amount']   # 精度 8
    self.ex.markets['ETH/BTC']['precision']['price']    # 精度 2
    '''
    async def load_markets(self):
        if self.ex.markets is None:
            await self.ex.load_markets()
            self.fee_taker = max(self.ex.fees['trading']['taker'], self.fee_taker)
            self.logger.debug(self.ex.id + ' symbols: ' + ', '.join(self.ex.symbols))
        return self.ex.markets

    def check_symbol(self, symbol):
        if symbol not in self.ex.symbols:
            raise Exception("[" + self.ex.id +"] 没有此symbol=" + symbol)

    '''
    self.balance['BTC']['free']     # 还有多少钱
    self.balance['BTC']['used']
    self.balance['BTC']['total']
    '''
    async def fetch_balance(self):
        p = {}
        if self.ex.id == 'binance':
            p = {
                'recvWindow' : 60000,
            }
        self.balance = await self.ex.fetch_balance(p)
        return self.balance

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
    async def fetch_ticker(self, symbol):
        self.set_symbol(symbol)
        self.ticker = await self.ex.fetch_ticker(symbol)
        self.ticker_time = int(time.time())
        return self.ticker

    # 取 ticker 数据，存入 db 中
    async def fetch_ticker_to_db(self, symbol, db):
        await self.fetch_ticker(symbol)
        db.add_bid_ask(self.ex.id, self.ticker_time, self.ticker['bid'], self.ticker['ask'])
        s = util.util.to_str(symbol, self.ex.id, self.ticker_time, self.ticker['bid'], self.ticker['ask'])
        self.logger.info(s)

    async def init_db_table(self, symbol, db):
        await self.load_markets()
        self.check_symbol(symbol)
        self.set_symbol(symbol)
        db.create_table_exchange(self.ex.id)

    '''
    self.order_book[symbol]['bids'][0][0]    # buy_1_price
    self.order_book[symbol]['bids'][0][1]    # buy_1_quantity
    self.order_book[symbol]['asks'][0][0]    # sell_1_price
    self.order_book[symbol]['asks'][0][1]    # sell_1_quantity
    '''
    async def fetch_order_book(self, symbol, i = 5):
        self.order_book[symbol] = await self.ex.fetch_order_book(symbol, i)
        self.order_book_time = int(time.time())
        self.buy_1_price = self.order_book[symbol]['bids'][0][0]
        self.sell_1_price = self.order_book[symbol]['asks'][0][0]
        self.slippage_value = self.sell_1_price - self.buy_1_price
        self.slippage_ratio = (self.sell_1_price - self.buy_1_price) / self.buy_1_price
        self.set_symbol(symbol)
        return self.order_book

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
    {
        'id':                '12345-67890:09876/54321', // string
        'datetime':          '2017-08-17 12:42:48.000', // ISO8601 datetime of 'timestamp' with milliseconds
        'timestamp':          1502962946216, // order placing/opening Unix timestamp in milliseconds
        'lastTradeTimestamp': 1502962956216, // Unix timestamp of the most recent trade on this order
        'status':     'open',         // 'open', 'closed', 'canceled'
        'symbol':     'ETH/BTC',      // symbol
        'type':       'limit',        // 'market', 'limit'
        'side':       'buy',          // 'buy', 'sell'
        'price':       0.06917684,    // float price in quote currency
        'amount':      1.5,           // ordered amount of base currency
        'filled':      1.1,           // filled amount of base currency
        'remaining':   0.4,           // remaining amount to fill
        'cost':        0.076094524,   // 'filled' * 'price'
        'trades':    [ ... ],         // a list of order trades/executions
        'fee': {                      // fee info, if available
            'currency': 'BTC',        // which currency the fee is (usually quote)
            'cost': 0.0009,           // the fee amount in that currency
            'rate': 0.002,            // the fee rate (if available)
        },
        'info': { ... },              // the original unparsed order structure as is
    }
    '''
    async def buy_cancel(self, symbol, amount):
        ret = await self.ex.create_order(symbol, 'limit', 'buy', amount, self.order_book[symbol]['asks'][0][0], {'leverage': 1})
        # 订单没有成交全部，剩下的订单取消
        if ret['remaining'] > 0:
            await self.ex.cancel_order(ret['id'])
        return ret

    async def sell_cancel(self, symbol, amount):
        ret = await self.ex.create_order(symbol, 'limit', 'sell', amount, self.order_book[symbol]['bids'][0][0], {'leverage': 1})
        # 订单没有成交全部，剩下的订单取消
        if ret['remaining'] > 0:
            await self.ex.cancel_order(ret['id'])
        return ret

    async def buy_all(self, symbol, amount):
        ret = await self.ex.create_order(symbol, 'market', 'buy', amount, None, {'leverage': 1})
        while ret['remaining'] > 0:
            ret = await self.ex.create_order(symbol, 'market', 'buy', ret['remaining'], None, {'leverage': 1})

    async def sell_all(self, symbol, amount):
        ret = await self.ex.create_order(symbol, 'market', 'sell', amount, None, {'leverage': 1})
        while ret['remaining'] > 0:
            ret = await self.ex.create_order(symbol, 'market', 'sell', ret['remaining'], None, {'leverage': 1})

    # 仓位再平衡
    async def rebalance_position(self, symbol):
        if self.rebalanced_position_proportion <= 0.0:
            return
        self.set_symbol(symbol)
        await self.fetch_ticker(symbol)
        await self.fetch_balance()
        pos_value = self.balance[self.base_cur]['free'] * self.ticker['bid']
        total_pos = self.balance[self.quote_cur]['free'] + pos_value
        target_pos_value = total_pos * self.rebalanced_position_proportion
        if target_pos_value > pos_value + self.ex.markets[symbol]['limits']['amount']['min'] * self.ticker['ask']:  # need to buy
            await self.buy_all(symbol, target_pos_value - pos_value)
        elif pos_value > target_pos_value + self.ex.markets[symbol]['limits']['amount']['min'] * self.ticker['bid']:  # need to sell
            sell_amount = (pos_value - target_pos_value) / self.ticker['bid']
            await self.sell_all(symbol, sell_amount)











    # 异常处理
    async def run(self, func, *args, **kwargs):
        err_timeout = 0
        err_ddos = 0
        err_auth = 0
        err_not_available = 0
        err_exchange = 0
        err_network = 0
        err = 0
        while True:
            try:
                await func(*args, **kwargs)
                err_timeout = 0
                err_ddos = 0
                err_auth = 0
                err_not_available = 0
                err_exchange = 0
                err_network = 0
                err = 0
            except ccxt.RequestTimeout:
                err_timeout = err_timeout + 1
                self.logger.error(traceback.format_exc())
                time.sleep(10)
            except ccxt.DDoSProtection:
                err_ddos = err_ddos + 1
                self.logger.error(traceback.format_exc())
                time.sleep(15)
            except ccxt.AuthenticationError:
                err_auth = err_auth + 1
                self.logger.error(traceback.format_exc())
                time.sleep(5)
                if err_auth > 5:
                    break
            except ccxt.ExchangeNotAvailable:
                err_not_available = err_not_available + 1
                self.logger.error(traceback.format_exc())
                time.sleep(5)
                if err_not_available > 5:
                    break
            except ccxt.ExchangeError:
                err_exchange = err_exchange + 1
                self.logger.error(traceback.format_exc())
                time.sleep(5)
                if err_exchange > 5:
                    break
            except ccxt.NetworkError:
                err_network = err_network + 1
                self.logger.error(traceback.format_exc())
                time.sleep(5)
                if err_network > 5:
                    break
            except Exception:
                err = err + 1
                self.logger.info(traceback.format_exc())
                break
            except:
                self.logger.error(traceback.format_exc())
                break
        if not self.ex is None:
            await self.ex.close()
        self.logger.debug(self.ex.id + ' run() end.')




    # 3角套利，查找可以套利的币
    async def triangle_find_best_profit(self, quote1 = "BTC", quote2 = "ETH"):
        btc_coin = dict()
        eth_coin = dict()
        allcoin = await self.ex.request('ticker/price', 'v3')
        for item in allcoin:
            coin = item["symbol"][:-3]
            quote = item["symbol"][-3:]
            if quote == quote1:
                btc_coin[coin] = item
            if quote == quote2:
                eth_coin[coin] = item

        ethprice = float(btc_coin[quote2]["price"])

        #print("币种------ETH记价---ETH/BTC价---转成BTC价---直接BTC价--价差比")
        find_coin = ''
        find_profit = 0.0
        for k, v in btc_coin.items():
            if k in eth_coin:
                coin2btc = float(ethprice) * float(eth_coin[k]["price"])
                btcbuy  = float(btc_coin[k]["price"])
                profit = (btcbuy - coin2btc) / coin2btc
                if abs(profit) > 0.008:
                    #print("%s\t%10.8f  %10.8f  %10.8f  %10.8f  %s"%(k, float(eth_coin[k]["price"]), round(ethprice,8), round(coin2btc, 8), btcbuy, profit))
                    if abs(profit) > abs(find_profit):
                        find_coin = k
                        find_profit = profit

        if find_coin != '':
            coin_btc = find_coin + '/' + quote1
            coin_eth = find_coin + '/' + quote2
            fee = 0.003
            await self.fetch_order_book(coin_btc)
            fee += self.slippage_ratio
            #print(coin_btc, ': bids=', self.buy_1_price, '|asks=', self.sell_1_price, '|spread%=', round(self.slippage_ratio, 4))
            await self.fetch_order_book(coin_eth) 
            fee += self.slippage_ratio
            #print(coin_eth, ': bids=', self.buy_1_price, '|asks=', self.sell_1_price, '|spread%=', round(self.slippage_ratio, 4))
            if abs(find_profit) > fee:
                self.logger.info("%s \t %10.4f"%(find_coin, abs(find_profit) - fee))
        



    # 找出 交易所共同支持的 交易对
    async def arbitrage_find_symbols(self, ids):
        exchanges = {}
        for id in ids:
            exchanges[id] = util.util.get_exchange(id, False)
            await exchanges[id].load_markets()
            await exchanges[id].close()
        allSymbols = [symbol for id in ids for symbol in exchanges[id].symbols]
        uniqueSymbols = list(set(allSymbols))
        arbitrableSymbols = sorted([symbol for symbol in uniqueSymbols if allSymbols.count(symbol) > 1])

        s = util.util.to_str(' symbol          | ' + ''.join([' {:<15} | '.format(id) for id in ids]))
        self.logger.info(s)
        s = util.util.to_str(''.join(['-----------------+-' for x in range(0, len(ids) + 1)]))
        self.logger.info(s)

        for symbol in arbitrableSymbols:
            string = ' {:<15} | '.format(symbol)
            for id in ids:
                string += ' {:<15} | '.format(id if symbol in exchanges[id].symbols else '')
            self.logger.info(string)









