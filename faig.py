#IF YOU FOUND THIS USEFUL, Please Donate some Bitcoin .... 1FWt366i5PdrxCC6ydyhD8iywUHQ2C7BWC

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
import requests
import json
import logging
import sys
import urllib
from time import time, sleep
import random
import time as systime
from statistics import mean, median
import numpy as np
#Scikit's LinearRegression model
from sklearn.linear_model import LinearRegression
##################################################
import sys, os

########################################################################################################################
REAL_OR_NO_REAL = 'https://demo-api.ig.com/gateway/deal'
API_ENDPOINT = "https://demo-api.ig.com/gateway/deal/session"
API_KEY = '***' #<-------------Special IG Index API Key, Problem on 23rd Jan
#API_KEY = '***'
data = {"identifier":"***","password": "***"}
########################################################################################################################
########################################################################################################################
########################################################################################################################
# FOR REAL....
########################################################################################################################
########################################################################################################################
########################################################################################################################
# REAL_OR_NO_REAL = 'https://api.ig.com/gateway/deal'
# API_ENDPOINT = "https://api.ig.com/gateway/deal/session"
# API_KEY = '***'
# data = {"identifier":"***","password": "***"}

headers = {'Content-Type':'application/json; charset=utf-8',
        'Accept':'application/json; charset=utf-8',
        'X-IG-API-KEY':API_KEY,
        'Version':'2'
        }

r = requests.post(API_ENDPOINT, data=json.dumps(data), headers=headers)
 
headers_json = dict(r.headers)
CST_token = headers_json["CST"]
print (R"CST : " + CST_token)
x_sec_token = headers_json["X-SECURITY-TOKEN"]
print (R"X-SECURITY-TOKEN : " + x_sec_token)

#GET ACCOUNTS
base_url = REAL_OR_NO_REAL + '/accounts'
authenticated_headers = {'Content-Type':'application/json; charset=utf-8',
        'Accept':'application/json; charset=utf-8',
        'X-IG-API-KEY':API_KEY,
        'CST':CST_token,
        'X-SECURITY-TOKEN':x_sec_token}

auth_r = requests.get(base_url, headers=authenticated_headers)
d = json.loads(auth_r.text)

# print(auth_r.status_code)
# print(auth_r.reason)
# print (auth_r.text)

for i in d['accounts']:
    if str(i['accountType']) == "SPREADBET":
        print ("Spreadbet Account ID is : " + str(i['accountId']))
        spreadbet_acc_id = str(i['accountId'])

#SET SPREAD BET ACCOUNT AS DEFAULT
base_url = REAL_OR_NO_REAL + '/session'
data = {"accountId":spreadbet_acc_id,"defaultAccount": "True"}
auth_r = requests.put(base_url, data=json.dumps(data), headers=authenticated_headers)

# print(auth_r.status_code)
# print(auth_r.reason)
# print (auth_r.text)
#ERROR about account ID been the same, Ignore! 

###################################################################################
##########################END OF LOGIN CODE########################################
##########################END OF LOGIN CODE########################################
##########################END OF LOGIN CODE########################################
##########################END OF LOGIN CODE########################################
###################################################################################

# PROGRAMMABLE VALUES
# UNIT TEST FOR CRYPTO'S
# limitDistance_value = "1"
# orderType_value = "MARKET"
# size_value = "5"
# expiry_value = "DFB"
# guaranteedStop_value = True
# currencyCode_value = "GBP"
# forceOpen_value = True
# stopDistance_value = "150"

#UNIT TEST FOR OTHER STUFF
limitDistance_value = "4" #Initial Limit (Take Profit), Worked out later per trade
orderType_value = "MARKET"
size_value = "1"
expiry_value = "DFB"
guaranteedStop_value = True
currencyCode_value = "GBP"
forceOpen_value = True
stopDistance_value = "250" #Initial Stop loss, Worked out later per trade

#HACKY/Weekend Testing - DO NOT USE!!! UNLESS YOU KNOW WHAT YOU ARE DOING!!
#HACKY/Weekend Testing - DO NOT USE!!! UNLESS YOU KNOW WHAT YOU ARE DOING!!
#epic_id = "CS.D.BITCOIN.TODAY.IP" #Bitcoin
#epic_id = "IX.D.SUNFUN.DAILY.IP" #Weekend Trading
#epic_id = "CS.D.ETHUSD.TODAY.IP" #Ether
#epic_id = "CS.D.BCHUSD.TODAY.IP" #Bitcoin Cash
#HACKY/Weekend Testing - DO NOT USE!!! UNLESS YOU KNOW WHAT YOU ARE DOING!!
#HACKY/Weekend Testing - DO NOT USE!!! UNLESS YOU KNOW WHAT YOU ARE DOING!!

#LIVE TEST
#epic_id = "CS.D.USCGC.TODAY.IP" #Gold - OK, Not Great
#epic_id = "CS.D.USCSI.TODAY.IP" #Silver - NOT RECOMMENDED 

#ALL EPICS
#ALL EPICS
#ALL EPICS
#ALL EPICS
epic_ids = ["CS.D.AUDUSD.TODAY.IP", "CS.D.EURCHF.TODAY.IP", "CS.D.EURGBP.TODAY.IP", "CS.D.EURJPY.TODAY.IP", "CS.D.EURUSD.TODAY.IP", "CS.D.GBPEUR.TODAY.IP", "CS.D.GBPUSD.TODAY.IP", "CS.D.USDCAD.TODAY.IP", "CS.D.USDCHF.TODAY.IP", "CS.D.USDJPY.TODAY.IP", "CS.D.CADCHF.TODAY.IP", "CS.D.CADJPY.TODAY.IP", "CS.D.CHFJPY.TODAY.IP", "CS.D.EURCAD.TODAY.IP", "CS.D.EURSGD.TODAY.IP", "CS.D.EURZAR.TODAY.IP", "CS.D.GBPCAD.TODAY.IP", "CS.D.GBPCHF.TODAY.IP", "CS.D.GBPJPY.TODAY.IP", "CS.D.GBPSGD.TODAY.IP", "CS.D.GBPZAR.TODAY.IP", "CS.D.MXNJPY.TODAY.IP", "CS.D.NOKJPY.TODAY.IP", "CS.D.PLNJPY.TODAY.IP", "CS.D.SEKJPY.TODAY.IP", "CS.D.SGDJPY.TODAY.IP", "CS.D.USDSGD.TODAY.IP", "CS.D.USDZAR.TODAY.IP", "CS.D.AUDCAD.TODAY.IP", "CS.D.AUDCHF.TODAY.IP", "CS.D.AUDEUR.TODAY.IP", "CS.D.AUDGBP.TODAY.IP", "CS.D.AUDJPY.TODAY.IP", "CS.D.AUDNZD.TODAY.IP", "CS.D.AUDSGD.TODAY.IP", "CS.D.EURAUD.TODAY.IP", "CS.D.EURNZD.TODAY.IP", "CS.D.GBPAUD.TODAY.IP", "CS.D.GBPNZD.TODAY.IP", "CS.D.NZDAUD.TODAY.IP", "CS.D.NZDCAD.TODAY.IP", "CS.D.NZDCHF.TODAY.IP", "CS.D.NZDEUR.TODAY.IP", "CS.D.NZDGBP.TODAY.IP", "CS.D.NZDJPY.TODAY.IP", "CS.D.NZDUSD.TODAY.IP", "CS.D.CHFHUF.TODAY.IP", "CS.D.EURCZK.TODAY.IP", "CS.D.EURHUF.TODAY.IP", "CS.D.EURILS.TODAY.IP", "CS.D.EURMXN.TODAY.IP", "CS.D.EURPLN.TODAY.IP", "CS.D.EURTRY.TODAY.IP", "CS.D.GBPCZK.TODAY.IP", "CS.D.GBPHUF.TODAY.IP", "CS.D.GBPILS.TODAY.IP", "CS.D.GBPMXN.TODAY.IP", "CS.D.GBPPLN.TODAY.IP", "CS.D.GBPTRY.TODAY.IP", "CS.D.TRYJPY.TODAY.IP", "CS.D.USDCZK.TODAY.IP", "CS.D.USDHUF.TODAY.IP", "CS.D.USDILS.TODAY.IP", "CS.D.USDMXN.TODAY.IP", "CS.D.USDPLN.TODAY.IP", "CS.D.USDTRY.TODAY.IP", "CS.D.CADNOK.TODAY.IP", "CS.D.CHFNOK.TODAY.IP", "CS.D.EURDKK.TODAY.IP", "CS.D.EURNOK.TODAY.IP", "CS.D.EURSEK.TODAY.IP", "CS.D.GBPDKK.TODAY.IP", "CS.D.GBPNOK.TODAY.IP", "CS.D.GBPSEK.TODAY.IP", "CS.D.NOKSEK.TODAY.IP", "CS.D.USDDKK.TODAY.IP", "CS.D.USDNOK.TODAY.IP", "CS.D.USDSEK.TODAY.IP", "CS.D.AUDCNH.TODAY.IP", "CS.D.CADCNH.TODAY.IP", "CS.D.CNHJPY.TODAY.IP", "CS.D.BRLJPY.TODAY.IP", "CS.D.GBPINR.TODAY.IP", "CS.D.USDBRL.TODAY.IP", "CS.D.USDIDR.TODAY.IP", "CS.D.USDINR.TODAY.IP", "CS.D.USDKRW.TODAY.IP", "CS.D.USDMYR.TODAY.IP", "CS.D.USDPHP.TODAY.IP", "CS.D.USDTWD.TODAY.IP", "CS.D.EURCNH.TODAY.IP", "CS.D.sp_EURRUB.TODAY.IP", "CS.D.GBPCNH.TODAY.IP", "CS.D.NZDCNH.TODAY.IP", "CS.D.USDCNH.TODAY.IP", "CS.D.sp_USDRUB.TODAY.IP"]
#ALL EPICS
#ALL EPICS
#ALL EPICS
##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
#SENSIBLE EPIC LIST, This is just the Major FX from IG Index Web Portal
#SENSIBLE EPIC LIST
#SENSIBLE EPIC LIST
#SENSIBLE EPIC LIST
#epic_ids = ["CS.D.GBPUSD.TODAY.IP","CS.D.EURUSD.TODAY.IP","CS.D.USDJPY.TODAY.IP","CS.D.AUDUSD.TODAY.IP","CS.D.EURGBP.TODAY.IP","CS.D.EURJPY.TODAY.IP", "CS.D.USDCAD.TODAY.IP","CS.D.GBPEUR.TODAY.IP", "CS.D.USDCHF.TODAY.IP","CS.D.EURCHF.TODAY.IP"]
#SENSIBLE EPIC LIST
#SENSIBLE EPIC LIST
#SENSIBLE EPIC LIST

#*******************************************************************
#*******************************************************************
#*******************************************************************
#*******************************************************************

TIME_WAIT_MULTIPLIER = 60
#STOP_LOSS_MULTIPLIER = 4 #Not currently in use, 13th Jan
predict_accuracy = 0.89
profitable_trade_count = 0
print ("START TIME : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))

def exponential_average(values, window):
    weights = np.exp(np.linspace(-1.,0.,window))
    weights /= weights.sum()

    a = np.convolve(values, weights) [:len(values)]
    a[:window]=a[window]
    return a

def ExpMovingAverage(values, window):
    """ Numpy implementation of EMA
    """
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a   

def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)   
    
previous_traded_epic_id = "None"
Tight_Spread = False

for times_round_loop in range(1, 9999):

#*******************************************************************
#*******************************************************************
#*******************************************************************
#*******************************************************************
    DO_A_THING = False
    Price_Change_OK = False
    Tight_Spread = False
    Start_loop_time = time()
    price_compare = "bid"
    Price_Change_Day_percent = 0
    low_price_list = []
    high_price_list = []
    close_price_list = []
    volume_list = []
    # Your input data, X and Y are lists (or Numpy Arrays)
    #THIS IS YOUR TRAINING DATA
    x = [] #This is Low Price, Volume
    y = [] #This is High Price
    
 
    while not Price_Change_OK:
    #If "big" percent increase, I'm not interested today. Thanks
        random.shuffle(epic_ids)
        epic_id = random.choice(epic_ids)
        print ("-----------------------------------------")
        print("!!DEBUG : Random epic_id is : " + str(epic_id))
        base_url = REAL_OR_NO_REAL + '/markets/' + epic_id
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)

        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")

        MARKET_ID = d['instrument']['marketId']
        current_price = d['snapshot']['bid']
        Price_Change_Day = d['snapshot']['netChange']
        Price_Change_Day_percent = d['snapshot']['percentageChange'] 
        #Bit o' movement .... Not alot!
        #Bit o' movement .... Not alot!
        if Price_Change_Day_percent < 0.45 and Price_Change_Day_percent > -0.45:
        #if Price_Change_Day_percent > 0.20 and Price_Change_Day_percent < -0.20:
            print ("Price Change Percentage on day is " + str(Price_Change_Day_percent))
            Price_Change_OK = True
            
        bid_price = d['snapshot']['bid']
        ask_price = d['snapshot']['offer']
        spread = float(bid_price) - float(ask_price)
        # print ("bid : " + str(bid_price))
        # print ("ask : " + str(ask_price))
        # print ("-------------------------")
        print ("spread : " + str(spread))
        ##################################################################################################################
        ##################################################################################################################
        #e.g Spread is -30, That is too big, In-fact way too big. Spread is -1.7, This is not too bad, We can trade on this reasonably well.
        #Spread is 0.8. This is considered a tight spread, Set the limit as 1 as it bounces around too much (Quick in and out trade). 
        ##################################################################################################################
        ##################################################################################################################
        #if spread is less than -2, It's too big
        if float(spread) < -2:
         print ("!!DEBUG!! :- SPREAD NOT OK")
         Price_Change_OK = False
         systime.sleep(2)
        elif float(spread) > -2:
         Price_Change_OK = True
        #If spread is better than -2 i.e 1.9,1.8 etc etc etc    
        if float(spread) > -1:
            print ("-------------------------")
            print ("!!DEBUG!! :- !!!WARNING!!! Tight Spread Detected")
            Tight_Spread = True
            
        #Don't Trade on the same epic twice in a row
        if previous_traded_epic_id == epic_id:
            Price_Change_OK = False
            print ("!!DEBUG!! : Don't Trade on the same epic twice in a row")
        
 
    while not DO_A_THING:
        print ("!!Internal Notes only - Top of Loop!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/DAY/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
        day_moving_avg_30 = []
        
     
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            open_price = i['openPrice'][price_compare]
            close_price = i['closePrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
            price_change_on_day = close_price - open_price
            #print ("DEBUG price_change_day : " + str(price_change_on_day))
            day_moving_avg_30.append(float(price_change_on_day))
            
        avg_price_movement_day = np.mean(day_moving_avg_30)
        # print ("-----------------DEBUG-----------------")
        # print ("DEBUG average movement over last 30 days : " + str(avg_price_movement_day)) 
        # print ("-----------------DEBUG-----------------")
        
        ############################################################
        ############################################################
        ############################################################
        ############################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/HOUR_4/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
            
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/HOUR_3/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
      
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
            
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/HOUR_2/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
     
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
        

        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/HOUR/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
        
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
        
        #Cut down on API Calls by using this again! 
        
        price_ranges = []
        closing_prices = []
        first_time_round_loop = True
        TR_prices = []


        for i in d['prices']:
            if first_time_round_loop == True:
                #First time round loop cannot get previous
                closePrice = i['closePrice'][price_compare]
                closing_prices.append(closePrice)
                high_price = i['highPrice'][price_compare]
                low_price = i['lowPrice'][price_compare]
                price_range = float(high_price - closePrice)
                price_ranges.append(price_range)
                first_time_round_loop = False
            else:
                prev_close = closing_prices[-1]
                ###############################
                closePrice = i['closePrice'][price_compare]
                closing_prices.append(closePrice)
                high_price = i['highPrice'][price_compare]
                low_price = i['lowPrice'][price_compare]
                price_range = float(high_price - closePrice)
                price_ranges.append(price_range)
                TR = max(high_price-low_price, abs(high_price-prev_close), abs(low_price-prev_close))
                #print (TR)
                TR_prices.append(TR)
                
             
        max_range = max(TR_prices)
        low_range = min(TR_prices)
        print ("stopDistance_value for " + str(epic_id) + " will bet set at " + str(int(max_range)))
        print ("limitDistance_value for " + str(epic_id) + " will bet set at " + str(int(low_range)))
        if low_range > 10:
            print ("!!DEBUG!! WARNING - Take Profit over high value, Might take a while for this trade!!")
            
        #print ("MAX RANGE FOR " + str(epic_id) + " IS " + str(int(max_range)))
        #print ("LOW RANGE FOR " + str(epic_id) + " IS " + str(int(low_range)))
        #Cut down on API Calls by using this again! 
       
        
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/MINUTE_30/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
  

        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices

        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/MINUTE_15/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
    
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
        
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/MINUTE_10/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
     
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
        
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/MINUTE_5/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
        
        

        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices

        
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/MINUTE_3/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
        
        

        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
        
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/MINUTE_2/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
  
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
            
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/MINUTE/30'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
    
        for i in d['prices']:
            tmp_list = []
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
            #---------------------------------
            tmp_list.append(float(low_price))
            tmp_list.append(float(volume))
            x.append(tmp_list)
            #x is Low Price and Volume
            y.append(float(high_price))
            #y = High Prices
            
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        
        
     
        base_url = REAL_OR_NO_REAL + '/prices/'+ epic_id + '/DAY/1'
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)
        
        #I only need this API call for real world values
        remaining_allowance = d['allowance']['remainingAllowance']
        reset_time = humanize_time(int(d['allowance']['allowanceExpiry']))
        total_allowance = humanize_time(int(d['allowance']['totalAllowance']))
                
        print ("-----------------DEBUG-----------------")
        print ("Remaining API Calls left : " + str(remaining_allowance))
        print ("Time to API Key reset : " + str(reset_time))
        print ("-----------------DEBUG-----------------")
   
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")

        for i in d['prices']:
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']
        
        # print ("DEBUG : avg_price_movement_day : " + str(avg_price_movement_day))
        # print ("DEBUG : Price_Change_Day : " + str(Price_Change_Day))
        
        # if float(avg_price_movement_day) < float(Price_Change_Day):
            # break
            
        #####################################################################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #####################################################################
        
        x = np.asarray(x)
        y = np.asarray(y)
        # Initialize the model then train it on the data
        genius_regression_model = LinearRegression()
        genius_regression_model.fit(x,y)
        # Predict the corresponding value of Y for X
        pred_ict = [low_price,volume]
        pred_ict = np.asarray(pred_ict) #To Numpy Array, hacky but good!! 
        pred_ict = pred_ict.reshape(1, -1)
        price_prediction = genius_regression_model.predict(pred_ict)
        print ("PRICE PREDICTION FOR PRICE " + epic_id + " IS : " + str(price_prediction))


        score = genius_regression_model.score(x,y)
        predictions = {'intercept': genius_regression_model.intercept_, 'coefficient': genius_regression_model.coef_,   'predicted_value': price_prediction, 'accuracy' : score}
        # print ("-----------------DEBUG-----------------")
        # print (score)
        # print (predictions)
        # print ("-----------------DEBUG-----------------")
        
        # print ("!!DEBUG TIME!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
               
        #####################################################################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #########################PREDICTION CODE#############################
        #####################################################################
        #DO WE NEED THIS API CALL???? TODO :- REMOVE
        #base_url = REAL_OR_NO_REAL + '/markets/' + epic_id
        #auth_r = requests.get(base_url, headers=authenticated_headers)
        #d = json.loads(auth_r.text)
        # print ("-----------------DEBUG-----------------")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print (auth_r.text)
        # print ("-----------------DEBUG-----------------")
            
        price_diff = current_price - price_prediction
        limitDistance_value = int(low_range)
        #Fixing a weird bug with some exotic fx, Where the prediction is 0. 
        if limitDistance_value == 0:
            limitDistance_value = "1"
            
        #stopDistance_value = int(max_range) 
        #NOTE Sometimes IG Index want a massive stop loss for Guaranteed, Either don't use Guaranteed or "sell at market" with Artificial Stop loss
        #MUST NOTE :- IF THIS PRICE IS - i.e NOT HIT TARGET YET, CONVERSELY IF THIS PRICE IS POSITIVE IT IS ALREADY ABOVE PREDICTION!!!
        
        print ("TRUE GUARANTEED STOP LOSS DISTANCE WILL BE SET AT : " + str(stopDistance_value))
        print ("Price Difference Away (Point's) : " + str(price_diff))
        #Price_diff should be minus if we are buying towards
        if float(price_diff) > float(limitDistance_value):
            print ("-----------------DEBUG-----------------")
            print ("-----------------DEBUG-----------------")
            print ("WARNING :- PRICE ALREADY OVER TARGET")
            print ("-----------------DEBUG-----------------")
            print ("-----------------DEBUG-----------------")
            
        ################################################################
        #########################ORDER CODE#############################
        #########################ORDER CODE#############################
        #########################ORDER CODE#############################
        #########################ORDER CODE#############################
        ################################################################
        
        ################################################################
        #############Predict Accuracy isn't that great. ################
        #############Predict Accuracy isn't that great. ################
        #############Predict Accuracy isn't that great. ################
        #############Predict Accuracy isn't that great. ################
        ################################################################
        Prediction_Wait_Timer = int(TIME_WAIT_MULTIPLIER) #Wait
        print ("!!DEBUG TIME!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
        if price_diff < 0 and score < predict_accuracy: 
                DO_A_THING = False
                print ("!!DEBUG TIME!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                systime.sleep(Prediction_Wait_Timer)
                print ("!!DEBUG TIME!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                break
        elif price_diff > 0 and score < predict_accuracy:
                DO_A_THING = False
                print ("!!DEBUG TIME!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                systime.sleep(Prediction_Wait_Timer)
                print ("!!DEBUG TIME!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                break
        
        
        if profitable_trade_count < 6:
            if price_diff < 0 and score > predict_accuracy:
                DIRECTION_TO_TRADE = "BUY"
                DIRECTION_TO_CLOSE = "SELL"
                DIRECTION_TO_COMPARE = 'bid'
                DO_A_THING = True
            elif price_diff > 0 and score > predict_accuracy:
                #It's OVER the predicted price, Keep going but keep it tight?? Tight limit!! Take small profits
                limitDistance_value = "2"
                DIRECTION_TO_TRADE = "SELL"
                DIRECTION_TO_CLOSE = "BUY"
                DIRECTION_TO_COMPARE = 'offer'
                DO_A_THING = True
        elif profitable_trade_count >= 6: #6, Trades ... profit. Right??? 
            profitable_trade_count = 0
            if price_diff < 0 and score > predict_accuracy:
                #Be Extra Sure, Set stop loss very tight???
                limitDistance_value = "2"
                DIRECTION_TO_TRADE = "SELL"
                DIRECTION_TO_CLOSE = "BUY"
                DIRECTION_TO_COMPARE = 'offer'
                DO_A_THING = True
            elif price_diff > 0 and score > predict_accuracy:
                #Be Extra Sure, Set stop loss very tight???
                limitDistance_value = "2"
                DIRECTION_TO_TRADE = "SELL"
                DIRECTION_TO_CLOSE = "BUY"
                DIRECTION_TO_COMPARE = 'offer'
                DO_A_THING = True
                
        
        
    if not DO_A_THING:
        #DO_A_THING NOT SET FOR WHATEVER REASON, GO BACK TO MAIN PROGRAM LOOP
        print ("-----------------DEBUG-----------------")
        print ("!!DEBUG!! AN ERROR OCCURED")
        print ("!!DEBUG!! Reminder, Check what the f*** is going on here")
        print ("!!DEBUG!! Most likely DO_A_THING Not Set!!")
        print ("-----------------DEBUG-----------------")
        continue
    
    previous_traded_epic_id = epic_id
    
    if Tight_Spread == True:
        limitDistance_value = "2"
    
    base_url = REAL_OR_NO_REAL + '/positions/otc'
    authenticated_headers = {'Content-Type':'application/json; charset=utf-8',
            'Accept':'application/json; charset=utf-8',
            'X-IG-API-KEY':API_KEY,
            'CST':CST_token,
            'X-SECURITY-TOKEN':x_sec_token}
            
    data = {"direction":DIRECTION_TO_TRADE,"epic": epic_id, "limitDistance":limitDistance_value, "orderType":orderType_value, "size":size_value,"expiry":expiry_value,"guaranteedStop":guaranteedStop_value,"currencyCode":currencyCode_value,"forceOpen":forceOpen_value,"stopDistance":stopDistance_value}
    r = requests.post(base_url, data=json.dumps(data), headers=authenticated_headers)
    
    print ("-----------------DEBUG-----------------")
    print(r.status_code)
    print(r.reason)
    print (r.text)
    print ("-----------------DEBUG-----------------")
        
        
    
    d = json.loads(r.text)
    deal_ref = d['dealReference']
    systime.sleep(2)
    # MAKE AN ORDER
    #CONFIRM MARKET ORDER
    base_url = REAL_OR_NO_REAL + '/confirms/'+ deal_ref
    auth_r = requests.get(base_url, headers=authenticated_headers)
    d = json.loads(auth_r.text)
    DEAL_ID = d['dealId']
    print("DEAL ID : " + str(d['dealId']))
    print(d['dealStatus'])
    print(d['reason'])
    #######################################################################################
    #This gets triggered if IG want a daft amount in your account for the margin, More than you specified initially. 
    #This is fine, Whilst it is a bit hacky basically start over again.
    #######################################################################################
    if str(d['reason']) == "ATTACHED_ORDER_LEVEL_ERROR" or str(d['reason']) == "MINIMUM_ORDER_SIZE_ERROR" or str(d['reason']) == "INSUFFICIENT_FUNDS":
        print ("!!DEBUG!! Not enough wonga in your account for this type of trade!!, Try again!!")
        continue
        
        
    # the trade will only break even once the price of the asset being traded has surpassed the sell price (for long trades) or buy price (for short trades). 
    ##########################################
    ##########READ IN INITIAL PROFIT##########
    ##########################################
        
    base_url = REAL_OR_NO_REAL + '/positions/'+ DEAL_ID
    auth_r = requests.get(base_url, headers=authenticated_headers)      
    d = json.loads(auth_r.text)
        
    print ("-----------------DEBUG-----------------")
    print(r.status_code)
    print(r.reason)
    print (r.text)
    print ("-----------------DEBUG-----------------")
    
    if DIRECTION_TO_TRADE == "SELL":
        PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
        PROFIT_OR_LOSS = PROFIT_OR_LOSS * float(size_value)
        print ("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS))
    else:
        PROFIT_OR_LOSS = float(d['market'][DIRECTION_TO_COMPARE] - float(d['position']['openLevel']))
        PROFIT_OR_LOSS = PROFIT_OR_LOSS * float(size_value)
        print ("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS))
     
    ##########################################
    ##########READ IN INITIAL PROFIT##########
    ##########################################
    
    ##########################################
    #####KEEP READING IN FOR PROFIT###########
    ##########################################
    try:
        #while PROFIT_OR_LOSS < float(limitDistance_value): 
        while PROFIT_OR_LOSS < float(limitDistance_value * int(size_value)) - 1: #Take something from the market, Before Take Profit.
            elapsed_time = round((time() - Start_loop_time), 1) 
            print ("******************************")
            print ("Order Time : " + str(humanize_time(elapsed_time)))
      
            base_url = REAL_OR_NO_REAL + '/positions/'+ DEAL_ID
            auth_r = requests.get(base_url, headers=authenticated_headers)      
            d = json.loads(auth_r.text)
            
            while not int(auth_r.status_code) == 200:
                if int(auth_r.status_code) == 400 or int(auth_r.status_code) == 404:
                    break
                    #This is a good thing!! It means that It cannot find the Deal ID, Your take profit has been hit. 
                    
                #Cannot read from API, Wait and try again
                #Give the Internet/IG 30s to sort it's shit out and try again
                systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))
                print ("-----------------DEBUG-----------------")
                print ("HTTP API ERROR!! Please check your Internet connection and Try again...")
                print ("Check Ping and Latency between you and IG Index Servers")
                # print(auth_r.status_code)
                # print(auth_r.reason)
                # print (auth_r.text)
                print ("-----------------DEBUG-----------------")
                #Got some "basic" error checking after all
                base_url = REAL_OR_NO_REAL + '/positions/'+ DEAL_ID
                auth_r = requests.get(base_url, headers=authenticated_headers)      
                d = json.loads(auth_r.text)
            
            
            if DIRECTION_TO_TRADE == "SELL":
                PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
                PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
                PROFIT_OR_LOSS = float(PROFIT_OR_LOSS * float(size_value))
                print ("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS))
                systime.sleep(2) #Don't be too keen to read price
            else:
                PROFIT_OR_LOSS = float(d['market'][DIRECTION_TO_COMPARE] - float(d['position']['openLevel']))
                PROFIT_OR_LOSS = float(PROFIT_OR_LOSS * float(size_value))
                print ("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS))
                systime.sleep(2) #Don't be too keen to read price
                
            ARTIFICIAL_STOP_LOSS = int(max_range) * int(size_value)
            if ARTIFICIAL_STOP_LOSS > 100:
                print ("!!!!WARNING!!!! STOP LOSS MIGHT BE TOO HIGH :- Current Value is " + str(ARTIFICIAL_STOP_LOSS))
            ARTIFICIAL_STOP_LOSS = ARTIFICIAL_STOP_LOSS * -1 #Make Negative, DO NOT REMOVE!!
               
            if PROFIT_OR_LOSS < ARTIFICIAL_STOP_LOSS:
                #CLOSE TRADE/GTFO
                print ("!!!WARNING!!! POTENTIAL DIRECTION CHANGE!!")
                SIZE = size_value
                ORDER_TYPE = orderType_value
                base_url = REAL_OR_NO_REAL + '/positions/otc'
                data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
                #authenticated_headers_delete IS HACKY AF WORK AROUND!! AS PER .... https://labs.ig.com/node/36
                authenticated_headers_delete = {'Content-Type':'application/json; charset=utf-8',
                'Accept':'application/json; charset=utf-8',
                'X-IG-API-KEY':API_KEY,
                'CST':CST_token,
                'X-SECURITY-TOKEN':x_sec_token,
                '_method':"DELETE"}
                auth_r = requests.post(base_url, data=json.dumps(data), headers=authenticated_headers_delete) 
                #DEBUG
                print(auth_r.status_code)
                print(auth_r.reason)
                print (auth_r.text)
                print ("!!DEBUG TIME!! Direction Change Wait: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                Prediction_Wait_Timer = 900 #15Mins
                systime.sleep(Prediction_Wait_Timer)
                
            if elapsed_time > 10800:
                print ("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER TIME")
                if float (PROFIT_OR_LOSS) > 0.50: #50p
                    print ("!!DEBUG!! TRADE OPEN OVER TIME AND IN PROFIT")
                    SIZE = size_value
                    ORDER_TYPE = orderType_value
                    base_url = REAL_OR_NO_REAL + '/positions/otc'
                    data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
                    #authenticated_headers_delete IS HACKY AF WORK AROUND!! AS PER .... https://labs.ig.com/node/36
                    authenticated_headers_delete = {'Content-Type':'application/json; charset=utf-8',
                    'Accept':'application/json; charset=utf-8',
                    'X-IG-API-KEY':API_KEY,
                    'CST':CST_token,
                    'X-SECURITY-TOKEN':x_sec_token,
                    '_method':"DELETE"}
                    auth_r = requests.post(base_url, data=json.dumps(data), headers=authenticated_headers_delete) 
                    #DEBUG
                    print(auth_r.status_code)
                    print(auth_r.reason)
                    print (auth_r.text)
                    print ("!!DEBUG!! : TIME AND IN PROFIT :- CLOSED")
                    
          
            if elapsed_time > 18000:
                print ("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER 4 HOURS")
                if -10 <= float (PROFIT_OR_LOSS) <= 0.50:
                    print ("!!DEBUG!! TRADE OPEN OVER 4 HOURS, CUT LOSSES")
                    #ENABLE THIS CODE WHEN HAPPY WITH VALUES
                    ########################################
                    SIZE = size_value
                    ORDER_TYPE = orderType_value
                    base_url = REAL_OR_NO_REAL + '/positions/otc'
                    data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
                    #authenticated_headers_delete IS HACKY AF WORK AROUND!! AS PER .... https://labs.ig.com/node/36
                    authenticated_headers_delete = {'Content-Type':'application/json; charset=utf-8',
                    'Accept':'application/json; charset=utf-8',
                    'X-IG-API-KEY':API_KEY,
                    'CST':CST_token,
                    'X-SECURITY-TOKEN':x_sec_token,
                    '_method':"DELETE"}
                    auth_r = requests.post(base_url, data=json.dumps(data), headers=authenticated_headers_delete) 
                    #DEBUG
                    print(auth_r.status_code)
                    print(auth_r.reason)
                    print (auth_r.text)
                    print ("DEBUG : TIME AND IN PROFIT :- CLOSED")
                
                        
    except Exception as e:
        #print(e) #Yeah, I know now. 
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print ("ERROR : ORDER MIGHT NOT BE OPEN FOR WHATEVER REASON")
        #WOAH CALM DOWN! WAIT .... STOP LOSS MIGHT HAVE BEEN HIT (Or take Profit)
        systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))
        pass
    
        #systime.sleep(1)
            
    if PROFIT_OR_LOSS > 0:
        profitable_trade_count = int(profitable_trade_count) + 1
        print ("DEBUG : ASSUME PROFIT!! Profitable Trade Count " + str(profitable_trade_count))
        SIZE = size_value
        ORDER_TYPE = orderType_value
        
        base_url = REAL_OR_NO_REAL + '/positions/otc'
        data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
        #authenticated_headers_delete IS HACKY AF WORK AROUND!! AS PER .... https://labs.ig.com/node/36
        authenticated_headers_delete = {'Content-Type':'application/json; charset=utf-8',
                'Accept':'application/json; charset=utf-8',
                'X-IG-API-KEY':API_KEY,
                'CST':CST_token,
                'X-SECURITY-TOKEN':x_sec_token,
                '_method':"DELETE"}
        
        auth_r = requests.post(base_url, data=json.dumps(data), headers=authenticated_headers_delete)   
        #CLOSE TRADE
        print(auth_r.status_code)
        print(auth_r.reason)
        print (auth_r.text)
        
        # #CONFIRM CLOSE - FUTURE
        # base_url = REAL_OR_NO_REAL + '/confirms/'+ deal_ref
        # auth_r = requests.get(base_url, headers=authenticated_headers)
        # d = json.loads(auth_r.text)
        # DEAL_ID = d['dealId']
        # print("DEAL ID : " + str(d['dealId']))
        # print(d['dealStatus'])
        # print(d['reason'])
        
        systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER)) #Obligatory Wait before doing next order
