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
import util.db_base
from util.exchange_base import exchange_base

logger = util.util.get_log(__name__)


# 搬砖
class stat_arbitrage():
    def __init__(self, symbol, exchange_base1, exchange_base2, db_base):
        self.symbol = symbol    # BTC/USD
        self.ex1 = exchange_base1
        self.ex2 = exchange_base2
        self.db = db_base

        self.base = self.symbol.split('/')[0]   # BTC
        self.quote = self.symbol.split('/')[1]  # USD

        self.spread1List = []       # exchange1_buy1 - exchange2_sell1
        self.spread2List = []       # exchange2_buy1 - exchange1_sell1

        # 多少根k线, 计算的时间跨度. 默认1秒1k线，计算1小时
        self.sma_window_size = 3600

        self.spread1_mean = None    # 均值
        self.spread1_stdev = None   # 方差
        self.spread2_mean = None
        self.spread2_stdev = None

        # 价格超过方差多少倍，有套利机会，下单
        self.spread1_open_condition_stdev_coe = 2.0
        self.spread2_open_condition_stdev_coe = 2.0

        # 价格小于方差多少倍，没有套利机会，这时可以考虑调整仓位
        self.spread1_close_condition_stdev_coe = 0.3
        self.spread2_close_condition_stdev_coe = 0.3

        # 0: no position
        # 1: long spread1(sell exchange1, buy exchange2)
        # 2: long spread2(buy exchange1, sell exchange2)
        self.current_position_direction = 0

        self.spread1_pos_amount = 0.0
        self.spread2_pos_amount = 0.0

        # 并不是所有挂单都能成交，每次预计能吃到的盘口深度的百分比
        self.order_book_ratio = 0.3

        # 评估 最小下注
        self.amount_min = 0.0

        # 仓位 再平衡，开关
        self.rebalance_on = False


    # 刚启动时，没有k线数据，尝试从数据库中取数据
    def fetch_history_data_from_db(self):
        if len(self.spread1List) > 0:
            return
        # 取最近的 sma_window_size 个k线
        from_dt = int(time.time()) - self.sma_window_size * 2
        for i in range(from_dt, from_dt + self.sma_window_size):
            try:
                self.fetch_data_from_db(i)
            except:
                logger.debug(traceback.format_exc())
    
    # 从 db 中取1条指定时间的数据
    def fetch_data_from_db(self, sql_con_timestamp):
        rows1 = self.db.ticker_select(self.db.db_name, self.symbol, self.ex1.ex.id, sql_con_timestamp)
        rows2 = self.db.ticker_select(self.db.db_name, self.symbol, self.ex2.ex.id, sql_con_timestamp)
        if rows1 is None or rows2 is None:
            return
        if len(rows1) >= 1:
            for row1 in rows1:
                self.ex1.buy_1_price = row1[1]
                self.ex1.sell_1_price = row1[2]
                self.ex1.order_book_time = sql_con_timestamp
        if len(rows2) >= 1:
            for row2 in rows2:
                self.ex2.buy_1_price = row2[1]
                self.ex2.sell_1_price = row2[2]
                self.ex2.order_book_time = sql_con_timestamp
        if self.ex1.buy_1_price <= 0 or self.ex1.sell_1_price <= 0 or self.ex2.buy_1_price <= 0 or self.ex2.sell_1_price <= 0:
            return
        spread1 = self.ex1.buy_1_price - self.ex2.sell_1_price
        spread2 = self.ex2.buy_1_price - self.ex1.sell_1_price
        self.spread1List = self.add_to_list(self.spread1List, spread1)
        self.spread2List = self.add_to_list(self.spread2List, spread2)

    # 从网络取数据
    async def fetch_order_book(self):
        await self.ex1.fetch_order_book()
        await self.ex2.fetch_order_book()
        if abs(self.ex1.order_book_time - self.ex2.order_book_time) > 3:
            return
        # 加入数据列表
        spread1 = self.ex1.buy_1_price - self.ex2.sell_1_price
        spread2 = self.ex2.buy_1_price - self.ex1.sell_1_price
        self.spread1List = self.add_to_list(self.spread1List, spread1)
        self.spread2List = self.add_to_list(self.spread2List, spread2)

    # 向list添加1个元素，当list长度大于某个定值时，会将前面超出的部分删除
    def add_to_list(self, dest_list, element):
        if self.sma_window_size == 1:
            return [element]
        while len(dest_list) > self.sma_window_size:
            del (dest_list[0])
        dest_list.append(element)
        return dest_list

    # 初始化足够的数据
    async def init_data(self):
        await self.ex1.load_markets()
        self.ex1.check_symbol(self.symbol)
        await self.ex2.load_markets()
        self.ex2.check_symbol(self.symbol)

        try:
            self.fetch_history_data_from_db()
        except:
            logger.error(traceback.format_exc())

        await self.ex1.fetch_balance()
        await self.ex2.fetch_balance()

        self.init_spread_amount()

        # 数据不足，不计算, 等待足够的数据
        while len(self.spread1List) < self.sma_window_size or len(self.spread2List) < self.sma_window_size:
            await self.fetch_order_book()
            #logger.debug(self.symbol + ',' + self.ex1.ex.id + ',' + self.ex2.ex.id + ';data len=' + str(len(self.spread1List)))

    # 计算移动平均
    def calc_sma_and_deviation(self):
        self.spread1_mean = np.mean(self.spread1List[-1 * self.sma_window_size:])
        self.spread1_stdev = np.std(self.spread1List[-1 * self.sma_window_size:])
        self.spread2_mean = np.mean(self.spread2List[-1 * self.sma_window_size:])
        self.spread2_stdev = np.std(self.spread2List[-1 * self.sma_window_size:])

    def init_spread_amount(self):
        if self.spread1_pos_amount > 0:
            self.current_position_direction = 1
        elif self.spread2_pos_amount > 0:
            self.current_position_direction = 2
        else:
            self.current_position_direction = 0

    # 仓位 再平衡
    def rebalance_set(self, rebalance_on, proportion):
        self.rebalance_on = rebalance_on
        self.ex1.rebalanced_position_proportion = proportion
        self.ex2.rebalanced_position_proportion = proportion

    async def rebalance_position(self):
        if not self.rebalance_on:
            return
        if self.ex1.rebalanced_position_proportion <= 0.0 or self.ex2.rebalanced_position_proportion <= 0.0:
            return
        await self.ex1.rebalance_position(self.symbol)
        await self.ex2.rebalance_position(self.symbol)
        # 1: long spread1(buy okcoin, sell huobi);  
        # 2: long spread2( buy huobi, sell okcoin), 
        # 0: no position
        self.current_position_direction = 0  
        self.spread1_pos_amount = 0
        self.spread2_pos_amount = 0

    # 判断开仓、平仓
    def calc_position_direction(self):
        # 没有仓位
        if self.current_position_direction == 0:
            if (self.spread1List[-1] - self.spread1_mean) / self.spread1_stdev > self.spread1_open_condition_stdev_coe:
                if (abs(self.spread1List[-1] - self.spread1_mean) / self.ex1.sell_1_price) < (self.ex1.fee_taker  + self.ex2.fee_taker) * 3:
                    logger.debug('calc_position_direction() check_fees 1')
                    return 0
                return 1
            elif (self.spread2List[-1] - self.spread2_mean) / self.spread2_stdev > self.spread2_open_condition_stdev_coe:
                if (abs(self.spread2List[-1] - self.spread2_mean) / self.ex1.buy_1_price) < (self.ex1.fee_taker  + self.ex2.fee_taker) * 3:
                    logger.debug('calc_position_direction() check_fees 2')
                    return 0
                return 2
        # 已有仓位, 方向1 (sell exchange1, buy exchange2)
        elif self.current_position_direction == 1:
            if (self.spread1List[-1] - self.spread1_mean) / self.spread1_stdev > self.spread1_open_condition_stdev_coe:
                # 还是方向1，可以继续判断，是否加仓
                return 1
            if (self.spread2List[-1] - self.spread2_mean) / self.spread2_stdev > -self.spread1_close_condition_stdev_coe:
                # 平仓
                return 2
        # 已有仓位, 方向2 (buy exchange1, sell exchange2)
        elif self.current_position_direction == 2:
            if (self.spread2List[-1] - self.spread2_mean) / self.spread2_stdev > self.spread2_open_condition_stdev_coe:
                # 还是方向2，可以继续判断，是否加仓
                return 2
            if (self.spread1List[-1] - self.spread1_mean) / self.spread1_stdev > -self.spread2_close_condition_stdev_coe:
                # 平仓
                return 1
        # 没有达到搬砖条件
        return 0

    async def run_arbitrage(self):
        await self.init_data()
        self.amount_min = max(self.ex1.balance_amount_min(self.symbol), self.ex2.balance_amount_min(self.symbol))
        while True:
            await self.ex1.fetch_balance()
            await self.ex2.fetch_balance()
            
            # 取订单深度信息
            await self.fetch_order_book()

            # 时间不同步，跳过 
            if abs(self.ex1.order_book_time - self.ex2.order_book_time) > 10:
                continue
            # 时间太久，跳过
            cur_t = int(time.time())
            timeout_warn = 10
            if self.ex1.order_book_time < cur_t - timeout_warn or self.ex2.order_book_time < cur_t - timeout_warn:
                continue

            # 计算方差
            self.calc_sma_and_deviation()

            # 价格回归平均值，平衡仓位
            if self.rebalance_on:
                c1 = abs(self.spread1List[-1] - self.spread1_mean) / self.spread1_stdev < self.spread1_close_condition_stdev_coe
                c2 = abs(self.spread2List[-1] - self.spread2_mean) / self.spread2_stdev < self.spread2_close_condition_stdev_coe
                if c1 or c2:
                    self.rebalance_position()
                    continue

            # 检查是否有机会
            amount_todo = 0.0
            position_direction = self.calc_position_direction()
            if position_direction == 0:
                # 没有交易信号，继续=
                continue
            elif position_direction == 1:
                self.log(position_direction)
                if self.current_position_direction == 0:  # 当前没有持仓
                    # 计算第1次开仓数量
                    amount_todo = min(self.ex1.buy_1_quantity, self.ex2.sell_1_quantity) * self.order_book_ratio
                elif self.current_position_direction == 1:  # 当前long spread1
                    # 已有仓位，计算加仓数量
                    amount_todo = min(self.ex1.buy_1_quantity, self.ex2.sell_1_quantity) * self.order_book_ratio
                elif self.current_position_direction == 2:  # 当前long spread2
                    # 另一个方向有仓位，计算可以减仓的数量
                    depth_amount = min(self.ex1.buy_1_quantity, self.ex2.sell_1_quantity) * self.order_book_ratio
                    amount_todo = min(depth_amount, self.spread2_pos_amount)

                # 以最小单位下注
                amount_todo = min(amount_todo, self.amount_min)

                # 账户中的钱，最大可以开多少仓位
                can_op_amount_1 = self.ex1.balance[self.base]['free']
                can_op_amount_2 = self.ex2.balance[self.quote]['free'] / self.ex2.sell_1_price * 0.98
                amount_max = min(can_op_amount_1, can_op_amount_2)
                amount_todo = min(amount_todo, amount_max)

                # 计算出的交易量 < 交易所要求的最小量 : 无法下单，忽略这次机会
                if amount_todo <= self.amount_min:
                    continue
                await self.do_order_spread1(amount_todo)

            elif position_direction == 2:
                self.log(position_direction)
                if self.current_position_direction == 0:  # 当前没有持仓
                    # 计算第1次开仓数量
                    amount_todo = min(self.ex2.buy_1_quantity, self.ex1.sell_1_quantity) * self.order_book_ratio
                elif self.current_position_direction == 2:  # 当前long spread2
                    # 已有仓位，计算加仓数量
                    amount_todo = min(self.ex2.buy_1_quantity, self.ex1.sell_1_quantity) * self.order_book_ratio
                elif self.current_position_direction == 1:  # 当前long spread1
                    # 另一个方向有仓位，计算可以减仓的数量
                    depth_amount = min(self.ex2.buy_1_quantity, self.ex1.sell_1_quantity) * self.order_book_ratio
                    amount_todo = min(depth_amount, self.spread1_pos_amount)

                # 以最小单位下注
                amount_todo = min(amount_todo, self.amount_min)

                # 账户中的钱，最大可以开多少仓位
                can_op_amount_1 = self.ex1.balance[self.quote]['free'] / self.ex1.sell_1_price * 0.98
                can_op_amount_2 = self.ex2.balance[self.base]['free']
                amount_max = min(can_op_amount_1, can_op_amount_2)
                amount_todo = min(amount_todo, amount_max)
                # 计算出的交易量 < 交易所要求的最小量 : 无法下单，忽略这次机会
                if amount_todo <= self.amount_min:
                    continue
                await self.do_order_spread2(amount_todo)

            if self.spread1_pos_amount > 0:
                self.current_position_direction = 1
            elif self.spread2_pos_amount > 0:
                self.current_position_direction = 2
            else:
                self.current_position_direction = 0
            
            # 完成一次套利，sleep 一下
            time.sleep(15)

    def log(self, position_direction):
        str_bz = '\n' + self.symbol + ';bz=' + str(position_direction) + '\n'     \
            + self.ex1.symbol + ';ex1=' + self.ex1.ex.id + ',bid=' + str(self.ex1.buy_1_price) + ',ask=' + str(self.ex1.sell_1_price) + '\n'    \
            + self.ex2.symbol + ';ex2=' + self.ex2.ex.id + ',bid=' + str(self.ex2.buy_1_price) + ',ask=' + str(self.ex2.sell_1_price) + '\n'
        if position_direction == 1:
            str_bz = str_bz + self.symbol + ';sell=' + str(self.ex1.buy_1_price) + ';buy=' + str(self.ex2.sell_1_price) + '\n'
        if position_direction == 2:
            str_bz = str_bz + self.symbol + ';buy=' + str(self.ex1.sell_1_price) + ';sell=' + str(self.ex2.buy_1_price)
        logger.info(str_bz)

    # 先执行第1个交易所的下单，等交易结果
    async def do_order_spread1(self, amount):
        ret = await self.ex1.sell_cancel(self.ex1.symbol, amount)
        if ret['filled'] <= 0:    # 订单完全没有成交，等待下一次机会
            return
        # 第1交易所已下单成功，第2交易所下单
        await self.ex2.buy_all(self.ex2.symbol, ret['filled'])
        if self.current_position_direction == 0 or self.current_position_direction == 1:
            self.spread1_pos_amount += ret['filled']
        elif self.current_position_direction == 2:
            self.spread2_pos_amount -= ret['filled']

    async def do_order_spread2(self, amount):
        ret = await self.ex2.sell_cancel(self.ex2.symbol, amount)
        if ret['filled'] <= 0:    # 订单完全没有成交，等待下一次机会
            return
        # 第2交易所已下单成功，第1交易所下单
        await self.ex1.buy_all(self.ex1.symbol, ret['filled'])
        if self.current_position_direction == 0 or self.current_position_direction == 2:
            self.spread2_pos_amount += ret['filled']
        elif self.current_position_direction == 1:
            self.spread1_pos_amount -= ret['filled']

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
                logger.error(traceback.format_exc())
                time.sleep(10)
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
                time.sleep(5)
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
        logger.debug('stat_arbitrage run() end.')









############################################################################

def do_stat_arbitrage(symbols, ids, db_base):
    ex_list = []
    for id in ids:
        ex = exchange_base(util.util.get_exchange(id, True))
        ex_list.append(ex)

    pair_list = []
    size = len(ex_list)
    for i in range(0, size):
        for j in range(0, size):
            if j > i:
                for symbol in symbols:
                    pair = stat_arbitrage(symbol, ex_list[i], ex_list[j], db_base)
                    pair_list.append(pair)

    tasks = []
    for pair in pair_list:
        tasks.append(asyncio.ensure_future(pair.run(pair.run_arbitrage)))

    pending = asyncio.Task.all_tasks()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*pending))











