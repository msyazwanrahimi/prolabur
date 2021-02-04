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


CONST_SCRIPT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
CONST_SCRIPT_DIR_UP = os.path.abspath(CONST_SCRIPT_DIR + os.sep + os.pardir)
# CONST_SCRIPT_DIR_UP_UP = os.path.abspath(CONST_SCRIPT_DIR_UP + os.sep + os.pardir)
CONST_HISTORICAL_DATA = os.path.join(CONST_SCRIPT_DIR_UP, "historicalData")
CONST_JSON = os.path.join(CONST_HISTORICAL_DATA, "JSON")
CONST_RESULT = os.path.join(CONST_SCRIPT_DIR, "first strategy screener only")

class Strategy:

    def __init__(self, data_frame):
        self.main_dataframe = data_frame
        self.list_master = []

    def poa_strategy(self, stock, duration, dateposition, long_duration, long_duration_period):

        print(stock)
        list_date_position = []
        list_long_duration_dateposition = []

        if (long_duration):
            list_long_duration_dateposition = [_ix for _ix in range(long_duration_period)]
            list_long_duration_dateposition = np.add(list_long_duration_dateposition, (dateposition)).tolist()
            list_long_duration_dateposition = [item for item in list_long_duration_dateposition if item < 0]
        else:
            list_long_duration_dateposition = [dateposition]

        self.main_dataframe['rsiClose'] = ta.rsi(self.main_dataframe['Close'], 14)
        self.main_dataframe.fillna(value={'rsiClose': 0}, inplace=True)
        self.main_dataframe.dropna(inplace=True)
        self.main_dataframe['fastk'], self.main_dataframe['fastd'] = talib.STOCH(self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
        self.main_dataframe['sma5'] = talib.SMA(self.main_dataframe['Close'], timeperiod=5)
        self.main_dataframe['sma10'] = talib.SMA(self.main_dataframe['Close'], timeperiod=10)
        self.main_dataframe['sma20'] = talib.SMA(self.main_dataframe['Close'], timeperiod=20)
        self.main_dataframe['sma30'] = talib.SMA(self.main_dataframe['Close'], timeperiod=30)
        self.main_dataframe['sma50'] = talib.SMA(self.main_dataframe['Close'], timeperiod=50)
        self.main_dataframe['sma200'] = talib.SMA(self.main_dataframe['Close'], timeperiod=200)
        self.main_dataframe['averagevolume10'] = self.main_dataframe['Volume'].rolling(10).mean()

        first_time = True
        for dateposition in list_long_duration_dateposition:

            # btst strategy Power of Average
            cd_1 = (self.main_dataframe.iloc[dateposition]['sma10'] > self.main_dataframe.iloc[dateposition]['sma30'])  # 1. MA 10 atas MA 30
            cd_2 = (self.main_dataframe.iloc[dateposition]['sma5'] > self.main_dataframe.iloc[dateposition]['sma10'])   # 2. MA 5 atas MA 10 
            cd_3 = (self.main_dataframe.iloc[dateposition]['sma20']<=self.main_dataframe.iloc[dateposition]['Close'])    # 3. MA 20 < Close
            cd_4 = (self.main_dataframe.iloc[dateposition]['sma50'] < self.main_dataframe.iloc[dateposition]['Close'])   # 4. MA 50 < Close
            cd_5 = (self.main_dataframe.iloc[dateposition]['sma200'] < self.main_dataframe.iloc[dateposition]['Close'])   # 5. MA 200 < Close
            cd_6 = (self.main_dataframe.iloc[dateposition]['Close'] > self.main_dataframe.iloc[dateposition]['Open'])   # 6. Candlestick = hijau
            cd_7 = (self.main_dataframe.iloc[dateposition]['Close'] >= 0.30)   # 7. Avoid Penny Stock
            cd_8 = (self.main_dataframe.iloc[dateposition]['averagevolume10'] > 5000000)  # 8. Avg Volume 10 > 5000000
            cd_9 = (self.main_dataframe.iloc[dateposition]['fastk'] >= self.main_dataframe.iloc[dateposition]['fastd'])   # 9. stochastic rsi k >= d
            cd_10 = ((self.main_dataframe.iloc[dateposition]['fastk'] < 40) & (self.main_dataframe.iloc[dateposition]['fastd'] < 40))   # 10. stochastic rsi < 40
            cd_11 = ((self.main_dataframe.iloc[dateposition]['High'] != self.main_dataframe.iloc[dateposition]['Close'])
                    | (self.main_dataframe.iloc[dateposition]['Low'] != self.main_dataframe.iloc[dateposition]['Close']))   # 11. Avoid no transaction candlestick

            list_buffer = []
            if (cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6 & cd_7 & cd_8 & cd_9 & cd_10 & cd_11):

                list_buffer += [[stock]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Date']]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Close']]]

                if first_time:
                    self.list_master = list_buffer
                    first_time = False
                else:
                    for _index, data in enumerate(self.list_master):
                        data.extend(list_buffer[_index])

            # print(self.list_master)
        return self.list_master

    def ms_strategy(self, stock, duration, dateposition, long_duration, long_duration_period):

        print(stock)
        list_date_position = []
        list_long_duration_dateposition = []

        if (long_duration):
            list_long_duration_dateposition = [_ix for _ix in range(long_duration_period)]
            list_long_duration_dateposition = np.add(list_long_duration_dateposition, (dateposition)).tolist()
            list_long_duration_dateposition = [item for item in list_long_duration_dateposition if item < 0]
        else:
            list_long_duration_dateposition = [dateposition]

        self.main_dataframe['rsiClose'] = ta.rsi(self.main_dataframe['Close'], 14)
        self.main_dataframe.fillna(value={'rsiClose': 0}, inplace=True)
        self.main_dataframe.dropna(inplace=True)
        self.main_dataframe['fastk'], self.main_dataframe['fastd'] = talib.STOCH(self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
        self.main_dataframe['sma10'] = talib.SMA(self.main_dataframe['Close'], timeperiod=10)
        self.main_dataframe['sma20'] = talib.SMA(self.main_dataframe['Close'], timeperiod=20)
        self.main_dataframe['averagevolume10'] = self.main_dataframe['Volume'].rolling(10).mean()

        first_time = True
        for dateposition in list_long_duration_dateposition:
            
            cd_1 = ((self.main_dataframe.iloc[dateposition]['fastk'] < 40) & (self.main_dataframe.iloc[dateposition]['fastd'] < 40))   # 1. stochastic rsi < 40
            cd_2 = (self.main_dataframe.iloc[dateposition]['sma10'] < self.main_dataframe.iloc[dateposition]['Close'])   # 2. MA 10 < Close
            cd_3 = (self.main_dataframe.iloc[dateposition]['sma20'] < self.main_dataframe.iloc[dateposition]['Close'])   # 3. MA 20 < Close
            cd_4 = (self.main_dataframe.iloc[dateposition]['Close'] >= 0.30)   # 4. Avoid Penny Stock
            cd_5 = (self.main_dataframe.iloc[dateposition]['fastk'] >= self.main_dataframe.iloc[dateposition]['fastd'])   # 5. stochastic rsi k >= d
            cd_6 = ((self.main_dataframe.iloc[dateposition]['Volume']) > (self.main_dataframe.iloc[dateposition]['averagevolume10']))  # 6. Volume > Avg Volume 10
            cd_7 = (self.main_dataframe.iloc[dateposition]['Close'] > self.main_dataframe.iloc[dateposition]['Open'])   # 7. Candlestick = hijau
            cd_8 = ((self.main_dataframe.iloc[dateposition]['High'] != self.main_dataframe.iloc[dateposition]['Close'])
                    | (self.main_dataframe.iloc[dateposition]['Low'] != self.main_dataframe.iloc[dateposition]['Close']))   # 8. Avoid no transaction candlestick
        
            list_buffer = []
            if (cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6 & cd_7 & cd_8):

                list_buffer += [[stock]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Date']]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Close']]]

                if first_time:
                    self.list_master = list_buffer
                    first_time = False
                else:
                    for _index, data in enumerate(self.list_master):
                        data.extend(list_buffer[_index])

            # print(self.list_master)
        return self.list_master
    
    def _3m_stoch_rsi_strategy(self, stock, duration, dateposition, long_duration, long_duration_period):

        print(stock)
        list_date_position = []
        list_long_duration_dateposition = []

        if (long_duration):
            list_long_duration_dateposition = [_ix for _ix in range(long_duration_period)]
            list_long_duration_dateposition = np.add(list_long_duration_dateposition, (dateposition)).tolist()
            list_long_duration_dateposition = [item for item in list_long_duration_dateposition if item < 0]
        else:
            list_long_duration_dateposition = [dateposition]

        self.main_dataframe['rsiClose'] = ta.rsi(self.main_dataframe['Close'], 14)
        self.main_dataframe.fillna(value={'rsiClose': 0}, inplace=True)
        self.main_dataframe.dropna(inplace=True)
        self.main_dataframe['fastk'], self.main_dataframe['fastd'] = talib.STOCH(self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
        self.main_dataframe['sma20'] = talib.SMA(self.main_dataframe['Close'], timeperiod=20)
        self.main_dataframe['sma50'] = talib.SMA(self.main_dataframe['Close'], timeperiod=50)
        self.main_dataframe['sma200'] = talib.SMA(self.main_dataframe['Close'], timeperiod=200)
        self.main_dataframe['averagevolume10'] = self.main_dataframe['Volume'].rolling(10).mean()

        first_time = True
        for dateposition in list_long_duration_dateposition:
            
            # mid-swing strategy 3M + Stochastic RSI
            cd_1 = ((self.main_dataframe.iloc[dateposition]['fastk'] < 40) & (self.main_dataframe.iloc[dateposition]['fastd'] < 40))   # 1. stochastic rsi < 40
            cd_2 = (self.main_dataframe.iloc[dateposition]['fastk'] >= self.main_dataframe.iloc[dateposition]['fastd'])   # 2. stochastic rsi k >= d
            cd_3 = (self.main_dataframe.iloc[dateposition]['sma20'] < self.main_dataframe.iloc[dateposition]['Close'])   # 3. MA 20 < Close
            cd_4 = (self.main_dataframe.iloc[dateposition]['sma50'] < self.main_dataframe.iloc[dateposition]['Close'])   # 4. MA 50 < Close
            cd_5 = (self.main_dataframe.iloc[dateposition]['sma200'] < self.main_dataframe.iloc[dateposition]['Close'])   # 5. MA 200 < Close
            cd_6 = (self.main_dataframe.iloc[dateposition]['Close'] > self.main_dataframe.iloc[dateposition]['Open'])   # 6. Candlestick = hijau
            cd_7 = (self.main_dataframe.iloc[dateposition]['Close'] >= 0.30)   # 7. Avoid Penny Stock
            cd_8 = ((self.main_dataframe.iloc[dateposition]['Volume']) > (self.main_dataframe.iloc[dateposition]['averagevolume10']))  # 8. Volume > Avg Volume 10
            cd_9 = ((self.main_dataframe.iloc[dateposition]['High'] != self.main_dataframe.iloc[dateposition]['Close'])
                    | (self.main_dataframe.iloc[dateposition]['Low'] != self.main_dataframe.iloc[dateposition]['Close']))   # 9. Avoid no transaction candlestick
            
            list_buffer = []
            if (cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6 & cd_7 & cd_8 & cd_9):

                list_buffer += [[stock]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Date']]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Close']]]

                if first_time:
                    self.list_master = list_buffer
                    first_time = False
                else:
                    for _index, data in enumerate(self.list_master):
                        data.extend(list_buffer[_index])
            
            # print(self.list_master)
        return self.list_master
    
    def ema_rsi_strategy(self, stock, duration, dateposition, long_duration, long_duration_period):

        print(stock)
        list_date_position = []
        list_long_duration_dateposition = []

        if (long_duration):
            list_long_duration_dateposition = [_ix for _ix in range(long_duration_period)]
            list_long_duration_dateposition = np.add(list_long_duration_dateposition, (dateposition)).tolist()
            list_long_duration_dateposition = [item for item in list_long_duration_dateposition if item < 0]
        else:
            list_long_duration_dateposition = [dateposition]

        self.main_dataframe['rsiClose'] = ta.rsi(self.main_dataframe['Close'], 14)
        self.main_dataframe.fillna(value={'rsiClose': 0}, inplace=True)
        self.main_dataframe.dropna(inplace=True)
        self.main_dataframe['fastk'], self.main_dataframe['fastd'] = talib.STOCH(self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
        self.main_dataframe['ema7'] = talib.EMA(self.main_dataframe['Close'], timeperiod=7)
        self.main_dataframe['ema21'] = talib.EMA(self.main_dataframe['Close'], timeperiod=21)
        self.main_dataframe['averagevolume10'] = self.main_dataframe['Volume'].rolling(10).mean()

        first_time = True
        for dateposition in list_long_duration_dateposition:
            # mid-swing strategy EMA 7 cross atas EMA 21 + Stochastic RSI
            cd_1 = ((self.main_dataframe.iloc[dateposition]['fastk'] < 40) & (self.main_dataframe.iloc[dateposition]['fastd'] < 40))   # 1. stochastic rsi < 40
            cd_2 = (self.main_dataframe.iloc[dateposition]['fastk'] >= self.main_dataframe.iloc[dateposition]['fastd'])   # 2. stochastic rsi k >= d
            cd_3 = (self.main_dataframe.iloc[dateposition]['ema7'] < self.main_dataframe.iloc[dateposition]['Close'])   # 3. EMA 7 < Close
            cd_4 = (self.main_dataframe.iloc[dateposition]['ema7'] >= self.main_dataframe.iloc[dateposition]['ema21'])   # 4. EMA 7 >= EMA 21
            cd_5 = (self.main_dataframe.iloc[dateposition]['Close'] > self.main_dataframe.iloc[dateposition]['Open'])   # 5. Candlestick = hijau
            cd_6 = (self.main_dataframe.iloc[dateposition]['Close'] >= 0.30)   # 6. Avoid Penny Stock
            cd_7 = ((self.main_dataframe.iloc[dateposition]['Volume']) > (self.main_dataframe.iloc[dateposition]['averagevolume10']))  # 7. Volume > Avg Volume 10
            cd_8 = ((self.main_dataframe.iloc[dateposition]['High'] != self.main_dataframe.iloc[dateposition]['Close'])
                    | (self.main_dataframe.iloc[dateposition]['Low'] != self.main_dataframe.iloc[dateposition]['Close']))   # 8. Avoid no transaction candlestick
            
            list_buffer = []
            if (cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6 & cd_7 & cd_8):

                list_buffer += [[stock]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Date']]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Close']]]

                if first_time:
                    self.list_master = list_buffer
                    first_time = False
                else:
                    for _index, data in enumerate(self.list_master):
                        data.extend(list_buffer[_index])
            
            # print(self.list_master)
        return self.list_master

    def shortTerm_swing_strategy(self, stock, duration, dateposition, long_duration, long_duration_period):

        print(stock)
        list_date_position = []
        list_long_duration_dateposition = []

        if (long_duration):
            list_long_duration_dateposition = [_ix for _ix in range(long_duration_period)]
            list_long_duration_dateposition = np.add(list_long_duration_dateposition, (dateposition)).tolist()
            list_long_duration_dateposition = [item for item in list_long_duration_dateposition if item < 0]
        else:
            list_long_duration_dateposition = [dateposition]

        self.main_dataframe['rsiHigh'] = talib.RSI(self.main_dataframe['High'], 14)
        self.main_dataframe['rsiLow'] = talib.RSI(self.main_dataframe['Low'], 14)
        self.main_dataframe['rsiClose'] = talib.RSI(self.main_dataframe['Close'], 14)
        self.main_dataframe.fillna(value={'rsiHigh': 0, 'rsiLow': 0, 'rsiClose': 0}, inplace=True)
        self.main_dataframe.dropna(inplace=True)
        self.main_dataframe['fastk'], self.main_dataframe['fastd'] = talib.STOCH(self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
        self.main_dataframe['sma5'] = talib.SMA(self.main_dataframe['Close'], timeperiod=5)
        self.main_dataframe['sma10'] = talib.SMA(self.main_dataframe['Close'], timeperiod=10)
        self.main_dataframe['averagevolume5'] = self.main_dataframe['Volume'].rolling(5).mean()
        self.main_dataframe['averagevolume10'] = self.main_dataframe['Volume'].rolling(10).mean()

        first_time = True
        for dateposition in list_long_duration_dateposition:
            #first strategy
            cd_1 = (self.main_dataframe.iloc[dateposition]['fastk']>self.main_dataframe.iloc[dateposition]['fastd'])
            cd_2 = ((self.main_dataframe.iloc[dateposition]['fastk']<=40)&(self.main_dataframe.iloc[dateposition]['fastd']<=40))
            cd_3 = ((self.main_dataframe.iloc[dateposition]['averagevolume5']>=1000000)&(self.main_dataframe.iloc[dateposition]['Volume']>=10000000))
            cd_4 = (self.main_dataframe.iloc[dateposition]['Close']>=0.40)   #Avoid Penny Stock
            cd_5 = ((self.main_dataframe.iloc[dateposition]['Close'])>(self.main_dataframe.iloc[dateposition]['Open']))
            cd_6 = ((self.main_dataframe.iloc[dateposition]['sma10']<self.main_dataframe.iloc[dateposition]['Close']))
                
            list_buffer = []
            if (cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6):

                list_buffer += [[stock]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Date']]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Close']]]

                if first_time:
                    self.list_master = list_buffer
                    first_time = False
                else:
                    for _index, data in enumerate(self.list_master):
                        data.extend(list_buffer[_index])
            
            # print(self.list_master)
        return self.list_master

    def midTerm_swing_strategy(self, stock, duration, dateposition, long_duration, long_duration_period):

        print(stock)
        list_date_position = []
        list_long_duration_dateposition = []

        if (long_duration):
            list_long_duration_dateposition = [_ix for _ix in range(long_duration_period)]
            list_long_duration_dateposition = np.add(list_long_duration_dateposition, (dateposition)).tolist()
            list_long_duration_dateposition = [item for item in list_long_duration_dateposition if item < 0]
        else:
            list_long_duration_dateposition = [dateposition]

        self.main_dataframe['rsiHigh'] = talib.RSI(self.main_dataframe['High'], 14)
        self.main_dataframe['rsiLow'] = talib.RSI(self.main_dataframe['Low'], 14)
        self.main_dataframe['rsiClose'] = talib.RSI(self.main_dataframe['Close'], 14)
        self.main_dataframe.fillna(value={'rsiHigh': 0, 'rsiLow': 0, 'rsiClose': 0}, inplace=True)
        self.main_dataframe.dropna(inplace=True)
        self.main_dataframe['fastk'], self.main_dataframe['fastd'] = talib.STOCH(self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
        self.main_dataframe['sma5'] = talib.SMA(self.main_dataframe['Close'], timeperiod=5)
        self.main_dataframe['sma10'] = talib.SMA(self.main_dataframe['Close'], timeperiod=10)
        self.main_dataframe['sma20'] = talib.SMA(self.main_dataframe['Close'], timeperiod=20)
        self.main_dataframe['sma30'] = talib.SMA(self.main_dataframe['Close'], timeperiod=30)
        self.main_dataframe['sma40'] = talib.SMA(self.main_dataframe['Close'], timeperiod=40)
        self.main_dataframe['sma50'] = talib.SMA(self.main_dataframe['Close'], timeperiod=50)
        self.main_dataframe['sma200'] = talib.SMA(self.main_dataframe['Close'], timeperiod=200)
        self.main_dataframe['averagevolume5'] = self.main_dataframe['Volume'].rolling(5).mean()
        self.main_dataframe['averagevolume10'] = self.main_dataframe['Volume'].rolling(10).mean()

        first_time = True
        for dateposition in list_long_duration_dateposition:
        # second_strategy
            cd_1 = (self.main_dataframe.iloc[dateposition]['sma20']>self.main_dataframe.iloc[dateposition]['sma40'])
            cd_2 = ((self.main_dataframe.iloc[dateposition]['fastk']<=40)&(self.main_dataframe.iloc[dateposition]['fastd']<=40))
            cd_3 = ((self.main_dataframe.iloc[dateposition]['averagevolume5']>=1000000)&(self.main_dataframe.iloc[dateposition]['Volume']>=10000000))
            cd_4 = (self.main_dataframe.iloc[dateposition]['Close']>=0.40)   #Avoid Penny Stock
            cd_5 = ((self.main_dataframe.iloc[dateposition]['Close'])>(self.main_dataframe.iloc[dateposition]['Open']))
            cd_6 = ((self.main_dataframe.iloc[dateposition]['sma20']<self.main_dataframe.iloc[dateposition]['Close']))
                
            list_buffer = []
            if (cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6):

                list_buffer += [[stock]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Date']]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Close']]]

                if first_time:
                    self.list_master = list_buffer
                    first_time = False
                else:
                    for _index, data in enumerate(self.list_master):
                        data.extend(list_buffer[_index])
            
            # print(self.list_master)
        return self.list_master

    def threeMA_n_MACD(self, stock, duration, dateposition, long_duration, long_duration_period):

        print(stock)
        list_date_position = []
        list_long_duration_dateposition = []

        if (long_duration):
            list_long_duration_dateposition = [_ix for _ix in range(long_duration_period)]
            list_long_duration_dateposition = np.add(list_long_duration_dateposition, (dateposition)).tolist()
            list_long_duration_dateposition = [item for item in list_long_duration_dateposition if item < 0]
        else:
            list_long_duration_dateposition = [dateposition]
        self.main_dataframe['macd'],self.main_dataframe['macdsignal'], self.main_dataframe['macdhist'] = talib.MACD(self.main_dataframe['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        self.main_dataframe['rsiHigh'] = talib.RSI(self.main_dataframe['High'], 14)
        self.main_dataframe['rsiLow'] = talib.RSI(self.main_dataframe['Low'], 14)
        self.main_dataframe['rsiClose'] = talib.RSI(self.main_dataframe['Close'], 14)
        self.main_dataframe.fillna(value={'rsiHigh': 0, 'rsiLow': 0, 'rsiClose': 0}, inplace=True)
        self.main_dataframe.dropna(inplace=True)
        self.main_dataframe['fastk'], self.main_dataframe['fastd'] = talib.STOCH(self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], self.main_dataframe['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
        self.main_dataframe['sma50'] = talib.SMA(self.main_dataframe['Close'], timeperiod=50)
        self.main_dataframe['sma10'] = talib.SMA(self.main_dataframe['Close'], timeperiod=10)
        self.main_dataframe['sma20'] = talib.SMA(self.main_dataframe['Close'], timeperiod=20)
        self.main_dataframe['averagevolume5'] = self.main_dataframe['Volume'].rolling(5).mean()
        self.main_dataframe['averagevolume10'] = self.main_dataframe['Volume'].rolling(10).mean()

        first_time = True
        for dateposition in list_long_duration_dateposition:
        # second_strategy
            cd_1 = (self.main_dataframe.iloc[dateposition]['macd']>self.main_dataframe.iloc[dateposition]['macdsignal'])
            cd_2 = ((self.main_dataframe.iloc[dateposition]['fastk']<=40)&(self.main_dataframe.iloc[dateposition]['fastd']<=40))
            cd_3 = ((self.main_dataframe.iloc[dateposition]['averagevolume5']>=1000000)&(self.main_dataframe.iloc[dateposition]['Volume']>=10000000))
            cd_4 = (self.main_dataframe.iloc[dateposition]['Close']>=0.40)   #Avoid Penny Stock
            cd_5 = ((self.main_dataframe.iloc[dateposition]['Close'])>(self.main_dataframe.iloc[dateposition]['Open']))
            cd_6 = ((self.main_dataframe.iloc[dateposition]['sma10']>self.main_dataframe.iloc[dateposition]['sma20']))
            cd_7 = ((self.main_dataframe.iloc[dateposition]['sma20']>self.main_dataframe.iloc[dateposition]['sma50']))
                
            list_buffer = []
            if (cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6, cd_7):

                list_buffer += [[stock]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Date']]]
                list_buffer += [[self.main_dataframe.iloc[dateposition]['Close']]]

                if first_time:
                    self.list_master = list_buffer
                    first_time = False
                else:
                    for _index, data in enumerate(self.list_master):
                        data.extend(list_buffer[_index])
            
            # print(self.list_master)
        return self.list_master