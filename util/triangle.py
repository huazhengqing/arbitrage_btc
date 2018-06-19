#!/usr/bin/python
import os
import sys
import math
import time
import logging
import asyncio
import traceback
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import ccxt.async as ccxt
dir_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_root)
import conf.conf
import util.util
import util.db_base
import util.exchange_data
from util.exchange_base import exchange_base
logger = util.util.get_log(__name__)



'''
交易对(symbol):  (base/quote) 例如： LTC/BTC
基准资产(base currency): LTC
定价资产(quote currency: BTC

3角套利原理: 
用两个市场（比如 BTC/USD，LTC/USD）的价格（分别记为P1，P2），计算出一个公允的 LTC/BTC 价格（P2/P1），
如果该公允价格跟实际的LTC/BTC市场价格（记为P3）不一致，就产生了套利机会

['base=基准资产', 'quote=定价资产', 'mid=中间资产']
['XXX', 'BTC/ETH/BNB/HT/OKB/', 'USDT/USD/CNY']
['XXX', 'ETH/BNB/HT/OKB/', 'BTC']
['XXX', 'BNB/HT/OKB/', 'ETH']
'''
class triangle(exchange_base):
    def __init__(self, exchange, base='EOS', quote='ETH', mid='USDT'):
        exchange_base.__init__(self, exchange)
        self.check(base, quote, mid)
        self.base = base
        self.quote = quote
        self.mid = mid
        self.base_quote = self.base + '/' + self.quote
        self.base_mid = self.base + '/' + self.mid
        self.quote_mid = self.quote + '/' + self.mid

        # 滑点 百分比，方便计算
        self.slippage_base_quote = 0.002  
        self.slippage_base_mid = 0.002
        self.slippage_quote_mid = 0.002

        # 吃单比例
        self.order_ratio_base_quote = 0.3
        self.order_ratio_base_mid = 0.3

        # 能用来操作的数量，用作限制。0表示不限制
        self.limit_base = 0.0
        self.limit_quote = 0.0
        self.limit_mid = 0.0

    '''
    ['base=基准资产', 'quote=定价资产', 'mid=中间资产']
    ['XXX', 'BTC/ETH/BNB/HT/OKB/', 'USDT/USD/CNY']
    ['XXX', 'ETH/BNB/HT/OKB/', 'BTC']
    ['XXX', 'BNB/HT/OKB/', 'ETH']
    '''
    def check(self, base, quote, mid):
        if mid in ['USD', 'USDT', 'CNY', 'JPY', 'EUR', 'CNH']:
            if quote not in ['BTC', 'ETH', 'BNB', 'HT', 'OKB']:
                raise Exception("check() base=" + base + ";quote=" + quote + ';mid=' + mid)
            return
        if mid in ['BTC']:
            if quote not in ['ETH', 'BNB', 'HT', 'OKB']:
                raise Exception("check() base=" + base + ";quote=" + quote + ';mid=' + mid)
            if base in ['USD', 'USDT', 'CNY', 'JPY', 'EUR', 'CNH']:
                raise Exception("check() base=" + base + ";quote=" + quote + ';mid=' + mid)
            return
        if mid in ['ETH']:
            if quote not in ['BNB', 'HT', 'OKB']:
                raise Exception("check() base=" + base + ";quote=" + quote + ';mid=' + mid)
            if base in ['BTC', 'USD', 'USDT', 'CNY', 'JPY', 'EUR', 'CNH']:
                raise Exception("check() base=" + base + ";quote=" + quote + ';mid=' + mid)
            return
        raise Exception("check() base=" + base + ";quote=" + quote + ';mid=' + mid)
    
    def to_string(self):
        return "triangle[{0}][{1},{2},{3}] ".format(self.ex.id, self.base, self.quote, self.mid)

    async def run_strategy(self):
        #logger.debug(self.to_string() + "run_strategy() start")
        await exchange_base.load_markets(self)
        exchange_base.check_symbol(self, self.base_quote)
        exchange_base.check_symbol(self, self.base_mid)
        exchange_base.check_symbol(self, self.quote_mid)

        await exchange_base.fetch_balance(self)

        # tudo: 需要改为同时取数据
        await exchange_base.fetch_order_book(self, self.base_quote, 5)
        base_quote_ask_1 = self.order_book[self.base_quote]['asks'][0][0]
        base_quote_bid_1 = self.order_book[self.base_quote]['bids'][0][0]
        self.slippage_base_quote = (base_quote_ask_1 - base_quote_bid_1)/base_quote_bid_1
        logger.debug(self.to_string() + "run_strategy() slippage_base_quote={0}".format(self.slippage_base_quote))

        await exchange_base.fetch_order_book(self, self.base_mid, 5)
        base_mid_ask_1 = self.order_book[self.base_mid]['asks'][0][0]
        base_mid_bid_1 = self.order_book[self.base_mid]['bids'][0][0]
        self.slippage_base_mid = (base_mid_ask_1 - base_mid_bid_1)/base_mid_bid_1
        logger.debug(self.to_string() + "run_strategy() slippage_base_mid={0}".format(self.slippage_base_mid))

        await exchange_base.fetch_order_book(self, self.quote_mid, 5)
        quote_mid_ask_1 = self.order_book[self.quote_mid]['asks'][0][0]
        quote_mid_bid_1 = self.order_book[self.quote_mid]['bids'][0][0]
        self.slippage_quote_mid = (quote_mid_ask_1 - quote_mid_bid_1)/quote_mid_bid_1
        logger.debug(self.to_string() + "run_strategy() slippage_quote_mid={0}".format(self.slippage_quote_mid))

        '''
        3角套利原理: 
        用两个市场（比如 BTC/USD，LTC/USD）的价格（分别记为P1，P2），计算出一个公允的 LTC/BTC 价格（P2/P1），
        如果该公允价格跟实际的LTC/BTC市场价格（记为P3）不一致，就产生了套利机会
        当公允价和市场价的价差比例大于所有市场的费率总和再加上滑点总和时，做三角套利才是盈利的。
        
        对应的套利条件就是：
        ltc_cny_buy_1_price > btc_cny_sell_1_price*ltc_btc_sell_1_price*(1+btc_cny_slippage)*(1+ltc_btc_slippage) / [(1-btc_cny_fee)*(1-ltc_btc_fee)*(1-ltc_cny_fee)*(1-ltc_cny_slippage)]
        考虑到各市场费率都在千分之几的水平，做精度取舍后，该不等式可以进一步化简成：
        (ltc_cny_buy_1_price/btc_cny_sell_1_price-ltc_btc_sell_1_price)/ltc_btc_sell_1_price > sum_slippage_fee
        基本意思就是：只有当公允价和市场价的价差比例大于所有市场的费率总和再加上滑点总和时，做三角套利才是盈利的。
        '''
        # 检查是否有套利空间
        diff_price_pos = (base_mid_bid_1 / quote_mid_ask_1 - base_quote_ask_1)/base_quote_ask_1
        diff_price_neg = (base_quote_bid_1 - base_mid_ask_1 / quote_mid_bid_1)/base_quote_bid_1
        cost = self.sum_slippage_fee()
        logger.debug(self.to_string() +  "run_strategy() 正循环差价={0}, 滑点+手续费={1}".format(diff_price_pos, cost))
        logger.debug(self.to_string() +  "run_strategy() 逆循环差价={0}, 滑点+手续费={1}".format(diff_price_neg, cost))
        # 检查正循环套利
        if diff_price_pos > cost:
            logger.info(self.to_string() +  "run_strategy() pos_cycle() 正循环差价={0}, 滑点+手续费={1}".format(diff_price_pos, cost))
            await self.pos_cycle(self.get_base_quote_buy_size())
        # 检查逆循环套利
        elif diff_price_neg > cost:
            logger.info(self.to_string() +  "run_strategy() neg_cycle() 逆循环差价={0}, 滑点+手续费={1}".format(diff_price_neg, cost))
            await self.neg_cycle(self.get_base_quote_sell_size())
        #logger.debug(self.to_string() + "run_strategy() end")

    def sum_slippage_fee(self):
        return self.slippage_base_quote + self.slippage_base_mid + self.slippage_quote_mid + self.fee_taker * 3

    def get_base_quote_buy_size(self):
        can_use_amount_base = 0.0
        if self.limit_base <= 0.0:
            can_use_amount_base = self.balance[self.base]['free']
        else:
            can_use_amount_base = min(self.balance[self.base]['free'], self.limit_base)
        
        can_use_amount_quote = 0.0
        if self.limit_quote <= 0.0:
            can_use_amount_quote = self.balance[self.quote]['free']
        else:
            can_use_amount_quote = min(self.balance[self.quote]['free'], self.limit_quote)

        can_use_amount_mid = 0.0
        if self.limit_mid <= 0.0:
            can_use_amount_mid = self.balance[self.mid]['free']
        else:
            can_use_amount_mid = min(self.balance[self.mid]['free'], self.limit_mid)

        market_buy_size = self.order_book[self.base_quote]["asks"][0][1] * self.order_ratio_base_quote
        base_mid_sell_size = self.order_book[self.base_mid]["bids"][0][1] * self.order_ratio_base_mid

        base_quote_off_reserve_buy_size = (can_use_amount_quote) /  self.order_book[self.base_quote]["asks"][0][0]
        quote_mid_off_reserve_buy_size = (can_use_amount_mid) / self.order_book[self.quote_mid]["asks"][0][0] / self.order_book[self.base_quote]["asks"][0][0]
        base_mid_off_reserve_sell_size = can_use_amount_base

        logger.info(self.to_string() + "计算数量：{0}，{1}，{2}，{3}，{4}".format(
            market_buy_size
            , base_mid_sell_size
            , base_quote_off_reserve_buy_size
            , quote_mid_off_reserve_buy_size
            , base_mid_off_reserve_sell_size)
            )

        size = min(market_buy_size, base_mid_sell_size, base_quote_off_reserve_buy_size, quote_mid_off_reserve_buy_size, base_mid_off_reserve_sell_size)
        return size

    def get_base_quote_sell_size(self):
        can_use_amount_base = 0.0
        if self.limit_base <= 0.0:
            can_use_amount_base = self.balance[self.base]['free']
        else:
            can_use_amount_base = min(self.balance[self.base]['free'], self.limit_base)
        
        can_use_amount_quote = 0.0
        if self.limit_quote <= 0.0:
            can_use_amount_quote = self.balance[self.quote]['free']
        else:
            can_use_amount_quote = min(self.balance[self.quote]['free'], self.limit_quote)

        can_use_amount_mid = 0.0
        if self.limit_mid <= 0.0:
            can_use_amount_mid = self.balance[self.mid]['free']
        else:
            can_use_amount_mid = min(self.balance[self.mid]['free'], self.limit_mid)

        market_sell_size = self.order_book[self.base_quote]["bids"][0][1] * self.order_ratio_base_quote
        base_mid_buy_size = self.order_book[self.base_mid]["asks"][0][1] * self.order_ratio_base_mid

        base_quote_off_reserve_sell_size = can_use_amount_base
        quote_mid_off_reserve_sell_size = (can_use_amount_quote) / self.order_book[self.base_quote]["bids"][0][0]
        base_mid_off_reserve_buy_size = (can_use_amount_mid) / self.order_book[self.base_mid]["asks"][0][0]

        logger.info(self.to_string() + "计算数量：{0}，{1}，{2}，{3}，{4}".format(
            market_sell_size
            , base_mid_buy_size
            , base_quote_off_reserve_sell_size
            , quote_mid_off_reserve_sell_size
            , base_mid_off_reserve_buy_size)
            )

        return min(market_sell_size, base_mid_buy_size, base_quote_off_reserve_sell_size, quote_mid_off_reserve_sell_size, base_mid_off_reserve_buy_size)

    '''
    正循环:
    LTC/BTC 买, LTC/CNY 卖，BTC/CNY 买
    '''
    async def pos_cycle(self, base_quote_buy_amount):
        logger.debug(self.to_string() + "pos_cycle({0}) start".format(base_quote_buy_amount))
        ret = await exchange_base.buy_cancel(self, self.base_quote, base_quote_buy_amount)
        logger.debug(self.to_string() + "pos_cycle({0}) buy_cancel() ret={1}".format(base_quote_buy_amount, ret))
        if ret['filled'] <= 0:
            logger.debug(self.to_string() + "pos_cycle({0}) return ret['filled'] <= 0 ret={1}".format(base_quote_buy_amount, ret))
            return
        quote_to_be_hedged = ret['filled'] * ret['price']
        logger.debug(self.to_string() + "pos_cycle({0}) Process hedged_sell({1}, {2})".format(base_quote_buy_amount, self.base_mid, ret['filled']))
        #p1 = multiprocessing.Process(target=self.hedged_sell, args=(self.base_mid, ret['filled']))
        p1 = threading.Thread(target=self.thread_hedged_sell, args=(self.base_mid, ret['filled']))
        p1.start()
        logger.debug(self.to_string() + "pos_cycle({0}) Process hedged_buy({1}, {2}={3}*{4})".format(base_quote_buy_amount, self.quote_mid, quote_to_be_hedged, ret['filled'], ret['price']))
        #p2 = multiprocessing.Process(target=self.hedged_buy, args=(self.quote_mid, quote_to_be_hedged))
        p2 = threading.Thread(target=self.thread_hedged_buy, args=(self.quote_mid, quote_to_be_hedged))
        p2.start()
        p1.join()
        p2.join()
        logger.debug(self.to_string() + "pos_cycle({0}) end".format(base_quote_buy_amount))

    '''
    逆循环:
    LTC/BTC 卖, LTC/CNY 买，BTC/CNY 卖
    '''
    async def neg_cycle(self, base_quote_sell_amount):
        logger.debug(self.to_string() + "neg_cycle({0}) start".format(base_quote_sell_amount))
        ret = await exchange_base.sell_cancel(self, self.base_quote, base_quote_sell_amount)
        logger.debug(self.to_string() + "neg_cycle({0}) sell_cancel() ret={1}".format(base_quote_sell_amount, ret))
        if ret['filled'] <= 0:
            logger.debug(self.to_string() + "neg_cycle({0}) return ret['filled'] <= 0 ret={1}".format(base_quote_sell_amount, ret))
            return
        quote_to_be_hedged = ret['filled'] * ret['price']
        logger.debug(self.to_string() + "neg_cycle({0}) hedged_buy({1}, {2}) Process".format(base_quote_sell_amount, self.base_mid, ret['filled']))
        #p1 = multiprocessing.Process(target=self.hedged_buy, args=(self.base_mid, ret['filled']))
        p1 = threading.Thread(target=self.thread_hedged_buy, args=(self.base_mid, ret['filled']))
        p1.start()
        logger.debug(self.to_string() + "neg_cycle({0}) hedged_sell({1}, {2}={3}*{4}) Process".format(base_quote_sell_amount, self.quote_mid, quote_to_be_hedged, ret['filled'], ret['price']))
        #p2 = multiprocessing.Process(target=self.hedged_sell, args=(self.quote_mid, quote_to_be_hedged))
        p2 = threading.Thread(target=self.thread_hedged_sell, args=(self.quote_mid, quote_to_be_hedged))
        p2.start()
        p1.join()
        p2.join()
        logger.debug(self.to_string() + "neg_cycle({0}) end".format(base_quote_sell_amount))

    async def hedged_buy(self, symbol, amount):
        logger.debug(self.to_string() + "hedged_buy({0}, {1}) start ".format(symbol, amount))
        '''
        try:
            ret = await exchange_base.buy_cancel(self, symbol, amount)
            logger.debug(self.to_string() + "hedged_buy({0}, {1}) buy_cancel() ret={2} ".format(symbol, amount, ret))
            if amount > ret['filled']:
                logger.debug(self.to_string() + "hedged_buy({0}, {1}) buy_all({2}, {3})".format(symbol, amount, symbol, amount - ret['filled']))
                await exchange_base.buy_all(self, symbol, amount - ret['filled'])
        except:
            logger.error(traceback.format_exc())
        '''
        logger.debug(self.to_string() + "hedged_buy({0}, {1}) buy_all({2}, {3})".format(symbol, amount, symbol, amount))
        await exchange_base.buy_all(self, symbol, amount)
        logger.debug(self.to_string() + "hedged_buy({0}, {1}) end ".format(symbol, amount))

    def thread_hedged_buy(self, symbol, amount):
        logger.debug(self.to_string() + "thread_hedged_buy({0}, {1}) start ".format(symbol, amount))
        loop2 = asyncio.new_event_loop()
        task = loop2.create_task(self.hedged_buy(symbol, amount))  
        loop2.run_until_complete(task)
        loop2.close()
        logger.debug(self.to_string() + "thread_hedged_buy({0}, {1}) end ".format(symbol, amount))

    async def hedged_sell(self, symbol, amount):
        logger.debug(self.to_string() + "hedged_sell({0}, {1}) start ".format(symbol, amount))
        '''
        try:
            ret = await exchange_base.sell_cancel(self, symbol, amount)
            logger.debug(self.to_string() + "hedged_sell({0}, {1}) sell_cancel() ret={2} ".format(symbol, amount, ret))
            if amount > ret['filled']:
                logger.debug(self.to_string() + "hedged_sell({0}, {1}) sell_all({2}, {3})".format(symbol, amount, symbol, amount - ret['filled']))
                await exchange_base.sell_all(self, symbol, amount - ret['filled'])
        except:
            logger.error(traceback.format_exc())
        '''
        logger.debug(self.to_string() + "hedged_sell({0}, {1}) sell_all({2}, {3})".format(symbol, amount, symbol, amount))
        await exchange_base.sell_all(self, symbol, amount)
        logger.debug(self.to_string() + "hedged_sell({0}, {1}) end ".format(symbol, amount))
    
    def thread_hedged_sell(self, symbol, amount):
        logger.debug(self.to_string() + "thread_hedged_sell({0}, {1}) start ".format(symbol, amount))
        loop2 = asyncio.new_event_loop()
        task = loop2.create_task(self.hedged_sell(symbol, amount))  
        loop2.run_until_complete(task)
        loop2.close()
        logger.debug(self.to_string() + "thread_hedged_sell({0}, {1}) end ".format(symbol, amount))
    







##########################################################################
# do
def do_triangle(list_id_base_quote_mid):
    logger.info("do_triangle({0}) start".format(list_id_base_quote_mid))
    tasks = []
    for target in list_id_base_quote_mid:
        logger.info("do_triangle({0}) target={1}".format(list_id_base_quote_mid, target))
        t = triangle(util.util.get_exchange(target['id'], True), target['base'], target['quote'], target['mid'])
        tasks.append(asyncio.ensure_future(t.run(t.run_strategy)))
    logger.info("do_triangle({0}) load all target".format(list_id_base_quote_mid))
    pending = asyncio.Task.all_tasks()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*pending))
    loop.close()
    logger.info("do_triangle({0}) end".format(list_id_base_quote_mid))







