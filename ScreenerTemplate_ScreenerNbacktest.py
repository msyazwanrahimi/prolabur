# 1. Import libraries
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

#2. Define directory path
CONST_SCRIPT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
CONST_SCRIPT_DIR_UP = os.path.abspath(CONST_SCRIPT_DIR + os.sep + os.pardir)
CONST_SCRIPT_DIR_UP_UP = os.path.abspath(CONST_SCRIPT_DIR_UP + os.sep + os.pardir)
CONST_HISTORICAL_DATA = os.path.join(CONST_SCRIPT_DIR_UP_UP, "historicalData")
CONST_JSON = os.path.join(CONST_HISTORICAL_DATA, "JSON")
CONST_RESULT = os.path.join(CONST_SCRIPT_DIR, "first strategy screener only")

#3. Unzip Data
if not os.path.exists(CONST_JSON):
    # os.makedirs(CONST_JSON)
    with zipfile.ZipFile(CONST_JSON+".zip", 'r') as unzip_ref:
        unzip_ref.extractall(CONST_HISTORICAL_DATA)
        unzip_ref.close()

#4. Get input time criteria from user
testdatefullstring = input("Please enter the date you want to test: (YYYY-MM-DD)")
testduration = int(input("Please enter the duration you want to backtest in days as unit: "))
testdate_y, testdate_m, testdate_d = [ int (x) for x in testdatefullstring.split('-')]
testdate = datetime(testdate_y, testdate_m, testdate_d)


# define our clear function 
def clear(): 
  
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear')

counter_result = []
testdate_result_price = []
ndayafter_price = []
list_cl_tp_sell = []
list_price_cl_tp_sell = []
list_date_cl_tp_sell = []

path, dirs, files = next(os.walk(CONST_JSON))
total_stock = len(files)
scanned_stock = 0
stock_found = 0

for _file in os.listdir(CONST_JSON):

    symbol, stock, code = _file.split('_')
    code = code[:-5]

    df = pd.read_json(os.path.join(CONST_JSON, _file), orient='index', convert_axes=False, dtype=object)
    # df = pd.read_json(os.path.join(CONST_JSON, "h_VIS_0120.json"), orient='index', convert_axes=False, dtype=object)
    df.reset_index(inplace=True)
    df.rename(columns={'index':'Date'}, inplace=True)
    df.sort_values('Date', inplace=True, ascending=True)
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df = df.apply(pd.to_numeric, errors='ignore')
    # print(df.tail(35))
    df.reset_index(drop=True, inplace=True)

    if (testdatefullstring not in df['Date'].tolist()):
        continue

    changes_of_time = (df[df['Date'] == testdatefullstring].index.tolist()[0]) - (df.tail(1).index.tolist()[0])
    # print(changes_of_time)
    dateposition_positive = df[df['Date'] == testdatefullstring].index.tolist()[0]
    # print(dateposition_positive)
    
    selected = df
    selected = selected.loc[:, ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    # selected.set_index('Date', drop=True, inplace=True)
    # selected.index = pd.to_datetime(selected.index)
    total_row = len(selected.index)
    dateposition = -abs(total_row - dateposition_positive)
    # print(selected.iloc[dateposition])

    selected['rsiClose'] = ta.rsi(selected['Close'], 14)
    # selected['rsiClose'] = talib.RSI(selected['Close'], 14)
    selected.fillna(value={'rsiClose': 0}, inplace=True)
    selected.dropna(inplace=True)
    selected['fastk'], selected['fastd'] = talib.STOCH(selected['rsiClose'], selected['rsiClose'], selected['rsiClose'], fastk_period=14, slowk_period=3, slowk_matype=talib.MA_Type.SMA, slowd_period=3, slowd_matype=talib.MA_Type.SMA)
    selected['sma20'] = talib.SMA(selected['Close'], timeperiod=20)
    selected['sma50'] = talib.SMA(selected['Close'], timeperiod=50)
    selected['sma200'] = talib.SMA(selected['Close'], timeperiod=200)
    selected['averagevolume5'] = selected['Volume'].rolling(5).mean()
    selected['averagevolume10'] = selected['Volume'].rolling(10).mean()
    
    # print(selected.tail(35))
    # print(selected.info())

    scanned_stock = scanned_stock+1
    progression = scanned_stock / total_stock * 100
    print("Scanning", str(scanned_stock), "of", str(total_stock), "stock(s)")
    print("Progression:", str(round(progression,2)), "%")
    print("Current Scanning Stock", stock)
    print((df.tail(1).index.tolist()[0]))

    if ((stock == "VIS") | (stock == "KRONO") | (stock == "SAMAIDEN")):
        print(selected.iloc[dateposition])
    # print(selected.iloc[dateposition])
    # mid-swing strategy 3M + Stochastic RSI
    cd_1 = ((selected.iloc[dateposition]['fastk'] < 40) & (selected.iloc[dateposition]['fastd'] < 40))   # 1. stochastic rsi < 40
    cd_2 = (selected.iloc[dateposition]['fastk']+1 >= selected.iloc[dateposition]['fastd'])   # 2. stochastic rsi k >= d
    cd_3 = (selected.iloc[dateposition]['sma20'] < selected.iloc[dateposition]['Close'])   # 3. MA 20 < Close
    cd_4 = (selected.iloc[dateposition]['sma50'] < selected.iloc[dateposition]['Close'])   # 4. MA 50 < Close
    cd_5 = (selected.iloc[dateposition]['sma200'] < selected.iloc[dateposition]['Close'])   # 5. MA 200 < Close
    cd_6 = (selected.iloc[dateposition]['Close'] > selected.iloc[dateposition]['Open'])   # 6. Candlestick = hijau
    cd_7 = (selected.iloc[dateposition]['Close'] >= 0.30)   # 7. Avoid Penny Stock
    # cd_8 = (selected.iloc[dateposition]['Volume'] >= 1000000)   # 8. Volume >= 1000000
    # cd_9 = (selected.iloc[dateposition]['averagevolume5'] >= 1000000)   # 9. Avg Volume 5 >= 1000000
    

    def processCLAndTP(test_date_price, list_price, list_date):
        
        list_test_date_price = [test_date_price] * 10
        criteria_1 = -0.05   # 5% loss
        criteria_2 = 0.10  # 10% profit
        # criteria_3 = 
        # criteria_4 = 
        df_processing = pd.DataFrame(list(zip(list_date, list_test_date_price, list_price)), columns =['Date', 'Close', 'NClose'])
        # df_processing['Change'] = (df_processing['NClose'] - df_processing['Close'])
        df_processing['Change(%)'] = ((df_processing['NClose'] - df_processing['Close'])/df_processing['Close'])
        print(df_processing)
        # print(df_processing.iloc[-1]['NClose'])
        # all((_cl <= criteria_1) for _cl in df_processing['Change(%)'])
        for _index, _data in df_processing.iterrows():
            if (_data['Change(%)'] <= criteria_1):
                # return cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell
                return "CL", _data['NClose'], _data['Date']
            elif (_data['Change(%)'] >= criteria_2):
                return "TP", _data['NClose'], _data['Date']

        return "SELL", df_processing.iloc[-1]['NClose'], df_processing.iloc[-1]['Date']
        print("processCLAndTP END")
    if(cd_1 & cd_2 & cd_3 & cd_4 & cd_5 & cd_6 & cd_7):

        list_buffer_price = [ selected.iloc[dateposition+_data+1]['Close'] for _data in range(int(testduration)) ]
        list_buffer_date = [ selected.iloc[dateposition+_data+1]['Date'] for _data in range(int(testduration)) ]
        cl_tp_sell, price_cl_tp_sell, date_cl_tp_sell = processCLAndTP(selected.iloc[dateposition]['Close'], list_buffer_price, list_buffer_date)
        list_cl_tp_sell.append(cl_tp_sell)
        list_price_cl_tp_sell.append(price_cl_tp_sell)
        list_date_cl_tp_sell.append(date_cl_tp_sell)
        counter_result.append(stock)
        testdate_result_price.append(selected.iloc[dateposition]['Close'])
        ndayafter_price.append(max(list_buffer_price))
        
    clear()

_close = str(testdatefullstring)+'Close'
df_result = pd.DataFrame(list(zip(counter_result, testdate_result_price, list_cl_tp_sell, list_price_cl_tp_sell, list_date_cl_tp_sell)), columns =['Stock', _close, 'Action', 'ActionPrice', 'ActionDate'])
df_result['Change'], df_result['Change(%)'] = (df_result['ActionPrice'] - df_result[_close]), ((df_result['ActionPrice'] - df_result[_close])/df_result[_close] * 100)
df_result['Result'] = (((df_result['Change(%)'] > 0) & (df_result['Action'] == 'SELL')) | (df_result['Action'] == 'TP'))*1
total_success = df_result[(df_result['Action'] == 'TP')].shape[0]
total_loss = df_result[(df_result['Action'] == 'CL')].shape[0]
total_sell = df_result[(df_result['Action'] == 'SELL')].shape[0]
total_win = df_result[(df_result['Result'] > 0)].shape[0]
total_loss = len(df_result.index) - total_win
print("Total Successful Counter", total_success)
print("Total Loss Counter", total_loss)
print("Total Sell Counter", total_sell)
print("Total Win", total_win)
print("Total Loss", total_loss)
print(df_result)
