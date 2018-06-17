#!/usr/bin/python
import os
import sys
import math
import time
import logging
import asyncio
import traceback
import multiprocessing
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

        # 余额预留数量
        self.base_quote_quote_reserve = 0.0    
        self.base_quote_base_reserve = 0.0
        self.quote_mid_mid_reserve = 0.0
        self.quote_mid_quote_reserve = 0.0
        self.base_mid_base_reserve = 0.0
        self.base_mid_mid_reserve = 0.0


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

    async def run_strategy(self):
        await exchange_base.load_markets(self)
        exchange_base.check_symbol(self, self.base_quote)
        exchange_base.check_symbol(self, self.base_mid)
        exchange_base.check_symbol(self, self.quote_mid)

        await exchange_base.fetch_balance(self)
        
        self.order_book = dict()

        await exchange_base.fetch_order_book(self, self.base_quote, 5)
        base_quote_ask_1 = self.order_book[self.base_quote]['asks'][0][0]
        base_quote_bid_1 = self.order_book[self.base_quote]['bids'][0][0]
        self.slippage_base_quote = (base_quote_ask_1 - base_quote_bid_1)/base_quote_bid_1

        await exchange_base.fetch_order_book(self, self.base_mid, 5)
        base_mid_ask_1 = self.order_book[self.base_mid]['asks'][0][0]
        base_mid_bid_1 = self.order_book[self.base_mid]['bids'][0][0]
        self.slippage_base_mid = (base_mid_ask_1 - base_mid_bid_1)/base_mid_bid_1

        await exchange_base.fetch_order_book(self, self.quote_mid, 5)
        quote_mid_ask_1 = self.order_book[self.quote_mid]['asks'][0][0]
        quote_mid_bid_1 = self.order_book[self.quote_mid]['bids'][0][0]
        self.slippage_quote_mid = (quote_mid_ask_1 - quote_mid_bid_1)/quote_mid_bid_1

        '''
        三角套利的基本思路是，用两个市场（比如BTC/CNY，LTC/CNY）的价格（分别记为P1，P2），计算出一个公允的LTC/BTC价格（P2/P1），
        如果该公允价格跟实际的LTC/BTC市场价格（记为P3）不一致，就产生了套利机会
        
        对应的套利条件就是：
        ltc_cny_buy_1_price > btc_cny_sell_1_price*ltc_btc_sell_1_price*(1+btc_cny_slippage)*(1+ltc_btc_slippage) / [(1-btc_cny_fee)*(1-ltc_btc_fee)*(1-ltc_cny_fee)*(1-ltc_cny_slippage)]
        考虑到各市场费率都在千分之几的水平，做精度取舍后，该不等式可以进一步化简成：
        (ltc_cny_buy_1_price/btc_cny_sell_1_price-ltc_btc_sell_1_price)/ltc_btc_sell_1_price > sum_slippage_fee
        基本意思就是：只有当公允价和市场价的价差比例大于所有市场的费率总和再加上滑点总和时，做三角套利才是盈利的。
        '''

        # 检查是否有套利空间
        # 检查正循环套利
        if (base_mid_bid_1 / quote_mid_ask_1 - base_quote_ask_1)/base_quote_ask_1 > self.sum_slippage_fee():
            d = (base_mid_bid_1 / quote_mid_ask_1 - base_quote_ask_1)/base_quote_ask_1
            s = self.ex.id + "正循环差价：{0},滑点+手续费:{1}".format(d, self.sum_slippage_fee())
            logger.info(s)
            await self.pos_cycle(self.get_market_buy_size())
        # 检查逆循环套利
        elif (base_quote_bid_1 - base_mid_ask_1 / quote_mid_bid_1)/base_quote_bid_1 > self.sum_slippage_fee():
            d = (base_quote_bid_1 - base_mid_ask_1 / quote_mid_bid_1)/base_quote_bid_1
            s = "逆循环差价：{0},滑点+手续费:{1}".format(d, self.sum_slippage_fee())
            logger.info(s)
            await self.neg_cycle(self.get_market_sell_size())

    def sum_slippage_fee(self):
        return self.slippage_base_quote + self.slippage_base_mid + self.slippage_quote_mid + self.fee_taker * 3

    '''
    # 计算最保险的下单数量
    1.	LTC/BTC卖方盘口吃单数量：ltc_btc_sell1_quantity*order_ratio_ltc_btc，其中ltc_btc_sell1_quantity 代表LTC/BTC卖一档的数量，
        order_ratio_ltc_btc代表本策略在LTC/BTC盘口的吃单比例
    2.	LTC/CNY买方盘口吃单数量：ltc_cny_buy1_quantity*order_ratio_ltc_cny，其中order_ratio_ltc_cny代表本策略在LTC/CNY盘口的吃单比例
    3.	LTC/BTC账户中可以用来买LTC的BTC额度及可以置换的LTC个数：
        btc_available - btc_reserve，可以置换成
        (btc_available – btc_reserve)/ltc_btc_sell1_price个LTC
        其中，btc_available表示该账户中可用的BTC数量，btc_reserve表示该账户中应该最少预留的BTC数量
        （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
    4.	BTC/CNY账户中可以用来买BTC的CNY额度及可以置换的BTC个数和对应的LTC个数：
        cny_available - cny_reserve, 可以置换成
        (cny_available-cny_reserve)/btc_cny_sell1_price个BTC，
        相当于
        (cny_available-cny_reserve)/btc_cny_sell1_price/ltc_btc_sell1_price
        个LTC
        其中：cny_available表示该账户中可用的人民币数量，cny_reserve表示该账户中应该最少预留的人民币数量
        （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
    5.	LTC/CNY账户中可以用来卖的LTC额度：
        ltc_available – ltc_reserve
        其中，ltc_available表示该账户中可用的LTC数量，ltc_reserve表示该账户中应该最少预留的LTC数量
        （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
    '''
    def get_market_buy_size(self):
        market_buy_size = self.order_book[self.base_quote]["asks"][0][1] * self.order_ratio_base_quote
        base_mid_sell_size = self.order_book[self.base_mid]["bids"][0][1] * self.order_ratio_base_mid
        base_quote_off_reserve_buy_size = (self.balance[self.quote]['free'] - self.base_quote_quote_reserve) /  self.order_book[self.base_quote]["asks"][0][0]
        quote_mid_off_reserve_buy_size = (self.balance[self.mid]['free'] - self.quote_mid_mid_reserve) / self.order_book[self.quote_mid]["asks"][0][0] / self.order_book[self.base_quote]["asks"][0][0]
        base_mid_off_reserve_sell_size = self.balance[self.base]['free'] - self.base_mid_base_reserve
        logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(
            market_buy_size
            , base_mid_sell_size
            , base_quote_off_reserve_buy_size
            , quote_mid_off_reserve_buy_size
            , base_mid_off_reserve_sell_size))
        size = min(market_buy_size, base_mid_sell_size, base_quote_off_reserve_buy_size, quote_mid_off_reserve_buy_size, base_mid_off_reserve_sell_size)
        return size

    '''
    卖出的下单保险数量计算
    假设BTC/CNY盘口流动性好
    1. LTC/BTC买方盘口吃单数量：ltc_btc_buy1_quantity*order_ratio_ltc_btc，其中ltc_btc_buy1_quantity 代表LTC/BTC买一档的数量，
        order_ratio_ltc_btc代表本策略在LTC/BTC盘口的吃单比例
    2. LTC/CNY卖方盘口卖单数量：ltc_cny_sell1_quantity*order_ratio_ltc_cny，其中order_ratio_ltc_cny代表本策略在LTC/CNY盘口的吃单比例
    3. LTC/BTC账户中可以用来卖LTC的数量：
        ltc_available - ltc_reserve，
        其中，ltc_available表示该账户中可用的LTC数量，ltc_reserve表示该账户中应该最少预留的LTC数量
        （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
    4.	BTC/CNY账户中可以用来卖BTC的BTC额度和对应的LTC个数：
        btc_available - btc_reserve, 可以置换成
        (btc_available-btc_reserve) / ltc_btc_sell1_price个LTC
        其中：btc_available表示该账户中可用的BTC数量，btc_reserve表示该账户中应该最少预留的BTC数量
        （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
    5.	LTC/CNY账户中可以用来卖的cny额度：
        cny_available – cny_reserve，相当于
        (cny_available – cny_reserve) / ltc_cny_sell1_price个LTC
        其中，cny_available表示该账户中可用的人民币数量，cny_reserve表示该账户中应该最少预留的人民币数量
        （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
    '''
    def get_market_sell_size(self):
        market_sell_size = self.order_book[self.base_quote]["bids"][0][1] * self.order_ratio_base_quote
        base_mid_buy_size = self.order_book[self.base_mid]["asks"][0][1] * self.order_ratio_base_mid
        base_quote_off_reserve_sell_size = self.balance[self.base]['free'] - self.base_quote_base_reserve
        quote_mid_off_reserve_sell_size = (self.balance[self.quote]['free'] - self.quote_mid_quote_reserve) / self.order_book[self.base_quote]["bids"][0][0]
        base_mid_off_reserve_buy_size = (self.balance[self.mid]['free'] - self.base_mid_mid_reserve) / self.order_book[self.base_mid]["asks"][0][0]
        logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(
            market_sell_size
            , base_mid_buy_size
            , base_quote_off_reserve_sell_size
            , quote_mid_off_reserve_sell_size
            , base_mid_off_reserve_buy_size))
        return min(market_sell_size, base_mid_buy_size, base_quote_off_reserve_sell_size, quote_mid_off_reserve_sell_size, base_mid_off_reserve_buy_size)

    '''
    正循环:
    LTC/BTC 买, LTC/CNY 卖，BTC/CNY 买
    '''
    async def pos_cycle(self, base_quote_buy_amount):
        logger.debug("pos_cycle() start  {0}".format(base_quote_buy_amount))
        ret = await self.buy_cancel(self.base_quote, base_quote_buy_amount)
        if ret['filled'] <= 0:
            logger.debug("pos_cycle() ret['filled'] <= 0 {0}".format(ret))
            return
        logger.debug("pos_cycle() ret['filled']= {0}".format(ret))

        logger.info("pos_cycle() 开始对冲，数量：{0}".format(ret['filled']))
        p1 = multiprocessing.Process(target=self.hedged_sell, args=(ret['filled'], self.base_mid))
        p1.start()

        # 直接从 ret 里面获取成交的 quote_cur 金额，然后对冲该金额
        quote_to_be_hedged = ret['filled'] * ret['price']
        p2 = multiprocessing.Process(target=self.hedged_buy, args=(quote_to_be_hedged, self.quote_mid))
        p2.start()

        p1.join()
        p2.join()
        logger.debug("pos_cycle() end")

    '''
    逆循环:
    LTC/BTC 卖, LTC/CNY 买，BTC/CNY 卖
    '''
    async def neg_cycle(self, base_quote_sell_amount):
        logger.debug("neg_cycle() start  {0}".format(base_quote_sell_amount))
        ret = await self.sell_cancel(self.base_quote, base_quote_sell_amount)
        if ret['filled'] <= 0:
            logger.debug("neg_cycle() ret['filled'] <= 0 {0}".format(ret))
            return
        logger.debug("neg_cycle() ret['filled']= {0}".format(ret))

        logger.info("neg_cycle() 开始对冲，数量：{0}".format(ret['filled']))
        p1 = multiprocessing.Process(target=self.hedged_buy, args=(ret['filled'], self.base_mid))
        p1.start()

        # 直接从 ret 里面获取成交的 quote_cur 金额，然后对冲该金额
        quote_to_be_hedged = ret['filled'] * ret['price']
        p2 = multiprocessing.Process(target=self.hedged_sell, args=(quote_to_be_hedged, self.quote_mid))
        p2.start()

        p1.join()
        p2.join()
        logger.debug("neg_cycle() end")

    async def hedged_buy(self, amount, symbol):
        logger.debug("hedged_buy() start {0}:{1}".format(symbol, amount))
        try:
            ret = await self.buy_cancel(symbol, amount)
            if amount > ret['filled']:
                await self.buy_all(symbol, amount - ret['filled'])
        except:
            logger.error(traceback.format_exc())
        logger.debug("hedged_buy() end {0}:{1}".format(symbol, amount))

    async def hedged_sell(self, amount, symbol):
        logger.debug("hedged_sell() start {0}:{1}".format(symbol, amount))
        try:
            ret = await self.sell_cancel(symbol, amount)
            if amount > ret['filled']:
                await self.sell_all(symbol, amount - ret['filled'])
        except:
            logger.error(traceback.format_exc())
        logger.debug("hedged_sell() end {0}:{1}".format(symbol, amount))
        





