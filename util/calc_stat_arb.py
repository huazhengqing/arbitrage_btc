#!/usr/bin/python

import os
import sys
import time
import asyncio
import ccxt.async as ccxt
import numpy as np

sys.path.append("..")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))
import db_banzhuan
import bz_conf



# 注：只有少数交易所，支持卖出


# 统计套利搬砖
class calc_stat_arb():
    def __init__(self, exchange1, exchange2, db_currency_pair):
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.db = db_currency_pair
        #self.db.create_table_spread(exchange1, exchange2)
        
        self.exchange1_buy_1_price = 0.0
        self.exchange1_sell_1_price = 0.0
        
        self.exchange2_buy_1_price = 0.0
        self.exchange2_sell_1_price = 0.0

        self.exchange1_last_alive = 0
        self.exchange2_last_alive = 0
        self.check_data_timestamp = 0

        self.spread1List = []       # exchange1_buy1 - exchange2_sell1
        self.spread2List = []       # exchange2_buy1 - exchange1_sell1

        self.sma_window_size = 3600        # 多少根k线, 计算的时间跨度. 默认1秒1k线，计算1小时
        self.spread1_mean = None        # 均值
        self.spread1_stdev = None        # 方差
        self.spread2_mean = None
        self.spread2_stdev = None
        
        self.spread1_open_condition_stdev_coe = 2        # 价格超过方差多少倍，下单
        self.spread2_open_condition_stdev_coe = 2
        self.spread1_close_condition_stdev_coe = 0.3        # 价格小于方差多少倍，平仓
        self.spread2_close_condition_stdev_coe = 0.3

        # 0: no position
        # 1: long spread1(sell exchange1, buy exchange2)
        # 2: long spread2(buy exchange1, sell exchange2)
        self.current_position_direction = 0  

        self.spread1_pos_qty = 0
        self.spread2_pos_qty = 0

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
        if self.exchange1_buy_1_price <= 0 or self.exchange1_sell_1_price <= 0 or self.exchange2_buy_1_price <= 0 or self.exchange2_sell_1_price:
            return
        spread1 = self.exchange1_buy_1_price - self.exchange2_sell_1_price
        spread2 = self.exchange2_buy_1_price - self.exchange1_sell_1_price
        self.spread1List = self.add_to_list(self.spread1List, spread1, self.sma_window_size)
        self.spread2List = self.add_to_list(self.spread2List, spread2, self.sma_window_size)


    def do_it(self):
        self.fetch_history_data_from_db()
        while True:
            cur_t = int(time.time())
            # 每秒钟，计算1次
            if self.check_data_timestamp >= cur_t
                time.sleep(0.5)
                continue
            self.check_data_timestamp = cur_t
            self.fetch_data_from_db(self.check_data_timestamp)

            # 数据不足，不计算, 等待回够的数据
            if len(self.spread1List) < self.sma_window_size:
                time.sleep(0.5)
                continue
            
            # 超过 5 秒钟没有收到新数据，暂停，等新数据
            timeout_warn = 5
            if self.exchange1_last_alive < cur_t - timeout_warn or self.exchange2_last_alive < cur_t - timeout_warn:
                # 接收不到新数据，报警 ???????????
                # 检查帐户情况，是否需要人工操作
                # send_sms()   ?????????
                continue

            self.calc_sma_and_deviation()
            position_direction = self.calc_position_direction()

            
            #
            # 如果是保证金帐户，还要检查是不是安全
            #
            if position_direction == 0:
                continue
            elif position_direction == 1:
                if self.current_position_direction == 0:  # 当前没有持仓
                    # 开仓

                elif self.current_position_direction == 1:  # 当前long spread1
                    # 判断是否加仓
                    # 还有仓位，就加仓

                elif self.current_position_direction == 2:  # 当前long spread2
                    #平仓
                    

            elif position_direction == 2:
                if self.current_position_direction == 0:  # 当前没有持仓
                    # 开仓

                elif self.current_position_direction == 2:  # 当前long spread2
                    # 判断是否加仓
                    # 还有仓位，就加仓
                    
                elif self.current_position_direction == 1:  # 当前long spread1
                    #平仓


            if self.spread1_pos_qty > 0:
                self.current_position_direction = 1
            elif self.spread2_pos_qty > 0:
                self.current_position_direction = 2
            else:
                self.current_position_direction = 0

