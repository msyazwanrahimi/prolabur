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
from strategy import Strategy
from backtest import Backtest
from datetime import date, datetime, timedelta


CONST_SCRIPT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
CONST_SCRIPT_DIR_UP = os.path.abspath(CONST_SCRIPT_DIR + os.sep + os.pardir)
# CONST_SCRIPT_DIR_UP_UP = os.path.abspath(CONST_SCRIPT_DIR_UP + os.sep + os.pardir)
CONST_HISTORICAL_DATA = os.path.join(CONST_SCRIPT_DIR_UP, "historicalData")
CONST_JSON = os.path.join(CONST_HISTORICAL_DATA, "JSON")
CONST_RESULT = os.path.join(CONST_SCRIPT_DIR_UP, "LIB_2_RESULT")
CONST_RESULT_NOT_BACKTESTED = os.path.join(CONST_RESULT, "Without Backtest")
CONST_RESULT_BACKTESTED = os.path.join(CONST_RESULT, "With Backtest")


if not os.path.exists(CONST_JSON):
    # os.makedirs(CONST_JSON)
    with zipfile.ZipFile(CONST_JSON+".zip", 'r') as unzip_ref:
        unzip_ref.extractall(CONST_HISTORICAL_DATA)
        unzip_ref.close()
if not os.path.exists(CONST_RESULT):
    os.makedirs(CONST_RESULT)
if not os.path.exists(CONST_RESULT_NOT_BACKTESTED):
    os.makedirs(CONST_RESULT_NOT_BACKTESTED)
if not os.path.exists(CONST_RESULT_BACKTESTED):
    os.makedirs(CONST_RESULT_BACKTESTED)


def main(beginning_date="2021-01-04", duration=10, strategy_option=5, backtest_option=1, take_profit=2, cut_loss=1, long_duration=0, long_duration_period=20, backtest_comparison="Close", strategies_backtest={}):

    current_time = datetime.now()
    # format_current_time = current_time.strftime("%d%b%Y_%H_")
    format_date_time = current_time.strftime("%Y-%m-%d_%H%M%S")
    print(format_date_time)

    df_main_strategy_result = pd.DataFrame
    df_main_backtest_result = pd.DataFrame
    list_strategy_result = []
    list_backtest_result = []
    list_strategy_dateposition = []

    path, dirs, files = next(os.walk(CONST_JSON))
    total_stock = len(files)
    scanned_stock = 0
    stock_found = 0

    counter_result = []
    list_test_date_result_price = []
    list_test_date_result_date = []
    ndayafter_price = []
    list_cl_tp_sell = []
    list_price_cl_tp_sell = []
    list_date_cl_tp_sell = []


    # define our clear function 
    def clear(): 
    
        # for windows 
        if name == 'nt': 
            _ = system('cls') 
    
        # for mac and linux(here, os.name is 'posix') 
        else: 
            _ = system('clear')

    first_time = True
    # for _index, _file in enumerate(sorted(os.listdir(CONST_JSON), key=len)):
    for _index, _file in enumerate(os.listdir(CONST_JSON)):

        symbol, stock, code = _file.split('_')
        code = code[:-5]

        df_main = pd.read_json(os.path.join(CONST_JSON, _file), orient='index', convert_axes=False, dtype=object)
        df_main.reset_index(inplace=True)
        df_main.rename(columns={'index':'Date'}, inplace=True)
        df_main.sort_values('Date', inplace=True, ascending=True)
        df_main = df_main[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df_main = df_main.apply(pd.to_numeric, errors='ignore')
        df_main.reset_index(drop=True, inplace=True)

        if (testdatefullstring not in df_main['Date'].tolist()):
            continue

        dateposition_positive = df_main[df_main['Date'] == testdatefullstring].index.tolist()[0]
        df_main = df_main[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        total_row = len(df_main.index)
        dateposition = -abs(total_row - dateposition_positive)

        scanned_stock = scanned_stock+1
        progression = scanned_stock / total_stock * 100
        print("Scanning", str(scanned_stock), "of", str(total_stock), "stock(s)")
        print("Progression:", str(round(progression,2)), "%")
        print("Current Scanning Stock", stock)
        clear()
        
        if (strategy_option == 1):

            list_strategy_result = Strategy(df_main).poa_strategy(stock, duration, dateposition, long_duration, long_duration_period)
            if list_strategy_result:
                df_main_strategy_result = (pd.DataFrame(list_strategy_result))
                # print(df_main_strategy_result)
            else:
                pass

        elif (strategy_option == 2):
            list_strategy_result = Strategy(df_main).ms_strategy(stock, duration, dateposition, long_duration, long_duration_period)
            if list_strategy_result:
                df_main_strategy_result = (pd.DataFrame(list_strategy_result))
                # print(df_main_strategy_result)
            else:
                pass

        elif (strategy_option == 3):
            list_strategy_result = Strategy(df_main)._3m_stoch_rsi_strategy(stock, duration, dateposition, long_duration, long_duration_period)
            if list_strategy_result:
                df_main_strategy_result = (pd.DataFrame(list_strategy_result))
                # print(df_main_strategy_result)
            else:
                pass

        elif (strategy_option == 4):
            list_strategy_result = Strategy(df_main).ema_rsi_strategy(stock, duration, dateposition, long_duration, long_duration_period)
            if list_strategy_result:
                df_main_strategy_result = (pd.DataFrame(list_strategy_result))
                # print(df_main_strategy_result)
            else:
                pass
        elif (strategy_option == 5):
            list_strategy_result = Strategy(df_main).shortTerm_swing_strategy(stock, duration, dateposition, long_duration, long_duration_period)
            if list_strategy_result:
                df_main_strategy_result = (pd.DataFrame(list_strategy_result))
                # print(df_main_strategy_result)
            else:
                pass            
        elif (strategy_option == 6):
            list_strategy_result = Strategy(df_main).midTerm_swing_strategy(stock, duration, dateposition, long_duration, long_duration_period)
            if list_strategy_result:
                df_main_strategy_result = (pd.DataFrame(list_strategy_result))
                # print(df_main_strategy_result)
            else:
                pass      
        elif (strategy_option == 7):
            list_strategy_result = Strategy(df_main).threeMA_n_MACD(stock, duration, dateposition, long_duration, long_duration_period)
            if list_strategy_result:
                df_main_strategy_result = (pd.DataFrame(list_strategy_result))
                # print(df_main_strategy_result)
            else:
                pass 

        if (backtest_option != 0):
            if (backtest_option == 1):

                if list_strategy_result:
                    backtest_result = Backtest(df_main, df_main_strategy_result).btst_backtest(duration, long_duration, long_duration_period, backtest_comparison)
                    if first_time:
                        list_backtest_result = backtest_result
                        first_time = False
                    else:
                        for _index, data in enumerate(list_backtest_result):
                            data.extend(backtest_result[_index])

                    # df_main_backtest_result = (pd.DataFrame(list_backtest_result)).T
                    # print(df_main_backtest_result)
                else:
                    pass
            
            elif (backtest_option == 2):

                if list_strategy_result:
                    backtest_result = Backtest(df_main, df_main_strategy_result).max_swing_profit_backtest(duration, long_duration, long_duration_period, backtest_comparison)
                    if first_time:
                        list_backtest_result = backtest_result
                        first_time = False
                    else:
                        for _index, data in enumerate(list_backtest_result):
                            data.extend(backtest_result[_index])

                    # df_main_backtest_result = (pd.DataFrame(list_backtest_result)).T
                    # print(df_main_backtest_result)
                else:
                    pass
            
            elif (backtest_option == 3):

                if list_strategy_result:
                    backtest_result = Backtest(df_main, df_main_strategy_result).trading_plan(duration, take_profit, cut_loss, long_duration, long_duration_period, backtest_comparison)
                    if first_time:
                        list_backtest_result = backtest_result
                        first_time = False
                    else:
                        for _index, data in enumerate(list_backtest_result):
                            data.extend(backtest_result[_index])

                    # df_main_backtest_result = (pd.DataFrame(list_backtest_result)).T
                    # print(df_main_backtest_result)
                else:
                    pass

        else:
            if list_strategy_result:

                if ((strategy_option == 2) 
                    | (strategy_option == 3)
                    | (strategy_option == 4) ):
                   list_strategy_result =  [[item[0]] for item in list_strategy_result]

                backtest_result = list_strategy_result
                if first_time:
                    list_backtest_result = backtest_result
                    first_time = False
                else:
                    for _index, data in enumerate(list_backtest_result):
                        data.extend(backtest_result[_index])

    ##---- Display Result ----##
    df_main_backtest_result = pd.DataFrame()

    # beginning_date, duration, strategy_option=1, backtest_option=1, take_profit=2, cut_loss=1, long_duration=0, long_duration_period=20
    _1_backtest_comparison = "T1_"+backtest_comparison
    N_backtest_comparison = "TN_"+backtest_comparison

    if (backtest_option == 0):
        if list_backtest_result:
            df_main_result = (pd.DataFrame(list_backtest_result)).T
            df_main_result.columns = ['Stock', 'T0_Date', 'T0_Close']
            df_main_result.sort_values(by='Stock', inplace=True, ascending=True)
            df_main_result.round({'T0_Close': 3})

            df_main_result.to_csv(os.path.join(CONST_RESULT_NOT_BACKTESTED, "START_"+str(beginning_date)+'_Strategy-'+strategies_backtest['Strategy'][strategy_option]+'_'+str(long_duration_period)+'_days_'+format_date_time+'.csv'))
            print(df_main_result)
        else:
            print("No result is found!")

    elif (backtest_option == 1):
        if list_backtest_result:
            df_main_backtest_result = (pd.DataFrame(list_backtest_result)).T
            df_main_backtest_result.columns = ['Stock', 'T0_Date', 'T0_Close', 'Action', 'T1_Date', _1_backtest_comparison]
            df_main_backtest_result.sort_values(by=['T0_Date','Stock'], inplace=True, ascending=True)
            df_main_backtest_result.reset_index(drop=True, inplace=True)
            df_main_backtest_result['Change'], df_main_backtest_result['Change(%)'] = (df_main_backtest_result[_1_backtest_comparison] - df_main_backtest_result['T0_Close']), ((df_main_backtest_result[_1_backtest_comparison] - df_main_backtest_result['T0_Close'])/df_main_backtest_result['T0_Close'] * 100)
            df_main_backtest_result['Result'] = (((df_main_backtest_result['Change(%)'] > 0) & (df_main_backtest_result['Action'] == 'SELL')) | (df_main_backtest_result['Action'] == 'TP'))*1
            # total_tp = df_main_backtest_result[(df_main_backtest_result['Action'] == 'TP')].shape[0]
            # total_cl = df_main_backtest_result[(df_main_backtest_result['Action'] == 'CL')].shape[0]
            # total_sell = df_main_backtest_result[(df_main_backtest_result['Action'] == 'SELL')].shape[0]
            # total_win = df_main_backtest_result[(df_main_backtest_result['Result'] > 0)].shape[0]
            # total_loss = len(df_main_backtest_result.index) - total_win
            # total_stock = len(df_main_backtest_result.index)
            # print("Total TP", total_tp)
            # print("Total CL", total_cl)
            # print("Total SELL", total_sell)
            # print("Total Win", total_win)
            # print("Total Loss", total_loss)
            # print("Total Stock", total_stock)

            # list_total_result = []
            # list_total_result += [['', '', '', '', '', '', '', 'Total TP', total_tp]]
            # list_total_result += [['', '', '', '', '', '', '', 'Total CL', total_cl]]
            # list_total_result += [['', '', '', '', '', '', '', 'Total SELL', total_sell]]
            # list_total_result += [['', '', '', '', '', '', '', 'Total Win', total_win]]
            # list_total_result += [['', '', '', '', '', '', '', 'Total Loss', total_loss]]
            # list_total_result += [['', '', '', '', '', '', '', 'Total Stock', total_stock]]
            # df_main_backtest_result = df_main_backtest_result.append(pd.DataFrame(list_total_result, columns=df_main_backtest_result.columns.tolist()), ignore_index=True)
            # print(df_main_backtest_result)
        else:
            print("No result is found!")

    elif (backtest_option == 2):
        if list_backtest_result:
            df_main_backtest_result = (pd.DataFrame(list_backtest_result)).T
            df_main_backtest_result.columns = ['Stock', 'T0_Date', 'T0_Close', 'Action', 'TN_Date', N_backtest_comparison]
            df_main_backtest_result.sort_values(by=['T0_Date','Stock'], inplace=True, ascending=True)
            df_main_backtest_result.reset_index(drop=True, inplace=True)
            df_main_backtest_result['Change'], df_main_backtest_result['Change(%)'] = (df_main_backtest_result[N_backtest_comparison] - df_main_backtest_result['T0_Close']), ((df_main_backtest_result[N_backtest_comparison] - df_main_backtest_result['T0_Close'])/df_main_backtest_result['T0_Close'] * 100)
            df_main_backtest_result['Result'] = (((df_main_backtest_result['Change(%)'] > 0) & (df_main_backtest_result['Action'] == 'SELL')) | (df_main_backtest_result['Action'] == 'TP'))*1

        else:
            print("No result is found!")
    
    elif (backtest_option == 3):
        if list_backtest_result:
            df_main_backtest_result = (pd.DataFrame(list_backtest_result)).T
            df_main_backtest_result.columns = ['Stock', 'T0_Date', 'T0_Close', 'Action', 'TN_Date', N_backtest_comparison]
            df_main_backtest_result.sort_values(by=['T0_Date','Stock'], inplace=True, ascending=True)
            df_main_backtest_result.reset_index(drop=True, inplace=True)
            df_main_backtest_result['Change'], df_main_backtest_result['Change(%)'] = (df_main_backtest_result[N_backtest_comparison] - df_main_backtest_result['T0_Close']), ((df_main_backtest_result[N_backtest_comparison] - df_main_backtest_result['T0_Close'])/df_main_backtest_result['T0_Close'] * 100)
            df_main_backtest_result['Result'] = (((df_main_backtest_result['Change(%)'] > 0) & (df_main_backtest_result['Action'] == 'SELL')) | (df_main_backtest_result['Action'] == 'TP'))*1

        else:
            print("No result is found!")

    if (len(df_main_backtest_result) != 0):

        df_main_backtest_result.round({'T0_Close': 3, _1_backtest_comparison: 3, N_backtest_comparison: 3, 'Change':3, 'Change(%)':2})
        total_tp = df_main_backtest_result[(df_main_backtest_result['Action'] == 'TP')].shape[0]
        total_cl = df_main_backtest_result[(df_main_backtest_result['Action'] == 'CL')].shape[0]
        total_sell = df_main_backtest_result[(df_main_backtest_result['Action'] == 'SELL')].shape[0]
        total_win = df_main_backtest_result[(df_main_backtest_result['Result'] > 0)].shape[0]
        total_loss = len(df_main_backtest_result.index) - total_win
        total_stock = len(df_main_backtest_result.index)
        print("Total TP", total_tp)
        print("Total CL", total_cl)
        print("Total SELL", total_sell)
        print("Total Win", total_win)
        print("Total Loss", total_loss)
        print("Total Stock", total_stock)

        list_total_result = []
        list_total_result += [['', '', '', '', '', '', '', 'Total TP', total_tp]]
        list_total_result += [['', '', '', '', '', '', '', 'Total CL', total_cl]]
        list_total_result += [['', '', '', '', '', '', '', 'Total SELL', total_sell]]
        list_total_result += [['', '', '', '', '', '', '', 'Total Win', total_win]]
        list_total_result += [['', '', '', '', '', '', '', 'Total Loss', total_loss]]
        list_total_result += [['', '', '', '', '', '', '', 'Total Stock', total_stock]]
        df_main_backtest_result = df_main_backtest_result.append(pd.DataFrame(list_total_result, columns=df_main_backtest_result.columns.tolist()), ignore_index=True)

        df_main_backtest_result.to_csv(os.path.join(CONST_RESULT_BACKTESTED, "START_"+str(beginning_date)+'_Strategy-'+strategies_backtest['Strategy'][strategy_option]+'_'+str(long_duration_period)+'_days'+'_Backtest-'+strategies_backtest['Backtest'][backtest_option]+'_'+str(duration)+'_days_'+format_date_time+'.csv'))
        print(df_main_backtest_result)

    print("END")


if __name__ == '__main__':
    
    testdatefullstring = ""
    long_duration = 0
    long_duration_period = 0
    duration = 0
    strategy_option = 0
    backtest_option = 0
    take_profit = 0
    cut_loss = 0

    backtest_comparison = {
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
    }

    strategies_backtest = {
        "Strategy": {
            1: "Power of Average",
            2: "Mid Swing",
            3: "3M + Stochastic RSI",
            4: "EMA 7 cross atas EMA 21 + Stochastic RSI",
        },
        "Backtest": {
            0: "",
            1: "Buy Today Sell Tomorrow",
            2: "Max Swing Profit",
            3: "Trading Plan",
        }
    }

    # testdatefullstring = input("Please enter the date you want to test (YYYY-MM-DD): ")
    # duration = int(input("Please enter the duration you want to backtest in days as unit: "))
    # while True:
    #     print("Strategy Option: \n",
    #             "1. Power of Average \n", 
    #             "2. Mid Swing \n",
    #             "3. 3M + Stochastic RSI \n",
    #             "4. EMA 7 cross atas EMA 21 + Stochastic RSI \n")
    #     strategy_option = input("Please key in your strategy: ")
    #     if (int(strategy_option) <= 0) | (np.isnan(int(strategy_option))):
    #         print("Please enter the right strategy\n")
    #     else:
    #         break


    # perform_backtest = input("Do you also want to perform backtest for this strategy?(Type: Y/N or YES/NO): ")
    # if (perform_backtest.lower() in "yes"):
    #     while True:
    #         print("Backtest Option: \n",
    #             "1. BTST \n", 
    #             "2. Max Swing \n",
    #             "3. Trading Plan \n")
    #         backtest_option = input("Please key in your backtest: ")
    #         if (int(backtest_option) <= 0) | (np.isnan(int(backtest_option))):
    #             print("Please enter the right strategy\n")
    #         else:
    #             if (backtest_option == 1):
    #                 proceed = input("By default this backtest duration is one, proceed?(Type: Y/N or YES/NO): ")
    #                 if (proceed.lower() in "yes"):
    #                     duration = 1
    #                 else:
    #                     continue
    #             elif int(backtest_option) == 3:
    #                 take_profit = int(input("Please Key in TP: "))
    #                 cut_loss = int(input("Please Key in CL: "))
    #             break
    # else:
    #     backtest_option = 0


    # perform_long_duration = input("By default this is a one day strategy-process. Proceed?(Type: Y/N or YES/NO): ")
    # if (perform_long_duration.lower() in "yes"):
    #     long_duration = 0
    # else:
    #     long_duration = 1
    #     while True:
    #         long_duration_period = input("Please enter the duration of your strategy-process: ")
    #         if (int(long_duration_period) <= 0) | (np.isnan(int(long_duration_period))):
    #             print("Please enter the right duration\n")
    #         else:
    #             break


    # backtest_comparison = input("What do you want to compare with?(Type: O/H/L/C or open/high/low/close): ")
    # if ((backtest_comparison.lower() == 'o') | (backtest_comparison.lower() == 'open')):
    #     backtest_comparison = "Open"
    # elif ((backtest_comparison.lower() == 'h') | (backtest_comparison.lower() == 'high')):
    #     backtest_comparison = "High"
    # elif ((backtest_comparison.lower() == 'l') | (backtest_comparison.lower() == 'low')):
    #     backtest_comparison = "Low"
    # elif ((backtest_comparison.lower() == 'c') | (backtest_comparison.lower() == 'close')):
    #     backtest_comparison = "Close"
    # else:
    #     backtest_comparison = "Close"


    # weekmask starts with an array of Mon to Sun
    number_of_days = np.busday_count('2020-11-01','2020-11-30', weekmask=[1,1,1,1,1,0,0], holidays=['2020-11-14'])
    print(number_of_days)

    list_strategy_option = [1, 2, 3, 4]
    list_backtest_option = [1, 2, 3]
    list_backtest_comparison = ['Close', 'Open']

    for _b_comparison in backtest_comparison:
        backtest_comparison = _b_comparison
        for _s_option in list_strategy_option:
            strategy_option = _s_option
            for _b_option in list_backtest_option:
                backtest_option = _b_option
                
                testdatefullstring = "2020-11-02"
                # backtest_comparison = "Close"
                # strategy_option = 1
                # backtest_option = 3
                duration = 10
                long_duration = 1
                long_duration_period = 21

                if not long_duration:
                    long_duration_period = 1

                if (backtest_option == 1):
                    duration = 1
                elif (backtest_option == 3):
                    take_profit = 10
                    cut_loss = 5


                main(testdatefullstring, int(duration), int(strategy_option), int(backtest_option), int(take_profit), int(cut_loss), int(long_duration), int(long_duration_period), backtest_comparison, strategies_backtest)


    # testdatefullstring = "2020-11-02"
    # backtest_comparison = "Close"
    # strategy_option = 1
    # backtest_option = 3
    # duration = 10
    # long_duration = 1
    # long_duration_period = 20

    # if not long_duration:
    #     long_duration_period = 1

    # if (backtest_option == 1):
    #     duration = 1
    # elif (backtest_option == 3):
    #     take_profit = 10
    #     cut_loss = 5


    # main(testdatefullstring, int(duration), int(strategy_option), int(backtest_option), int(take_profit), int(cut_loss), int(long_duration), int(long_duration_period), backtest_comparison, strategies_backtest)
    
