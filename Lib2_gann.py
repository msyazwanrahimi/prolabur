import pandas as pd
import numpy as np

def cents_to_RM(cents):
    ringgit = '{0:.02f}'.format(float(cents) / 100.0)

    return ringgit

def RM_to_cents(ringgit):

    cents = int(ringgit * 100)

    return cents

def find_nearest(array, value):

    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    if array[idx] < value :
        return array[idx - 2], array[idx - 1], array[idx], array[idx + 1], array[idx + 2], array[idx + 3]

    else:
        return array[idx - 3], array[idx - 2], array[idx - 1], array[idx], array[idx + 1], array[idx + 2]

def gann_generate(price):

    price = RM_to_cents(price)

    gl = []
    i = 1

    for item in range(1,18):
        i = i + 2
        #print(i)
        j = i * i
        #print(j)
        gl.append(j)

        n = 0.25

        for item in range(1,8):

            r = int((i + n) * (i + n)) + 1
            n = n + 0.25
            #print(r)
            gl.append(r)

    s3,s2,s1,r1,r2,r3 = find_nearest(gl, price)
    print("Gann Square of 9 Support and Resistance")
    print("The latest price %i cents" %price)
    print ("S3=%i S2=%i S1=%i R1=%i R2=%i R3=%i" %(s3,s2,s1,r1,r2,r3))

    data1 = np.arange(14,1226)

    df = pd.DataFrame(data1)
    df.columns = ['Price']

    s_3 = []
    s_2 = []
    s_1 = []
    r_1 = []
    r_2 = []
    r_3 = []

    print(price)
    s3, s2, s1, r1, r2, r3 = find_nearest(gl, price)
    s_3.append(cents_to_RM(int(s3)))
    s_2.append(cents_to_RM(int(s2)))
    s_1.append(cents_to_RM(int(s1)))
    r_1.append(cents_to_RM(int(r1)))
    r_2.append(cents_to_RM(int(r2)))
    r_3.append(cents_to_RM(int(r3)))

    return cents_to_RM(int(s3)), cents_to_RM(int(s2)), cents_to_RM(int(s1)), cents_to_RM(int(r1)), cents_to_RM(int(r2)), cents_to_RM(int(r3))

def priceMovement(test_date_price, list_price, list_date):
            duration = len(list_price)
            list_test_date_price = [test_date_price] * duration
            

            df_processing = pd.DataFrame(list(zip(list_date, list_test_date_price, list_price)), columns= ['Date', 'NClose', 'N-1Close'])
            priceMovement = []

            print(df_processing['NClose'][1])
            for x in range(len(list_price)):
                if(x>=1):
                    s3, s2, s1, r1, r2, r3 = gann_generate(list_price[x-1])
                else:
                    s3, s2, s1, r1, r2, r3 = gann_generate(list_price[x])
                
                if(float(df_processing['NClose'][x]<float(df_processing['N-1Close'][x]))):
                    print("Price risen")
                    if(float(df_processing['N-1Close'][x]>float(r1))):
                        print("breakout one resistance")
                        priceMovement.append(2)
                    elif(float(df_processing['N-1Close'][x]>float(r2))):
                        print("breakout two resistance")
                        priceMovement.append(3)
                    elif(float(df_processing['N-1Close'][x]>float(r3))):
                        print("breakout three resistance")
                        priceMovement.append(4)
                    else:
                        print("Price Risen but not breakout")
                        priceMovement.append(1)
                elif(float(df_processing['NClose'][x]>float(df_processing['N-1Close'][x]))):

                    print("Price Drop")
                    if(float(df_processing['N-1Close'][x]<float(s1))):
                        print("support one resistance")
                        priceMovement.append(-2)
                    elif(float(df_processing['N-1Close'][x]<float(s2))):
                        print("support two resistance")
                        priceMovement.append(-3)
                    elif(float(df_processing['N-1Close'][x]<float(s3))):
                        print("support three resistance")
                        priceMovement.append(-4)
                    else:
                        print("Price Drop but not breakout")
                        priceMovement.append(-1)
                elif(float(df_processing['NClose'][x]==float(df_processing['N-1Close'][x]))):
                    print("price not change")
                    priceMovement.append(0)
            max_profit = max(df_processing['N-1Close'])
            max_profit_index_positive = df_processing[df_processing['N-1Close'] == max_profit].index.tolist()[0]
            total_row = len(df_processing.index)
            max_profit_index = -abs(total_row - max_profit_index_positive)

            return priceMovement
