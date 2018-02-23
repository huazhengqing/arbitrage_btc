#!/usr/bin/python

import os
import sys
import time
import asyncio
import ccxt.async as ccxt
import numpy as np


# 注：只有少数交易所，支持作空
# 假定是保证金交易，2个交易所，都是可以作空

# usd == usdt，没有usd 的交易所，自动更换成 usdt

# 统计套利搬砖
class calc_stat_arb():
    def __init__(self, symbol, exchange1, exchange2, db_symbol):
        self.symbol = symbol         # BTC/USD
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.db = db_symbol

        self.spread1List = []       # exchange1_buy1 - exchange2_sell1
        self.spread2List = []       # exchange2_buy1 - exchange1_sell1

        self.sma_window_size = 3600        # 多少根k线, 计算的时间跨度. 默认1秒1k线，计算1小时
        self.spread1_mean = None        # 均值
        self.spread1_stdev = None        # 方差
        self.spread2_mean = None
        self.spread2_stdev = None
        
        self.spread1_open_condition_stdev_coe = 2        # 价格超过方差多少倍，下单
        self.spread2_open_condition_stdev_coe = 2
        self.spread1_close_condition_stdev_coe = 0.3        # 价格小于方差多少倍，可以平仓
        self.spread2_close_condition_stdev_coe = 0.3

        # 0: no position
        # 1: long spread1(sell exchange1, buy exchange2)
        # 2: long spread2(buy exchange1, sell exchange2)
        self.current_position_direction = 0  

        self.spread1_pos_qty = 0
        self.spread2_pos_qty = 0

        # load_markets
        self.symbol_1 = self.symbol.split('/')[0]       # BTC
        self.symbol_2 = self.symbol.split('/')[1]       # USD

        # 有平台没有 usd，只有 usdt
        self.exchange1_symbol = self.symbol         # BTC/USD
        self.exchange2_symbol = self.symbol         # BTC/USD
        self.exchange1_symbol_2 = self.symbol_2       # USD
        self.exchange2_symbol_2 = self.symbol_2       # USD

        self.exchange1_market = {}
        self.exchange1_trade_fee = 0.0        # 单笔交易费用
        self.exchange1_trade_min = 0.001        # 最小交易量
        self.exchange1_trade_min_base = 0.001        # 交易量最小增加值

        self.exchange2_market = {}
        self.exchange2_trade_fee = 0.0        # 单笔交易费用
        self.exchange2_trade_min = 0.001        # 最小交易量
        self.exchange2_trade_min_base = 0.001        # 交易量最小增加值

        # fetch_balance
        self.exchange1.balance = None
        self.exchange1_symbol1_free = 0
        self.exchange1_symbol1_used = 0
        self.exchange1_symbol1_total = 0

        self.exchange1_symbol2_free = 0
        self.exchange1_symbol2_used = 0
        self.exchange1_symbol2_total = 0

        self.exchange2.balance = None
        self.exchange2_symbol1_free = 0
        self.exchange2_symbol1_used = 0
        self.exchange2_symbol1_total = 0
        
        self.exchange2_symbol2_free = 0
        self.exchange2_symbol2_used = 0
        self.exchange2_symbol2_total = 0
        
        # fetch_order_book
        self.exchange1_buy_1_price = 0.0
        self.exchange1_buy_1_quantity = 0.0
        self.exchange1_sell_1_price = 0.0
        self.exchange1_sell_1_quantity = 0.0
        self.exchange1_last_alive = 0
        
        self.exchange2_buy_1_price = 0.0
        self.exchange2_buy_1_quantity = 0.0
        self.exchange2_sell_1_price = 0.0
        self.exchange2_sell_1_quantity = 0.0
        self.exchange2_last_alive = 0

        self.check_data_timestamp = 0

        self.order_ratio = 0.6  # 每次预计能吃到的盘口深度的百分比
        

    # 向list添加1个元素，当list长度大于某个定值时，会将前面超出的部分删除
    def add_to_list(self, dest_list, element):
        if self.sma_window_size == 1:
            return [element]
        while len(dest_list) >= self.sma_window_size:
            del (dest_list[0])
        dest_list.append(element)
        return dest_list

    # 计算移动平均
    def calc_sma_and_deviation(self):
        self.spread1_mean = np.mean(self.spread1List[-1 * self.sma_window_size:])
        self.spread1_stdev = np.std(self.spread1List[-1 * self.sma_window_size:])
        self.spread2_mean = np.mean(self.spread2List[-1 * self.sma_window_size:])
        self.spread2_stdev = np.std(self.spread2List[-1 * self.sma_window_size:])

    # 判断开仓、平仓
    def calc_position_direction(self):
        # 没有仓位
        if self.current_position_direction == 0:
            if (self.spread1List[-1] - self.spread1_mean) / self.spread1_stdev > self.spread1_open_condition_stdev_coe:
                return 1
            elif (self.spread2List[-1] - self.spread2_mean) / self.spread2_stdev > self.spread2_open_condition_stdev_coe:
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

    # 刚启动时，没有k线数据，尝试从数据库中取数据
    def fetch_history_data_from_db(self):
        if len(self.spread1List) > 0:
            return
        # 取最近的 sma_window_size 个k线
        from_dt = int(time.time()) - self.sma_window_size
        for i in range(from_dt, from_dt + self.sma_window_size):
            self.fetch_data_from_db(i)
    
    # 从 db 中取1条指定时间的数据
    def fetch_data_from_db(self, sql_con_timestamp):
        rows1 = self.db.fetch_one(self.exchange1, sql_con_timestamp)
        rows2 = self.db.fetch_one(self.exchange2, sql_con_timestamp)
        if len(rows1) >= 1:
            for row1 in rows1:
                self.exchange1_buy_1_price = row1[1]
                self.exchange1_sell_1_price = row1[2]
                self.exchange1_last_alive = sql_con_timestamp
        if len(rows2) >= 1:
            for row2 in rows2:
                self.exchange2_buy_1_price = row2[1]
                self.exchange2_sell_1_price = row2[2]
                self.exchange2_last_alive = sql_con_timestamp
        if self.exchange1_buy_1_price <= 0 or self.exchange1_sell_1_price <= 0 or self.exchange2_buy_1_price <= 0 or self.exchange2_sell_1_price <= 0:
            return
        spread1 = self.exchange1_buy_1_price - self.exchange2_sell_1_price
        spread2 = self.exchange2_buy_1_price - self.exchange1_sell_1_price
        self.spread1List = self.add_to_list(self.spread1List, spread1)
        self.spread2List = self.add_to_list(self.spread2List, spread2)


    # 检查是否支持 symbol，确定最小交易量，费用
    async def load_markets(self):
        # exchange1
        await self.exchange1.load_markets()
        if self.symbol_2 == 'USD':
            if self.symbol not in self.exchange1.markets:         # 没有 usd，只有 usdt
                self.exchange1_symbol_2 = 'USDT'
                self.exchange1_symbol = self.symbol_1 + '/' + self.exchange1_symbol_2         # BTC/USD
        self.exchange1_market = self.exchange1.markets[self.exchange1_symbol]
        self.exchange1_trade_fee = 0        # 单笔交易费用
        self.exchange1_trade_min = 0.01        # 最小交易量
        self.exchange1_trade_min_base = 0        # 交易量最小增加值
        
        # exchange2
        await self.exchange2.load_markets()
        if self.symbol_2 == 'USD':
            if not self.exchange2.markets.has_key(self.symbol):         # 没有 usd，只有 usdt
                self.exchange2_symbol_2 = 'USDT'
                self.exchange1_symbol = self.symbol_1 + '/' + self.exchange2_symbol_2         # BTC/USD
        self.exchange2_market = self.exchange2.markets[self.exchange2_symbol]
        self.exchange2_trade_fee = 0        # 单笔交易费用
        self.exchange2_trade_min = 0.01        # 最小交易量
        self.exchange2_trade_min_base = 0        # 交易量最小增加值

    #  查看余额
    async def fetch_balance(self):
        # exchange1
        self.exchange1.balance = await self.exchange1.fetch_balance()
        self.exchange1_symbol1_free = self.exchange1.balance[self.symbol_1]['free']        # 已经开仓了多少
        self.exchange1_symbol1_used = self.exchange1.balance[self.symbol_1]['used']
        self.exchange1_symbol1_total = self.exchange1.balance[self.symbol_1]['total']

        self.exchange1_symbol2_free = self.exchange1.balance[self.exchange1_symbol_2]['free']        # 还有多少钱
        self.exchange1_symbol2_used = self.exchange1.balance[self.exchange1_symbol_2]['used']
        self.exchange1_symbol2_total = self.exchange1.balance[self.exchange1_symbol_2]['total']

        # exchange2
        self.exchange2.balance = await self.exchange2.fetch_balance()
        self.exchange2_symbol1_free = self.exchange2.balance[self.symbol_1]['free']        # 已经开仓了多少
        self.exchange2_symbol1_used = self.exchange2.balance[self.symbol_1]['used']
        self.exchange2_symbol1_total = self.exchange2.balance[self.symbol_1]['total']
        
        self.exchange2_symbol2_free = self.exchange2.balance[self.exchange2_symbol_2]['free']        # 还有多少钱
        self.exchange2_symbol2_used = self.exchange2.balance[self.exchange2_symbol_2]['used']
        self.exchange2_symbol2_total = self.exchange2.balance[self.exchange2_symbol_2]['total']

    def init_spread_qty(self):
        # exc1 有空单
        if self.exchange1_symbol1_used > 0:
            self.spread1_pos_qty = self.exchange1_symbol1_used

        # exc2 有空单
        if self.exchange2_symbol1_used > 0:
            self.spread2_pos_qty = self.exchange2_symbol1_used

        if self.spread1_pos_qty > 0:
            self.current_position_direction = 1
        elif self.spread2_pos_qty > 0:
            self.current_position_direction = 2
        else:
            self.current_position_direction = 0


    # 取深度信息，只取1层
    async def fetch_order_book(self):
        # exchange1
        order_book1 = await self.exchange1.fetch_order_book(self.exchange1_symbol, 1)
        self.exchange1_buy_1_price = order_book1['bids'][0][0]
        self.exchange1_buy_1_quantity = order_book1['bids'][0][1]
        self.exchange1_sell_1_price = order_book1['asks'][0][0]
        self.exchange1_sell_1_quantity = order_book1['asks'][0][1]
        self.exchange1_last_alive = int(time.time())
        
        # exchange2
        order_book2 = await self.exchange2.fetch_order_book(self.exchange2_symbol, 1)
        self.exchange2_buy_1_price = order_book2['bids'][0][0]
        self.exchange2_buy_1_quantity = order_book2['bids'][0][1]
        self.exchange2_sell_1_price = order_book2['asks'][0][0]
        self.exchange2_sell_1_quantity = order_book2['asks'][0][1]
        self.exchange2_last_alive = int(time.time())

        # 加入数据列表
        spread1 = self.exchange1_buy_1_price - self.exchange2_sell_1_price
        spread2 = self.exchange2_buy_1_price - self.exchange1_sell_1_price
        self.spread1List = self.add_to_list(self.spread1List, spread1)
        self.spread2List = self.add_to_list(self.spread2List, spread2)


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
    # 先执行第1个交易所的下单，等交易结果
    # 假定交易所，支持保证金交易，但是只用1倍保证金
    # 有交易所，只支持 limit order 
    # 不支持, 失败, 未全部成交   ????????????
    # 异常，网络问题，报警   ?????????????
    def do_order_spread1(self, todo_qty):
        exc1_order_ret = self.exchange1.create_order(self.exchange1_symbol, 'market', 'sell', todo_qty, None, {'leverage': 1})
        # 订单没有成交全部，剩下的订单取消
        if exc1_order_ret['remaining'] > 0:
            self.exchange1.cancel_order(exc1_order_ret['id'])
        ok_qty = exc1_order_ret['filled']
        if ok_qty <= 0:    # 订单完全没有成交，等待下一次机会
            return
        # 第1交易所已下单成功，第2交易所下单
        exc2_order_ret = self.exchange2.create_order(self.exchange2_symbol, 'market', 'buy', ok_qty, None, {'leverage': 1})
        while exc2_order_ret['remaining'] > 0:
            exc2_order_ret = self.exchange2.create_order(self.exchange2_symbol, 'market', 'buy', exc2_order_ret['remaining'], None, {'leverage': 1})

        if self.current_position_direction == 0 or self.current_position_direction == 1:
            self.spread1_pos_qty += ok_qty
        elif self.current_position_direction == 2:
            self.spread2_pos_qty -= ok_qty



    def do_order_spread2(self, todo_qty):
        exc2_order_ret = self.exchange2.create_order(self.exchange2_symbol, 'market', 'sell', todo_qty, None, {'leverage': 1})
        # 订单没有成交全部，剩下的订单取消
        if exc2_order_ret['remaining'] > 0:
            self.exchange2.cancel_order(exc2_order_ret['id'])
        ok_qty = exc2_order_ret['filled']
        if ok_qty <= 0:    # 订单完全没有成交，等待下一次机会
            return
        # 第2交易所已下单成功，第1交易所下单
        exc1_order_ret = self.exchange1.create_order(self.exchange1_symbol, 'market', 'buy', ok_qty, None, {'leverage': 1})
        while exc1_order_ret['remaining'] > 0:
            exc1_order_ret = self.exchange1.create_order(self.exchange1_symbol, 'market', 'buy', exc1_order_ret['remaining'], None, {'leverage': 1})

        if self.current_position_direction == 0 or self.current_position_direction == 2:
            self.spread2_pos_qty += ok_qty
        elif self.current_position_direction == 1:
            self.spread1_pos_qty -= ok_qty



    def do_it(self):
        self.fetch_history_data_from_db()
        self.load_markets()
        self.fetch_balance()
        self.init_spread_qty()
        while True:
            cur_t = int(time.time())
            if self.check_data_timestamp >= cur_t:
                time.sleep(0.5)
                continue
            self.check_data_timestamp = cur_t

            # 取订单深度信息
            self.fetch_order_book()

            # 数据不足，不计算, 等待足够的数据
            if len(self.spread1List) < self.sma_window_size or len(self.spread2List) < self.sma_window_size:
                time.sleep(0.5)
                continue
            
            # 超过 5 秒钟没有收到新数据，等新数据
            timeout_warn = 5
            if self.exchange1_last_alive < cur_t - timeout_warn or self.exchange2_last_alive < cur_t - timeout_warn:
                continue

            # 计算方差
            self.calc_sma_and_deviation()

            '''
            # 价格回归平均值
            # 为赚取最大收益，在价格反向方差开仓时，再平仓。以下代码注释
            if abs(self.spread1List[-1] - self.spread1_mean) / self.spread1_stdev < self.spread1_close_condition_stdev_coe:
                continue
            if abs(self.spread2List[-1] - self.spread2_mean) / self.spread2_stdev < self.spread2_close_condition_stdev_coe:
                continue
            '''

            # 检查是否有机会
            todo_qty = 0.0
            position_direction = self.calc_position_direction()
            if position_direction == 0:
                # 没有交易信号，继续=
                continue
            elif position_direction == 1:
                if self.current_position_direction == 0:  # 当前没有持仓
                    # 计算第1次开仓数量
                    todo_qty = min(self.exchange1_buy_1_quantity, self.exchange2_sell_1_quantity) * self.order_ratio
                elif self.current_position_direction == 1:  # 当前long spread1
                    # 已有仓位，计算加仓数量
                    todo_qty = min(self.exchange1_buy_1_quantity, self.exchange2_sell_1_quantity) * self.order_ratio
                elif self.current_position_direction == 2:  # 当前long spread2
                    # 另一个方向有仓位，计算可以减仓的数量
                    depth_qty = min(self.exchange1_buy_1_quantity, self.exchange2_sell_1_quantity) * self.order_ratio
                    todo_qty = min(depth_qty, self.spread2_pos_qty)
                    

                # 假定是保证金交易，2个交易所，都是持有 usd

                # 最大可以开多少仓位
                # ?????????????? 需要调试  ????????????????
                # free used 什么意思
                # 作空的仓位，是什么
                can_op_qty_1 = self.exchange1_symbol1_free + self.exchange1_symbol2_free / self.exchange1_buy_1_price
                can_op_qty_2 = self.exchange2_symbol1_used + self.exchange2_symbol2_free / self.exchange2_sell_1_price
                qty_max = min(can_op_qty_1, can_op_qty_2)
                # 每次最多只能买的数量, 暂定为最大交易量的  1/10
                qty_by_cash_one = qty_max / 10
                todo_qty = min(todo_qty, qty_by_cash_one)
                
                # 计算出的交易量 < 交易所要求的最小量
                # 无法下单，忽略这次机会
                if todo_qty < self.exchange1_trade_min or todo_qty < self.exchange2_trade_min:
                    continue
                
                # 计算预计的收益，要是不够手续费，就略过这次机会
                # ???????????????????
                if todo_qty < self.exchange1_trade_min or todo_qty < self.exchange2_trade_min:
                    continue

                self.do_order_spread1(todo_qty)

            elif position_direction == 2:
                if self.current_position_direction == 0:  # 当前没有持仓
                    # 计算第1次开仓数量
                    todo_qty = min(self.exchange2_buy_1_quantity, self.exchange1_sell_1_quantity) * self.order_ratio
                elif self.current_position_direction == 2:  # 当前long spread2
                    # 已有仓位，计算加仓数量
                    todo_qty = min(self.exchange2_buy_1_quantity, self.exchange1_sell_1_quantity) * self.order_ratio
                elif self.current_position_direction == 1:  # 当前long spread1
                    # 另一个方向有仓位，计算可以减仓的数量
                    depth_qty = min(self.exchange2_buy_1_quantity, self.exchange1_sell_1_quantity) * self.order_ratio
                    todo_qty = min(depth_qty, self.spread1_pos_qty)

                # 假定是保证金交易，2个交易所，都是持有 usd

                # 最大可以开多少仓位
                # ?????????????? 需要调试  ????????????????
                # free used 什么意思
                # 作空的仓位，是什么
                can_op_qty_1 = self.exchange1_symbol1_used + self.exchange1_symbol2_free / self.exchange1_sell_1_price
                can_op_qty_2 = self.exchange2_symbol1_free + self.exchange2_symbol2_free / self.exchange2_buy_1_price
                qty_max = min(can_op_qty_1, can_op_qty_2)
                # 每次最多只能买的数量, 暂定为最大交易量的  1/10
                qty_by_cash_one = qty_max / 10
                todo_qty = min(todo_qty, qty_by_cash_one)
                
                # 计算出的交易量 < 交易所要求的最小量
                # 无法下单，忽略这次机会
                if todo_qty < self.exchange1_trade_min or todo_qty < self.exchange2_trade_min:
                    continue
                
                # 计算预计的收益，要是不够手续费，就略过这次机会
                # ???????????????????
                if todo_qty < self.exchange1_trade_min or todo_qty < self.exchange2_trade_min:
                    continue

                self.do_order_spread2(todo_qty)

            if self.spread1_pos_qty > 0:
                self.current_position_direction = 1
            elif self.spread2_pos_qty > 0:
                self.current_position_direction = 2
            else:
                self.current_position_direction = 0
                

