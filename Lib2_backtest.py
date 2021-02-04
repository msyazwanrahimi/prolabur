#Import libraries
import os
import sys
import csv
import json
import math
import glob
import talib
import zipfile
import requests
import numpy as np
import pandas as pd
import pandas_ta as ta


from os import system, name
from datetime import datetime
from gann import gann_generate
from gann import priceMovement

CONST_SCRIPT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
CONST_SCRIPT_DIR_UP = os.path.abspath(CONST_SCRIPT_DIR + os.sep + os.pardir)
# CONST_SCRIPT_DIR_UP_UP = os.path.abspath(CONST_SCRIPT_DIR_UP + os.sep + os.pardir)
CONST_HISTORICAL_DATA = os.path.join(CONST_SCRIPT_DIR_UP, "historicalData")
CONST_JSON = os.path.join(CONST_HISTORICAL_DATA, "JSON")
CONST_RESULT = os.path.join(CONST_SCRIPT_DIR, "first strategy screener only")


class Backtest:

    def __init__(self, data_frame, df_main_result):
        self.main_dataframe = data_frame
        # print(df_main_result)
        self.result_dataframe = df_main_result
        self.list_master = self.result_dataframe.values.tolist()
        self.original_df_main_result = len(self.list_master)
    
    
    def btst_backtest(self, duration, long_duration, long_duration_period, backtest_comparison="Close"):

        def process_btst_backtest(list_price, list_date_tn, list_price_tn):
        
            criteria_1 = 0   # 
            N_backtest_comparison = "N"+backtest_comparison

            df_processing = pd.DataFrame(list(zip(list_price, list_date_tn, list_price_tn)), columns =['Close', 'NDate', N_backtest_comparison])
            df_processing['Change(%/100)'] = ((df_processing[N_backtest_comparison] - df_processing['Close'])/df_processing['Close'])
            
            for _index, _data in df_processing.iterrows():
                if (_data['Change(%/100)'] < criteria_1):
                    return "CL", _data[N_backtest_comparison], _data['NDate']
                elif (_data['Change(%/100)'] > criteria_1):
                    return "TP", _data[N_backtest_comparison], _data['NDate']

            return "SELL", df_processing.iloc[-1][N_backtest_comparison], df_processing.iloc[-1]['NDate']

        self.result_dataframe = self.result_dataframe.T
        first_time = True
        list_backtest_master = []
        for _index, _values in self.result_dataframe.iterrows():
            list_buffer_stock = []
            list_buffer_date = []
            list_buffer_price = []
            list_buffer_date_tn = []
            list_buffer_price_tn = []

            dateposition_positive = self.main_dataframe.index[self.main_dataframe['Date'] == _values[1]].tolist()[0]
            total_row = len(self.main_dataframe.index)
            dateposition = -abs(total_row - dateposition_positive)

            list_buffer = [_ix for _ix in range(duration+1)]
            list_buffer = np.add(list_buffer, (dateposition)).tolist()
            list_buffer = [item for item in list_buffer if item < 0]

            list_buffer_stock += [_values[0]]*(duration+1)
            list_buffer_date += [_values[1]]*(duration+1)
            list_buffer_price += [_values[2]]*(duration+1)
            list_buffer_date_tn += [self.main_dataframe.iloc[_data]['Date'] for _data in list_buffer]
            list_buffer_price_tn += [self.main_dataframe.iloc[_data][backtest_comparison] for _data in list_buffer]

            cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell = process_btst_backtest(list_buffer_price, list_buffer_date_tn, list_buffer_price_tn)
            priceMovementList = priceMovement(list_buffer_price, list_buffer_price_tn, list_buffer_date_tn)
            list_backtest_master_buffer = []
            list_backtest_master_buffer += [[list_buffer_stock[0]]]
            list_backtest_master_buffer += [[list_buffer_date[0]]]
            list_backtest_master_buffer += [[list_buffer_price[0]]]
            list_backtest_master_buffer += [[cl_tp_sell]]
            list_backtest_master_buffer += [[date_cl_tp_sell]]
            list_backtest_master_buffer += [[price_cl_tp_sell]]
            list_backtest_master_buffer += [[priceMovementList]]
            if first_time:
                list_backtest_master = list_backtest_master_buffer
                first_time = False
            else:
                for _index, data in enumerate(list_backtest_master):
                    data.extend(list_backtest_master_buffer[_index])

        return list_backtest_master

        # first_time = True
        # for _index, _data in enumerate(list_date_position):
        #     list_buffer = []
        #     list_buffer_date = [self.main_dataframe.iloc[(_data+1)]['Date']]
        #     list_buffer_price = [self.main_dataframe.iloc[(_data+1)]['Close']]
        #     cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell = process_btst_backtest(self.main_dataframe.iloc[_data]['Close'], list_buffer_price, list_buffer_date)

        #     list_buffer += [[cl_tp_sell]]
        #     list_buffer += [[date_cl_tp_sell]]
        #     list_buffer += [[price_cl_tp_sell]]

        #     if first_time:
        #         self.list_master += list_buffer
        #         first_time = False
        #     else:
        #         for _index, data in enumerate(self.list_master):
        #             if (_index >= self.original_df_main_result):
        #                 data.extend(list_buffer[_index-self.original_df_main_result])

        # return self.list_master


    def max_swing_profit_backtest(self, duration, long_duration, long_duration_period, backtest_comparison="Close"):

        def process_max_profit_backtest(list_price, list_date_tn, list_price_tn):

            criteria_1 = 0   # 
            N_backtest_comparison = "N"+backtest_comparison

            df_processing = pd.DataFrame(list(zip(list_price[1:], list_date_tn[1:], list_price_tn[1:])), columns =['Close', 'NDate', N_backtest_comparison])
            df_processing['Change'] = ((df_processing[N_backtest_comparison] - df_processing['Close'])/df_processing['Close'])
            max_profit = criteria_1
            min_profit = criteria_1
            max_profit_index = 0
            min_profit_index = 0
            const_profit_index = 0

            max_profit = max(df_processing[N_backtest_comparison])
            max_profit_index_positive = df_processing[df_processing[N_backtest_comparison] == max_profit].index.tolist()[0]
            total_row = len(df_processing.index)
            max_profit_index = -abs(total_row - max_profit_index_positive)

            if (df_processing.iloc[max_profit_index][N_backtest_comparison] > df_processing.iloc[max_profit_index]['Close']):
                return "TP", df_processing.iloc[max_profit_index][N_backtest_comparison], df_processing.iloc[max_profit_index]['NDate']
            elif (df_processing.iloc[max_profit_index][N_backtest_comparison] < df_processing.iloc[max_profit_index]['Close']):
                return "CL", df_processing.iloc[max_profit_index][N_backtest_comparison], df_processing.iloc[max_profit_index]['NDate']
            else:
                return "SELL", df_processing.iloc[max_profit_index][N_backtest_comparison], df_processing.iloc[max_profit_index]['NDate']
            
        self.result_dataframe = self.result_dataframe.T
        first_time = True
        list_backtest_master = []
        for _index, _values in self.result_dataframe.iterrows():

            list_buffer_stock = []
            list_buffer_date = []
            list_buffer_price = []
            list_buffer_date_tn = []
            list_buffer_price_tn = []

            dateposition_positive = self.main_dataframe.index[self.main_dataframe['Date'] == _values[1]].tolist()[0]
            total_row = len(self.main_dataframe.index)
            dateposition = -abs(total_row - dateposition_positive)

            list_buffer = [_ix for _ix in range(duration+1)]
            list_buffer = np.add(list_buffer, (dateposition)).tolist()
            list_buffer = [item for item in list_buffer if item < 0]

            list_buffer_stock += [_values[0]]*(duration+1)
            list_buffer_date += [_values[1]]*(duration+1)
            list_buffer_price += [_values[2]]*(duration+1)
            list_buffer_date_tn += [self.main_dataframe.iloc[_data]['Date'] for _data in list_buffer]
            list_buffer_price_tn += [self.main_dataframe.iloc[_data][backtest_comparison] for _data in list_buffer]

            cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell = process_max_profit_backtest(list_buffer_price, list_buffer_date_tn, list_buffer_price_tn)
            priceMovementList = priceMovement(list_buffer_price, list_buffer_price_tn, list_buffer_date_tn)
            list_backtest_master_buffer = []
            list_backtest_master_buffer += [[list_buffer_stock[0]]]
            list_backtest_master_buffer += [[list_buffer_date[0]]]
            list_backtest_master_buffer += [[list_buffer_price[0]]]
            list_backtest_master_buffer += [[cl_tp_sell]]
            list_backtest_master_buffer += [[date_cl_tp_sell]]
            list_backtest_master_buffer += [[price_cl_tp_sell]]
            list_backtest_master_buffer += [[priceMovementList]]
            if first_time:
                list_backtest_master = list_backtest_master_buffer
                first_time = False
            else:
                for _index, data in enumerate(list_backtest_master):
                    data.extend(list_backtest_master_buffer[_index])

        return list_backtest_master


    def trading_plan(self, duration, take_profit, cut_loss, long_duration, long_duration_period, backtest_comparison="Close"):

        def process_tp_cl_and_sell(list_price, list_date_tn, list_price_tn):

            criteria_1 = int(take_profit)/100   # profit
            criteria_2 = -int(cut_loss)/100 # loss
            N_backtest_comparison = "N"+backtest_comparison

            df_processing = pd.DataFrame(list(zip(list_price, list_date_tn, list_price_tn)), columns =['Close', 'Date', N_backtest_comparison])
            # print(df_processing)
            df_processing['Change(%)'] = ((df_processing[N_backtest_comparison] - df_processing['Close'])/df_processing['Close'])
            
            for _index, _data in df_processing.iterrows():
                if (_data['Change(%)'] <= criteria_2):
                    # return cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell
                    return "CL", _data[N_backtest_comparison], _data['Date']
                elif (_data['Change(%)'] >= criteria_1):
                    return "TP", _data[N_backtest_comparison], _data['Date']

            return "SELL", df_processing.iloc[-1][N_backtest_comparison], df_processing.iloc[-1]['Date']
        

        self.result_dataframe = self.result_dataframe.T
        first_time = True
        list_backtest_master = []
        for _index, _values in self.result_dataframe.iterrows():

            list_buffer_stock = []
            list_buffer_date = []
            list_buffer_price = []
            list_buffer_date_tn = []
            list_buffer_price_tn = []
            # print(_values[0], _values[1], _values[2])
            # print(self.result_dataframe, len(self.result_dataframe))
            # print(self.result_dataframe[1][0])
            dateposition_positive = self.main_dataframe.index[self.main_dataframe['Date'] == _values[1]].tolist()[0]
            total_row = len(self.main_dataframe.index)
            dateposition = -abs(total_row - dateposition_positive)
            # print(dateposition)

            list_buffer = [_ix for _ix in range(duration+1)]
            list_buffer = np.add(list_buffer, (dateposition)).tolist()
            list_buffer = [item for item in list_buffer if item < 0]

            list_buffer_stock += [_values[0]]*(duration+1)
            list_buffer_date += [_values[1]]*(duration+1)
            list_buffer_price += [_values[2]]*(duration+1)
            list_buffer_date_tn += [self.main_dataframe.iloc[_data]['Date'] for _data in list_buffer]
            list_buffer_price_tn += [self.main_dataframe.iloc[_data][backtest_comparison] for _data in list_buffer]
            # print(list_buffer_price_tn)

            cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell = process_tp_cl_and_sell(list_buffer_price, list_buffer_date_tn, list_buffer_price_tn)
            priceMovementList = priceMovement(list_buffer_price, list_buffer_price_tn, list_buffer_date_tn)
            # print(cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell)
            # 'Stock', 'T0_Date', 'T0_Close', 'Action', 'T1_Date', 'T1_Close'
            list_backtest_master_buffer = []
            list_backtest_master_buffer += [[list_buffer_stock[0]]]
            list_backtest_master_buffer += [[list_buffer_date[0]]]
            list_backtest_master_buffer += [[list_buffer_price[0]]]
            list_backtest_master_buffer += [[cl_tp_sell]]
            list_backtest_master_buffer += [[date_cl_tp_sell]]
            list_backtest_master_buffer += [[price_cl_tp_sell]]

            list_backtest_master_buffer += [[priceMovementList]]
            if first_time:
                list_backtest_master = list_backtest_master_buffer
                first_time = False
            else:
                for _index, data in enumerate(list_backtest_master):
                    data.extend(list_backtest_master_buffer[_index])

        return list_backtest_master