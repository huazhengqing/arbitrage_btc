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
from util.exchange_base import exchange_base


"""
交易对：用一种资产（quote currency）去定价另一种资产（base currency）,比如用比特币（BTC）去定价莱特币（LTC），
就形成了一个LTC/BTC的交易对，
交易对的价格代表的是买入1单位的base currency（比如LTC）
需要支付多少单位的quote currency（比如BTC），
或者卖出一个单位的base currency（比如LTC）
可以获得多少单位的quote currency（比如BTC）。
当LTC对BTC的价格上涨时，同等单位的LTC能够兑换的BTC是增加的，而同等单位的BTC能够兑换的LTC是减少的。
"""
class triangle(exchange_base):
    """
    base:  基准资产
    quote:  定价资产
    mid:  中间资产
    """
    def __init__(self, exchange, base, quote, mid):
        exchange_base.__init__(self, exchange)
        self.base = base
        self.quote = quote
        self.mid = mid

        # 滑点 百分比，方便计算
        self.slippage_base_quote = 0.002  
        self.slippage_base_mid = 0.002
        self.slippage_quote_mid = 0.002

        # 吃单比例
        self.order_ratio_base_quote = 0.5
        self.order_ratio_base_mid = 0.5

        # 设定市场初始 ------------现在没有接口，人工转币，保持套利市场平衡--------------
        # 余额预留数量
        self.base_quote_quote_reserve = 0.0    
        self.base_quote_base_reserve = 0.0
        self.quote_mid_mid_reserve = 0.0
        self.quote_mid_quote_reserve = 0.0
        self.base_mid_base_reserve = 0.0
        self.base_mid_mid_reserve = 0.0

        exchange_base.init_log(self)

    async def run_strategy(self):
        await exchange_base.load_markets(self)
        exchange_base.check_symbol(self, util.util.get_symbol(self.base, self.quote))
        exchange_base.check_symbol(self, util.util.get_symbol(self.base, self.mid))
        exchange_base.check_symbol(self, util.util.get_symbol(self.quote, self.mid))

        await exchange_base.fetch_balance(self)
        
        self.order_book = dict()

        cur_pair = util.util.get_symbol(self.base, self.quote)
        self.logger.debug(cur_pair)
        await exchange_base.fetch_order_book(self, cur_pair, 5)
        market_price_sell_1 = self.order_book[cur_pair]['asks'][0][0]
        market_price_buy_1 = self.order_book[cur_pair]['bids'][0][0]
        self.slippage_base_quote = (market_price_sell_1 - market_price_buy_1)/market_price_buy_1

        cur_pair = util.util.get_symbol(self.base, self.mid)
        self.logger.debug(cur_pair)
        await exchange_base.fetch_order_book(self, cur_pair, 5)
        base_mid_price_sell_1 = self.order_book[cur_pair]['asks'][0][0]
        base_mid_price_buy_1 = self.order_book[cur_pair]['bids'][0][0]
        self.slippage_base_mid = (base_mid_price_sell_1 - base_mid_price_buy_1)/base_mid_price_buy_1

        cur_pair = util.util.get_symbol(self.quote, self.mid)
        self.logger.debug(cur_pair)
        await exchange_base.fetch_order_book(self, cur_pair, 5)
        quote_mid_price_sell_1 = self.order_book[cur_pair]['asks'][0][0]
        quote_mid_price_buy_1 = self.order_book[cur_pair]['bids'][0][0]
        self.slippage_quote_mid = (quote_mid_price_sell_1 - quote_mid_price_buy_1)/quote_mid_price_buy_1

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
        if (base_mid_price_buy_1 / quote_mid_price_sell_1 - market_price_sell_1)/market_price_sell_1 > self.sum_slippage_fee():
            d = (base_mid_price_buy_1 / quote_mid_price_sell_1 - market_price_sell_1)/market_price_sell_1
            s = self.ex.id + "正循环差价：{0},滑点+手续费:{1}".format(d, self.sum_slippage_fee())
            self.logger.info(s)
            await self.pos_cycle(self.get_market_buy_size())
        # 检查逆循环套利
        elif (market_price_buy_1 - base_mid_price_sell_1 / quote_mid_price_buy_1)/market_price_buy_1 > self.sum_slippage_fee():
            d = (market_price_buy_1 - base_mid_price_sell_1 / quote_mid_price_buy_1)/market_price_buy_1
            s = "逆循环差价：{0},滑点+手续费:{1}".format(d, self.sum_slippage_fee())
            self.logger.info(s)
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
        market_buy_size = self.order_book[util.util.get_symbol(self.base, self.quote)]["asks"][0][1] * self.order_ratio_base_quote
        base_mid_sell_size = self.order_book[util.util.get_symbol(self.base, self.mid)]["bids"][0][1] * self.order_ratio_base_mid
        base_quote_off_reserve_buy_size = (self.balance[self.quote]['free'] - self.base_quote_quote_reserve) /  self.order_book[util.util.get_symbol(self.base, self.quote)]["asks"][0][0]
        quote_mid_off_reserve_buy_size = (self.balance[self.mid]['free'] - self.quote_mid_mid_reserve) / self.order_book[util.util.get_symbol(self.quote, self.mid)]["asks"][0][0] / self.order_book[util.util.get_symbol(self.base, self.quote)]["asks"][0][0]
        base_mid_off_reserve_sell_size = self.balance[self.base]['free'] - self.base_mid_base_reserve
        self.logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(
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
        market_sell_size = self.order_book[util.util.get_symbol(self.base, self.quote)]["bids"][0][1] * self.order_ratio_base_quote
        base_mid_buy_size = self.order_book[util.util.get_symbol(self.base, self.mid)]["asks"][0][1] * self.order_ratio_base_mid
        base_quote_off_reserve_sell_size = self.balance[self.base]['free'] - self.base_quote_base_reserve
        quote_mid_off_reserve_sell_size = (self.balance[self.quote]['free'] - self.quote_mid_quote_reserve) / self.order_book[util.util.get_symbol(self.base, self.quote)]["bids"][0][0]
        base_mid_off_reserve_buy_size = (self.balance[self.mid]['free'] - self.base_mid_mid_reserve) / self.order_book[util.util.get_symbol(self.base, self.mid)]["asks"][0][0]
        self.logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(
            market_sell_size
            , base_mid_buy_size
            , base_quote_off_reserve_sell_size
            , quote_mid_off_reserve_sell_size
            , base_mid_off_reserve_buy_size))
        return min(market_sell_size, base_mid_buy_size, base_quote_off_reserve_sell_size, quote_mid_off_reserve_sell_size, base_mid_off_reserve_buy_size)

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
    '''
    正循环套利
    正循环套利的顺序如下：
    先去LTC/BTC吃单买入LTC，卖出BTC，然后根据LTC/BTC的成交量，使用多线程，
    同时在LTC/CNY和BTC/CNY市场进行对冲。LTC/CNY市场吃单卖出LTC，BTC/CNY市场吃单买入BTC。
    '''
    async def pos_cycle(self, market_buy_size):
        cur_pair = util.util.get_symbol(self.base, self.quote)
        if market_buy_size < self.ex.markets[cur_pair]['limits']['amount']['min']:
            self.logger.info("下注数量 < 最小交易单位 size:{0}".format(market_buy_size))
            return
        self.logger.info("开始正循环套利 size:{0}".format(market_buy_size))
        order_result = await self.ex.create_order(
            cur_pair
            , self.order_book[cur_pair]["asks"][0][0]
            , 'buy'
            , util.util.downRound(market_buy_size, self.ex.markets[cur_pair]['precision']['amount'])
            , None
            , {'leverage': 1}
            )
        self.logger.info("买入结果：{0}".format(order_result))
        if order_result['filled'] <= 0:
            # 交易失败
            self.logger.info("正循环交易失败，退出套利 {0}".format(order_result))
            return
        # 获取真正成交量
        retry, already_hedged_amount = 0, 0.0
        while retry < 3:   # 循环3次检查是否交易成功
            if retry == 2:
                # 取消剩余未成交的
                if order_result['remaining'] > 0:
                    await self.ex.cancel_order(order_result['id'])
            field_amount = float(order_result['filled'])
            self.logger.info("field_amount:{0}{1}".format(field_amount,already_hedged_amount))

            if field_amount-already_hedged_amount < self.ex.markets[cur_pair]['limits']['amount']['min']:
                self.logger.info("没有新的成功交易或者新成交数量太少")
                retry += 1
                continue

            # 开始对冲
            self.logger.info("开始对冲，数量：{0}".format(field_amount - already_hedged_amount))
            p1 = multiprocessing.Process(target=self.hedged_sell_cur_pair, args=(field_amount-already_hedged_amount, util.util.get_symbol(self.base, self.mid)))
            p1.start()

            # 直接从order_result里面获取成交的quote_cur金额，然后对冲该金额
            quote_to_be_hedged = (field_amount - already_hedged_amount) * order_result['price']
            p2 = multiprocessing.Process(target=self.hedged_buy_cur_pair, args=(quote_to_be_hedged, util.util.get_symbol(self.quote, self.mid)))
            p2.start()

            p1.join()
            p2.join()

            already_hedged_amount = field_amount
            if field_amount >= market_buy_size:  # 已经完成指定目标数量的套利
                break
            retry += 1
        self.logger.info("完成正循环套利")

    '''
    逆循环套利
    逆循环套利的顺序如下：
    先去LTC/BTC吃单卖出LTC，买入BTC，然后根据LTC/BTC的成交量，使用多线程，
    同时在LTC/CNY和BTC/CNY市场进行对冲。
    LTC/CNY市场吃单买入LTC，BTC/CNY市场吃单卖出BTC。
    '''
    async def neg_cycle(self, market_sell_size):
        cur_pair = util.util.get_symbol(self.base, self.quote)
        if market_sell_size < self.ex.markets[cur_pair]['limits']['amount']['min']:
            self.logger.info("下注数量 < 最小交易单位 size:{0}".format(market_sell_size))
            return
        self.logger.info("开始逆循环套利 size:{0}".format(market_sell_size))
        order_result = await self.ex.create_order(
            cur_pair
            , self.order_book[cur_pair]["bids"][0][0]
            , 'sell'
            , util.util.downRound(market_sell_size, self.ex.markets[cur_pair]['precision']['amount'])
            , None
            , {'leverage': 1}
            )
        if order_result['filled'] <= 0:
            # 交易失败
            self.logger.info("逆循环交易失败，退出套利 {0}".format(order_result))
            return
        # 获取真正成交量
        retry, already_hedged_amount = 0, 0.0
        while retry < 3:  # 循环3次检查是否交易成功
            if retry == 2:
                # 取消剩余未成交的
                if order_result['remaining'] > 0:
                    await self.ex.cancel_order(order_result['id'])
            field_amount = float(order_result['filled'])
            self.logger.info("field_amount:{0}{1}".format(field_amount, already_hedged_amount))

            if field_amount - already_hedged_amount < self.ex.markets[cur_pair]['limits']['amount']['min']:
                self.logger.info("没有新的成功交易或者新成交数量太少")
                retry += 1
                continue

            # 开始对冲
            self.logger.info("开始对冲，数量：{0}".format(field_amount - already_hedged_amount))
            p1 = multiprocessing.Process(target=self.hedged_buy_cur_pair, args=(field_amount - already_hedged_amount, util.util.get_symbol(self.base, self.mid)))
            p1.start()

            # 直接从order_result里面获取成交的quote_cur金额，然后对冲该金额
            quote_to_be_hedged = (field_amount - already_hedged_amount) * order_result['price']
            p2 = multiprocessing.Process(target=self.hedged_sell_cur_pair, args=(quote_to_be_hedged, util.util.get_symbol(self.quote, self.mid)))
            p2.start()

            p1.join()
            p2.join()

            already_hedged_amount = field_amount
            if field_amount >= market_sell_size:  # 已经完成指定目标数量的套利
                break
            retry += 1
        self.logger.info("结束逆循环套利")

    async def hedged_buy_cur_pair(self, buy_size, cur_pair):
        self.logger.info("开始买入{0}".format(cur_pair))
        try:
            order_result = await self.ex.create_order(
                cur_pair
                , self.order_book[cur_pair]["asks"][0][0]
                , 'buy'
                , util.util.downRound(buy_size, self.ex.markets[cur_pair]['precision']['amount'])
                , None
                , {'leverage': 1}
                )
            hedged_amount = 0.0
            self.logger.info("买入结果：{0}".format(order_result))

            if order_result['filled'] <= 0:
                # 交易失败
                self.logger.info("买入{0} 交易失败 {1}".format(cur_pair, order_result))
            if order_result['remaining'] > 0:
                await self.ex.cancel_order(order_result['id'])      # 取消未成交的order
            hedged_amount = float(order_result['filled'])
            if buy_size > hedged_amount:
                # 对未成交的进行市价交易
                buy_amount = self.order_book[cur_pair]["asks"][4][0] * (buy_size - hedged_amount)  # 市价的amount按5档最差情况预估
                buy_amount = max(self.ex.markets[cur_pair]['limits']['amount']['min'], buy_amount)
                market_order_result = await self.ex.create_order(
                    cur_pair
                    , 'market'
                    , 'buy'
                    , util.util.downRound(buy_amount, self.ex.markets[cur_pair]['precision']['amount'])
                    , None
                    , {'leverage': 1}
                    )
                self.logger.info(market_order_result)
        except:
            self.logger.error(traceback.format_exc())
        self.logger.info("结束买入{0}".format(cur_pair))

    async def hedged_sell_cur_pair(self, sell_size, cur_pair):
        self.logger.info("开始卖出{0}".format(cur_pair))
        try:
            order_result = await self.ex.create_order(
                cur_pair
                , self.order_book[cur_pair]["bids"][0][0]
                , 'sell'
                , util.util.downRound(sell_size, self.ex.markets[cur_pair]['precision']['amount'])
                , None
                , {'leverage': 1}
                )
            hedged_amount = 0.0
            self.logger.info("卖出结果：{0}".format(order_result))
            if order_result['filled'] <= 0:
                # 交易失败
                self.logger.info("卖出{0} 交易失败  {1}".format(cur_pair, order_result))
            if order_result['remaining'] > 0:
                await self.ex.cancel_order(order_result['id'])      # 取消未成交的order
            hedged_amount = float(order_result['filled'])
            if sell_size > hedged_amount:
                # 对未成交的进行市价交易
                sell_qty = sell_size - hedged_amount
                sell_qty = max(self.ex.markets[cur_pair]['limits']['amount']['min'], sell_qty)
                market_order_result = await self.ex.create_order(
                    cur_pair
                    , 'market'
                    , 'sell'
                    , util.util.downRound(sell_qty, self.ex.markets[cur_pair]['precision']['amount'])
                    , None
                    , {'leverage': 1}
                    )
                self.logger.info(market_order_result)
        except:
            self.logger.error(traceback.format_exc())
        self.logger.info("结束卖出{0}".format(cur_pair))






