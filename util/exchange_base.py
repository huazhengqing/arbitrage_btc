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
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
logger = util.util.get_log(__name__)


class exchange_base(object):
    def __init__(self, exchange = None):
        self.ex = exchange

        '''
        self.ex.markets['ETH/BTC']['limits']['amount']['min']   # 最小交易量 0.000001
        self.ex.markets['ETH/BTC']['limits']['price']['min']    # 最小价格 0.000001
        self.ex.markets['ETH/BTC']['precision']['amount']   # 精度 8
        self.ex.markets['ETH/BTC']['precision']['price']    # 精度 2
        '''

        # 手续费 百分比
        self.fee_taker = 0.001

        # 是否支持作空
        #self.support_short = False

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
        self.buy_1_quantity = 0.0
        self.sell_1_price = 0.0
        self.sell_1_quantity = 0.0
        self.slippage_value = 0.0
        self.slippage_ratio  = 0.0

        self.symbol_cur = ''
        self.base_cur = ''
        self.quote_cur = ''

        # 仓位再平衡
        self.rebalance_position_proportion = 0.5
        self.rebalance_time = 0
        
        
    '''
    async def __del__(self):
        if not self.ex is None:
            await self.ex.close()
    '''

    def to_string(self):
        return "exchange_base[{0}] ".format(self.ex.id)
    
    async def close(self):
        if not self.ex is None:
            await self.ex.close()

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
        #logger.debug(self.to_string() + "load_markets() start")
        if self.ex.markets is None:
            await self.ex.load_markets()
            #logger.debug(self.to_string() + "load_markets() markets={0}".format(self.ex.markets))
            #logger.debug(self.to_string() + "load_markets() symbols={0}".format(self.ex.symbols))
            #logger.debug(self.to_string() + "load_markets() fees={0}".format(self.ex.fees))
            #logger.debug(self.to_string() + "load_markets() api={0}".format(self.ex.api))
            #logger.debug(self.to_string() + "load_markets() has={0}".format(self.ex.has))
            #logger.debug(self.to_string() + "load_markets() urls={0}".format(self.ex.urls))
            #logger.debug(self.to_string() + "load_markets() currencies={0}".format(self.ex.currencies))
            self.fee_taker = max(self.ex.fees['trading']['taker'], self.fee_taker)
            logger.debug(self.to_string() + "load_markets() fee_taker={0}".format(self.fee_taker))
        #logger.debug(self.to_string() + "load_markets() end ")
        return self.ex.markets

    def check_symbol(self, symbol):
        if symbol not in self.ex.symbols:
            raise Exception(self.to_string() + "check_symbol({0}) error".format(symbol))

    '''
    self.balance['BTC']['free']     # 还有多少钱
    self.balance['BTC']['used']
    self.balance['BTC']['total']
    '''
    async def fetch_balance(self):
        #logger.debug(self.to_string() + "fetch_balance() start")
        p = {}
        if self.ex.id == 'binance':
            p = {
                'recvWindow' : 60000,
            }
        self.balance = await self.ex.fetch_balance(p)
        #logger.debug(self.to_string() + "fetch_balance() end balance={0}".format(self.balance))
        #logger.debug(self.to_string() + "fetch_balance() end")
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
        #logger.debug(self.to_string() + "fetch_ticker({0}) start".format(symbol))
        self.set_symbol(symbol)
        self.ticker = await self.ex.fetch_ticker(symbol)
        self.ticker_time = int(time.time())
        #logger.debug(self.to_string() + "fetch_ticker({0}) end ticker={1}".format(symbol, self.ticker))
        return self.ticker

    '''
    self.order_book[symbol]['bids'][0][0]    # buy_1_price
    self.order_book[symbol]['bids'][0][1]    # buy_1_quantity
    self.order_book[symbol]['asks'][0][0]    # sell_1_price
    self.order_book[symbol]['asks'][0][1]    # sell_1_quantity
    '''
    async def fetch_order_book(self, symbol, i = 5):
        #logger.debug(self.to_string() + "fetch_order_book({0}) start".format(symbol))
        if symbol == '':
            return
        self.order_book[symbol] = await self.ex.fetch_order_book(symbol, i)
        self.order_book_time = int(time.time())
        self.buy_1_price = self.order_book[symbol]['bids'][0][0]
        self.buy_1_quantity = self.order_book[symbol]['bids'][0][1]
        self.sell_1_price = self.order_book[symbol]['asks'][0][0]
        self.sell_1_quantity = self.order_book[symbol]['asks'][0][1]
        self.slippage_value = self.sell_1_price - self.buy_1_price
        self.slippage_ratio = (self.sell_1_price - self.buy_1_price) / self.buy_1_price
        self.set_symbol(symbol)
        #logger.debug(self.to_string() + "fetch_order_book({0}) end order_book[{1}]={2}".format(symbol, symbol, self.order_book[symbol]))
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
    # 限价买卖
    async def buy_cancel(self, symbol, amount):
        logger.debug(self.to_string() + "buy_cancel({0}, {1}) start".format(symbol, amount))
        if amount <= self.ex.markets[symbol]['limits']['amount']['min']:
            logger.debug(self.to_string() + "buy_cancel({0}, {1}) return min={2}".format(symbol, amount, self.ex.markets[symbol]['limits']['amount']['min']))
            return
        #await self.fetch_order_book(symbol, 5)
        price = self.order_book[symbol]['asks'][0][0]
        amount = util.util.downRound(amount, self.ex.markets[symbol]['precision']['amount'])
        ret = await self.ex.create_order(symbol, 'limit', 'buy', amount, price)
        ret = await self.ex.fetch_order(ret['id'], symbol)
        logger.debug(self.to_string() + "buy_cancel({0}, {1}) ret={2}".format(symbol, amount, ret))
        if ret['filled'] is None or ret['filled'] <= 0.0:
            logger.debug(self.to_string() + "buy_cancel({0}, {1}) ret['filled'] <= 0.0 ret={2}".format(symbol, amount, ret))
        # 订单没有成交全部，剩下的订单取消
        if ret['remaining'] is None or ret['remaining'] > 0:
            logger.debug(self.to_string() + "buy_cancel({0}, {1}) ret['remaining']={2}".format(symbol, amount, ret['remaining']))
            c = 0
            while c < 5:
                try:
                    c = c + 1
                    await self.ex.cancel_order(ret['id'])
                    logger.debug(self.to_string() + "buy_cancel({0}, {1}) cancel_order({2}) c={3}".format(symbol, amount, ret['id'], c))
                    break
                except:
                    logger.error(traceback.format_exc())
        logger.debug(self.to_string() + "buy_cancel({0}, {1}) end ret={2}".format(symbol, amount, ret))
        return ret

    async def sell_cancel(self, symbol, amount):
        logger.debug(self.to_string() + "sell_cancel({0}, {1}) start".format(symbol, amount))
        if amount <= self.ex.markets[symbol]['limits']['amount']['min']:
            logger.debug(self.to_string() + "sell_cancel({0}, {1}) return min={2}".format(symbol, amount, self.ex.markets[symbol]['limits']['amount']['min']))
            return
        #await self.fetch_order_book(symbol, 5)
        price = self.order_book[symbol]['bids'][0][0]
        amount = util.util.downRound(amount, self.ex.markets[symbol]['precision']['amount'])
        ret = await self.ex.create_order(symbol, 'limit', 'sell', amount, price)
        ret = await self.ex.fetch_order(ret['id'], symbol)
        logger.debug(self.to_string() + "sell_cancel({0}, {1}) ret={2}".format(symbol, amount, ret))
        if ret['filled'] is None or ret['filled'] <= 0.0:
            logger.debug(self.to_string() + "sell_cancel({0}, {1}) ret['filled'] <= 0.0 ret={2}".format(symbol, amount, ret))
        # 订单没有成交全部，剩下的订单取消
        if ret['remaining'] is None or ret['remaining'] > 0:
            logger.debug(self.to_string() + "sell_cancel({0}, {1}) ret['remaining']={2}".format(symbol, amount, ret['remaining']))
            c = 0
            while c < 5:
                try:
                    c = c + 1
                    await self.ex.cancel_order(ret['id'])
                    logger.debug(self.to_string() + "sell_cancel({0}, {1}) cancel_order({2}) c={3}".format(symbol, amount, ret['id'], c))
                    break
                except:
                    logger.error(traceback.format_exc())
        logger.debug(self.to_string() + "sell_cancel({0}, {1}) end ret={2}".format(symbol, amount, ret))
        return ret

    # 有交易所，只支持 limit order 
    async def buy_all(self, symbol, amount):
        logger.debug(self.to_string() + "buy_all({0}, {1}) start".format(symbol, amount))
        if amount < self.ex.markets[symbol]['limits']['amount']['min']:
            logger.debug(self.to_string() + "buy_all({0}, {1}) return amount.min={2}".format(symbol, amount, self.ex.markets[symbol]['limits']['amount']['min']))
            return
        #await self.fetch_order_book(symbol, 5)
        price = self.order_book[symbol]['asks'][0][0]
        amount = util.util.downRound(amount, self.ex.markets[symbol]['precision']['amount'])
        logger.debug(self.to_string() + "buy_all({0}, {1}) price={2}".format(symbol, amount, price))
        ret = None
        c = 0
        while c < 5:
            try:
                c = c + 1
                ret = await self.ex.create_order(symbol, 'limit', 'buy', amount, price)
                ret = await self.ex.fetch_order(ret['id'], symbol)
                logger.debug(self.to_string() + "buy_all({0}, {1}) create_order() ret={2} c={3}".format(symbol, amount, ret, c))
                break
            except:
                logger.error(traceback.format_exc())
        c = 0
        while ret['remaining'] is not None and ret['remaining'] >= self.ex.markets[symbol]['limits']['amount']['min']:
            try:
                price = self.order_book[symbol]['asks'][4][0]
                logger.debug(self.to_string() + "buy_all({0}, {1}) remaining price={2} c={3}".format(symbol, amount, price, c))
                ret = await self.ex.create_order(symbol, 'limit', 'buy', ret['remaining'], price)
                ret = await self.ex.fetch_order(ret['id'], symbol)
                logger.debug(self.to_string() + "buy_all({0}, {1}) remaining ret={2} c={3}".format(symbol, amount, ret, c))
                if ret['remaining'] is not None and ret['remaining'] >= self.ex.markets[symbol]['limits']['amount']['min']:
                    await self.fetch_order_book(symbol, 5)
            except:
                logger.error(traceback.format_exc())
                c = c + 1
                if c > 5:
                    raise
        logger.debug(self.to_string() + "buy_all({0}, {1}) end".format(symbol, amount))

    async def sell_all(self, symbol, amount):
        logger.debug(self.to_string() + "sell_all({0}, {1}) start".format(symbol, amount))
        if amount < self.ex.markets[symbol]['limits']['amount']['min']:
            logger.debug(self.to_string() + "sell_all({0}, {1}) return amount.min={2}".format(symbol, amount, self.ex.markets[symbol]['limits']['amount']['min']))
            return
        #await self.fetch_order_book(symbol, 5)
        price = self.order_book[symbol]['bids'][0][0]
        amount = util.util.downRound(amount, self.ex.markets[symbol]['precision']['amount'])
        ret = None
        c = 0
        while c < 5:
            try:
                c = c + 1
                ret = await self.ex.create_order(symbol, 'limit', 'sell', amount, price)
                ret = await self.ex.fetch_order(ret['id'], symbol)
                logger.debug(self.to_string() + "sell_all({0}, {1}) ret={2} c={3}".format(symbol, amount, ret, c))
                break
            except:
                logger.error(traceback.format_exc())
        c = 0
        while ret['remaining'] is not None and ret['remaining'] >= self.ex.markets[symbol]['limits']['amount']['min']:
            try:
                price = self.order_book[symbol]['bids'][4][0]
                logger.debug(self.to_string() + "sell_all({0}, {1}) remaining price={2} c={3}".format(symbol, amount, price, c))
                ret = await self.ex.create_order(symbol, 'limit', 'sell', ret['remaining'], price)
                ret = await self.ex.fetch_order(ret['id'], symbol)
                logger.debug(self.to_string() + "sell_all({0}, {1}) remaining ret={2} c={3}".format(symbol, amount, ret, c))
                if ret['remaining'] is not None and ret['remaining'] >= self.ex.markets[symbol]['limits']['amount']['min']:
                    await self.fetch_order_book(symbol, 5)
            except:
                logger.error(traceback.format_exc())
                c = c + 1
                if c > 5:
                    raise
        logger.debug(self.to_string() + "sell_all({0}, {1}) end".format(symbol, amount))

    # 仓位再平衡
    async def rebalance_position(self, symbol):
        #logger.debug(self.to_string() + "rebalance_position({0}) start".format(symbol))
        if self.rebalance_position_proportion <= 0.0:
            #logger.debug(self.to_string() + "rebalance_position({0}) return rebalance_position_proportion <= 0.0".format(symbol))
            return
        if int(time.time()) < self.rebalance_time + 60:
            #logger.debug(self.to_string() + "rebalance_position({0}) return  time  ".format(symbol))
            return
        self.rebalance_time = int(time.time())
        logger.debug(self.to_string() + "rebalance_position({0}) start".format(symbol))
        await self.load_markets()
        await self.fetch_balance()
        await self.fetch_ticker(symbol)
        self.set_symbol(symbol)
        pos_value = self.balance[self.base_cur]['free'] * self.ticker['bid']
        total_value = self.balance[self.quote_cur]['free'] + pos_value
        target_pos_value = total_value * self.rebalance_position_proportion
        if pos_value < target_pos_value * 0.8:
            buy_amount = (target_pos_value - pos_value) / self.ticker['bid']
            logger.debug(self.to_string() + "rebalance_position({0}) buy_all({1}) ".format(symbol, buy_amount))
            await self.buy_all(symbol, buy_amount)
        elif pos_value > target_pos_value * 1.2:
            sell_amount = (pos_value - target_pos_value) / self.ticker['bid']
            logger.debug(self.to_string() + "rebalance_position({0}) sell_all({1}) ".format(symbol, sell_amount))
            await self.sell_all(symbol, sell_amount)
        self.rebalance_time = int(time.time())
        logger.debug(self.to_string() + "rebalance_position({0}) end".format(symbol))

    # 评估账户 最小下注量
    async def balance_amount_min(self, symbol):
        logger.debug(self.to_string() + "balance_amount_min({0}) start".format(symbol))
        await self.load_markets()
        await self.fetch_balance()
        await self.fetch_ticker(symbol)
        self.set_symbol(symbol)
        pos_value = self.balance[self.base_cur]['free'] * self.ticker['bid']
        total_value = self.balance[self.quote_cur]['free'] + pos_value
        total_amount = total_value / self.ticker['ask'] * 0.97
        ret = max(self.ex.markets[symbol]['limits']['amount']['min'] * 2, total_amount * 0.02)
        logger.debug(self.to_string() + "balance_amount_min({0}) end ret={1}".format(symbol, ret))
        return ret

    # 异常处理
    async def run(self, func, *args, **kwargs):
        logger.info(self.to_string() + "run() start")
        err_timeout = 0
        err_ddos = 0
        err_auth = 0
        err_not_available = 0
        err_exchange = 0
        err_network = 0
        err = 0
        while True:
            try:
                logger.info(self.to_string() + "run() func")
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
                logger.info(traceback.format_exc())
                time.sleep(30)
            except ccxt.DDoSProtection:
                err_ddos = err_ddos + 1
                logger.error(traceback.format_exc())
                time.sleep(15)
            except ccxt.AuthenticationError:
                err_auth = err_auth + 1
                logger.error(traceback.format_exc())
                time.sleep(5)
                if err_auth > 5:
                    break
            except ccxt.ExchangeNotAvailable:
                err_not_available = err_not_available + 1
                logger.error(traceback.format_exc())
                time.sleep(30)
                if err_not_available > 5:
                    break
            except ccxt.ExchangeError:
                err_exchange = err_exchange + 1
                logger.error(traceback.format_exc())
                time.sleep(5)
                if err_exchange > 5:
                    break
            except ccxt.NetworkError:
                err_network = err_network + 1
                logger.error(traceback.format_exc())
                time.sleep(5)
                if err_network > 5:
                    break
            except Exception:
                err = err + 1
                logger.info(traceback.format_exc())
                break
            except:
                logger.error(traceback.format_exc())
                break
        if not self.ex is None:
            await self.ex.close()
        logger.info(self.to_string() + "run() end")

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
                logger.info("%s \t %10.4f"%(find_coin, abs(find_profit) - fee))








