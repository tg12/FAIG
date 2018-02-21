#IF YOU FOUND THIS USEFUL, Please Donate some Bitcoin .... 1FWt366i5PdrxCC6ydyhD8iywUHQ2C7BWC

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
import json
import logging
import sys
from time import time, sleep
import random
import time as systime
from statistics import mean, median
import numpy as np
#Scikit's LinearRegression model
from sklearn.linear_model import LinearRegression
##################################################
import sys, os
import configparser

from igclient import IGClient

igclient = IGClient()

config = configparser.ConfigParser()
config.read("default.conf")
config.read("config.conf")

igclient.session()
 
#GET ACCOUNTS
d = igclient.accounts()

for i in d['accounts']:
    if str(i['accountType']) == "SPREADBET":
        print ("Spreadbet Account ID is : " + str(i['accountId']))
        spreadbet_acc_id = str(i['accountId'])

#SET SPREAD BET ACCOUNT AS DEFAULT
r = igclient.update_session({"accountId":spreadbet_acc_id,"defaultAccount": "True"})
#ERROR about account ID been the same, Ignore! 

###################################################################################
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

# PROGRAMMABLE VALUES
#SET INITIAL VARIABLES, SOME ARE CALCUALTED LATER
limitDistance_value = "4" 
orderType_value = "MARKET"
size_value = "2"
expiry_value = "DFB"
guaranteedStop_value = True
currencyCode_value = "GBP"
forceOpen_value = True
stopDistance_value = "150" #Initial Stop loss, Worked out later per trade

epic_ids = json.loads(config['Epics']['EPIC_IDS'])

#*******************************************************************
predict_accuracy = 0.89
TIME_WAIT_MULTIPLIER = 60
#STOP_LOSS_MULTIPLIER = 4 #Not currently in use, 13th Jan
Client_Sentiment_Check = 69
profitable_trade_count = 0
previous_traded_epic_id = "None"
Tight_Spread = False
High_Trend_Watermark = 89

#******************************************************************************************************************************
#******************************************************************************************************************************
#******************************************************************************************************************************
#"You can use sentiment as a filter. Only taking the setups going against the crowd. You must be in the minority of 40% or less."
#More information See here :-https://www.reddit.com/r/Forex/comments/7wehbq/how_much_does_client_sentiment_sway_your_decisions/
#******************************************************************************************************************************
#******************************************************************************************************************************
#******************************************************************************************************************************

print ("START TIME : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))

def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)   
    
for times_round_loop in range(1, 9999):

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

    while not Price_Change_OK:
        random.shuffle(epic_ids)
        epic_id = random.choice(epic_ids)
        #Don't Trade on the same epic twice in a row
        if str(previous_traded_epic_id) == str(epic_id):
            Price_Change_OK = False
            print ("!!DEBUG!! : Don't Trade on the same epic twice in a row")
            continue

        print("!!DEBUG : Random epic_id: " + str(epic_id), end='')
        systime.sleep(2)
        d = igclient.markets(epic_id)

        MARKET_ID = d['instrument']['marketId']
        current_price = d['snapshot']['bid']
        Price_Change_Day = d['snapshot']['netChange']
        
        if d['snapshot']['percentageChange'] is None:
            Price_Change_Day_percent = 0
        else:
            Price_Change_Day_percent = float(d['snapshot']['percentageChange'])

        if (Price_Change_Day_percent > 0.48 and Price_Change_Day_percent < 1.9) or (Price_Change_Day_percent < -0.48 and Price_Change_Day_percent > -1.9): 
            print (" Day Price Change {}% ".format(str(Price_Change_Day_percent)), end='')
            Price_Change_OK = True
            bid_price = d['snapshot']['bid']
            ask_price = d['snapshot']['offer']
            spread = float(bid_price) - float(ask_price)

            ##################################################################################################################
            ##################################################################################################################
            #e.g Spread is -30, That is too big, In-fact way too big. Spread is -1.7, This is not too bad, We can trade on this reasonably well.
            #Spread is 0.8. This is considered a tight spread
            ##################################################################################################################
            ##################################################################################################################
            #if spread is less than -2, It's too big
            if float(spread) < -2:
              print (":- spread not ok {}".format(spread), end="\n", flush=True)
              Price_Change_OK = False
              systime.sleep(2)
            elif float(spread) > -2:
              print (":- GOOD SPREAD {}".format(spread), end="\n", flush=True)
              Price_Change_OK = True
            else:
              print (":- spread exactly {} - not ok".format(spread), end="\n", flush=True)
        else:
            print(": !Price change {}%".format(Price_Change_Day_percent), end="\n", flush=True)

    #Good ol "Crowd-sourcing" check.....
    d = igclient.clientsentiment(MARKET_ID)
    
    longPositionPercentage = float(d['longPositionPercentage'])
    shortPositionPercentage = float(d['shortPositionPercentage'])
    
    while not DO_A_THING:
        print ("!!Internal Notes only - Top of Loop!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        d = igclient.prices(epic_id, 'DAY/30')
        
        day_moving_avg_30 = []
        # Your input data, X and Y are lists (or Numpy Arrays)
        #THIS IS YOUR TRAINING DATA
        x = [] #This is Low Price, Volume
        y = [] #This is High Price
        
        #I only need this API call for real world values
        remaining_allowance = d['allowance']['remainingAllowance']
        reset_time = humanize_time(int(d['allowance']['allowanceExpiry']))
                
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

        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        resolutions = ['HOUR_4/30', 'HOUR_3/30', 'HOUR_2/30', 'HOUR/30']
        for resolution in resolutions:
            d = igclient.prices(epic_id, resolution)
            
            for i in d['prices']:
                tmp_list = []
                high_price = i['highPrice'][price_compare]
                low_price = i['lowPrice'][price_compare]
                volume = i['lastTradedVolume']
                #---------------------------------
                if low_price != None:
                    tmp_list.append(float(low_price))
                    tmp_list.append(float(volume))
                    x.append(tmp_list)
                    #x is Low Price and Volume
                    y.append(float(high_price))
                    #y = High Prices
            
        ###################################################################################
        
        #Cut down on API Calls by using this again! 
        
        price_ranges = []
        closing_prices = []
        TR_prices = []

        for count, i in enumerate(d['prices']):
            if count == 0:
                #First time round loop cannot get previous
                closePrice = i['closePrice'][price_compare]
                closing_prices.append(closePrice)
                high_price = i['highPrice'][price_compare]
                low_price = i['lowPrice'][price_compare]
                price_range = float(high_price - closePrice)
                price_ranges.append(price_range)
            else:
                prev_close = closing_prices[-1]
                ###############################
                closePrice = i['closePrice'][price_compare]
                closing_prices.append(closePrice)
                high_price = i['highPrice'][price_compare]
                low_price = i['lowPrice'][price_compare]
                try:
                  price_range = float(high_price - closePrice)
                except Exception:
                  print ("No data for {e}.{r}".format(e=epic_id, r=resolution))
                  #sys.exit(1)
                price_ranges.append(price_range)
                TR = max(high_price-low_price, abs(high_price-prev_close), abs(low_price-prev_close))
                #print (TR)
                TR_prices.append(TR)
                
             
        max_range = max(TR_prices)
        low_range = min(TR_prices)
        print ("stopDistance_value for " + str(epic_id) + " will bet set at " + str(float(max_range)))
        print ("limitDistance_value for " + str(epic_id) + " will bet set at " + str(float(low_range)))
        if low_range > 10:
            print ("!!DEBUG!! WARNING - Take Profit over high value, Might take a while for this trade!!")
            
        #print ("MAX RANGE FOR " + str(epic_id) + " IS " + str(int(max_range)))
        #print ("LOW RANGE FOR " + str(epic_id) + " IS " + str(int(low_range)))
        #Cut down on API Calls by using this again! 

        ###################################################################################
        ###################################################################################
        
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        resolutions = ['MINUTE_30/30', 'MINUTE_15/30', 'MINUTE_10/30', 'MINUTE_5/30', 'MINUTE_3/30', 'MINUTE_2/30', 'MINUTE/30']
        for resolution in resolutions:
            d = igclient.prices(epic_id, resolution)
            
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

        d = igclient.prices(epic_id, 'DAY/1')
        
        for i in d['prices']:
            low_price = i['lowPrice'][price_compare]
            volume = i['lastTradedVolume']

        #####################################################################
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
        print ("-----------------DEBUG-----------------")
        print (score)
        print (predictions)
        print ("-----------------DEBUG-----------------")
            
        price_diff = current_price - price_prediction
        
        limitDistance_value = int(low_range)
        
        #Fixing a weird bug with some exotic fx, Where the prediction is 0. 
        #Fixing a weird bug with some exotic fx, Where the prediction is 0.
        if int(limitDistance_value) <= 0:
            limitDistance_value = "1"
            
        #stopDistance_value = int(max_range) 
        #NOTE Sometimes IG Index want a massive stop loss for Guaranteed, Either don't use Guaranteed or "sell at market" with Artificial Stop loss
        #MUST NOTE :- IF THIS PRICE IS - i.e NOT HIT TARGET YET, CONVERSELY IF THIS PRICE IS POSITIVE IT IS ALREADY ABOVE PREDICTION!!!
        #print ("TRUE GUARANTEED STOP LOSS DISTANCE WILL BE SET AT : " + str(stopDistance_value))
        #print ("Price Difference Away (Point's) : " + str(price_diff))
        
        ############################
        #NEW METHOD OF SETTING LIMIT - BETA CODE!! TEST CAREFULLY!! 
        ############################
        
        # tmp_price_diff = price_diff * -1
        # take_profit_limit = float(low_range) + (float(tmp_price_diff)) / 4
        # true_profit = float(take_profit_limit) * float(size_value)
        # limitDistance_value = int(take_profit_limit)
        
        # print ("!!!DEBUG!!! !!!DEBUG!!! !!!DEBUG!!! !!!DEBUG!!!")
        # print ("Profit is set at :- " + str(true_profit))
        # print ("!!!DEBUG!!! !!!DEBUG!!! !!!DEBUG!!! !!!DEBUG!!!")
        
                   
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

        if float(score) < float(predict_accuracy):
            # NOT ACCURATE ENOUGH (YET)
            print ("!!DEBUG!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
            DO_A_THING = False
            print ("!!DEBUG!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
            systime.sleep(Prediction_Wait_Timer)
            print ("!!DEBUG!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
            break

        #Three things, Price difference is less than target, Accuracy is OK, Current Price is less than Price Prediction
        #Added a fourth thing "contrarian indicator"
        
        print ("price_diff:{} score:{} current_price:{} limitDistance_value:{} predict_accuracy:{} price_prediction:{}".format(price_diff, score, current_price, limitDistance_value, predict_accuracy, price_prediction))
        b_contrarian = eval(config['Trade']['b_contrarian']) #THIS MUST BE SET EITHER WAY!! 
        if b_contrarian == True:
            print ("!!DEBUG!! b_contrarian SET!!")
            if price_diff < 0 and score > predict_accuracy and float(current_price) < float(price_prediction):
                if float(shortPositionPercentage) > float(longPositionPercentage) and float(shortPositionPercentage) > Client_Sentiment_Check:
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif float(longPositionPercentage) > float(shortPositionPercentage) and float(longPositionPercentage) > Client_Sentiment_Check:
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                elif longPositionPercentage >= High_Trend_Watermark:
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif shortPositionPercentage >= High_Trend_Watermark:
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                else:
                    print ("!!DEBUG No Trade This time")
                    DO_A_THING = False
                    break
                
            elif float(price_diff) > float(limitDistance_value) and score > predict_accuracy and float(current_price) > float(price_prediction):
                #!!!!Above Predicted Target!!!!
                #Tight limit (Take Profit)
                if float(shortPositionPercentage) > float(longPositionPercentage) and float(shortPositionPercentage) > Client_Sentiment_Check:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif float(longPositionPercentage) > float(shortPositionPercentage) and float(longPositionPercentage) > Client_Sentiment_Check:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                elif longPositionPercentage >= High_Trend_Watermark:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif shortPositionPercentage >= High_Trend_Watermark:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                else:
                    print ("!!DEBUG No Trade This time")
                    DO_A_THING = False
                    break
            else:
                DO_A_THING = False
                print ("!!DEBUG!! NO CRITERIA YET - SLEEPING!!: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                systime.sleep(Prediction_Wait_Timer)
                print ("!!DEBUG!! NO CRITERIA!! " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                break
        
        elif b_contrarian == False:
            print ("!!DEBUG!! b_contrarian NOT SET!! !!WARNING!! :- You are following the client sentiment")
            if price_diff < 0 and score > predict_accuracy and float(current_price) < float(price_prediction):
                if float(longPositionPercentage) > float(shortPositionPercentage) and float(longPositionPercentage) > Client_Sentiment_Check:
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif float(shortPositionPercentage) > float(longPositionPercentage) and float(shortPositionPercentage) > Client_Sentiment_Check:
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                elif longPositionPercentage >= High_Trend_Watermark:
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif shortPositionPercentage >= High_Trend_Watermark:
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                else:
                    print ("!!DEBUG No Trade This time")
                    DO_A_THING = False
                    break
                
            elif float(price_diff) > float(limitDistance_value) and score > predict_accuracy and float(current_price) > float(price_prediction):
                #!!!!Above Predicted Target!!!!
                #Tight limit (Take Profit)
                if float(longPositionPercentage) > float(shortPositionPercentage) and float(longPositionPercentage) > Client_Sentiment_Check:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif float(shortPositionPercentage) > float(longPositionPercentage) and float(shortPositionPercentage) > Client_Sentiment_Check:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                elif longPositionPercentage >= High_Trend_Watermark:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "BUY"
                    DIRECTION_TO_CLOSE = "SELL"
                    DIRECTION_TO_COMPARE = 'bid'
                    DO_A_THING = True
                elif shortPositionPercentage >= High_Trend_Watermark:
                    limitDistance_value = "2"
                    DIRECTION_TO_TRADE = "SELL"
                    DIRECTION_TO_CLOSE = "BUY"
                    DIRECTION_TO_COMPARE = 'offer'
                    DO_A_THING = True
                else:
                    print ("!!DEBUG No Trade This time")
                    DO_A_THING = False
                    break
            else:
                DO_A_THING = False
                print ("!!DEBUG!! NO CRITERIA YET - SLEEPING!!: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                systime.sleep(Prediction_Wait_Timer)
                print ("!!DEBUG!! NO CRITERIA!! " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                break

    if not DO_A_THING:
        #DO_A_THING NOT SET FOR WHATEVER REASON, GO BACK TO MAIN PROGRAM LOOP
        print ("-----------------DEBUG-----------------")
        print ("!!DEBUG!! AN ERROR OCCURED")
        print ("!!DEBUG!! Reminder, Check what the f*** is going on here")
        print ("!!DEBUG!! Most likely DO_A_THING Not Set!!")
        print ("-----------------DEBUG-----------------")
        continue

    data = {"direction":DIRECTION_TO_TRADE,"epic": epic_id, "limitDistance":limitDistance_value, "orderType":orderType_value, "size":size_value,"expiry":expiry_value,"guaranteedStop":guaranteedStop_value,"currencyCode":currencyCode_value,"forceOpen":forceOpen_value,"stopDistance":stopDistance_value}
    igclient.setdebug(True)
    d = igclient.positions_otc(data)
    
    deal_ref = d['dealReference']
    systime.sleep(2)
    # MAKE AN ORDER

    #CONFIRM MARKET ORDER
    d = igclient.confirms(deal_ref)    
    igclient.setdebug(False)
    DEAL_ID = d['dealId']
    print("DEAL ID : " + str(d['dealId']))
    print(d['dealStatus'])
    print(d['reason'])
    
    #######################################################################################
    #This gets triggered if IG want a daft amount in your account for the margin, More than you specified initially. This happens sometimes... deal with it! 
    #This is fine, Whilst it is a bit hacky basically start over again.
    #######################################################################################
    if str(d['reason']) == "ATTACHED_ORDER_LEVEL_ERROR" or str(d['reason']) == "MINIMUM_ORDER_SIZE_ERROR" or str(d['reason']) == "INSUFFICIENT_FUNDS" or str(d['reason']) == "MARKET_OFFLINE":
        print ("!!DEBUG!! Not enough wonga in your account for this type of trade!!, Try again!!")
        continue
  
                                         
    # the trade will only break even once the price of the asset being traded has surpassed the sell price (for long trades) or buy price (for short trades). 
    ##########################################
    ##########READ IN INITIAL PROFIT##########
    ##########################################
    
    igclient.setdebug(True)
    d = igclient.positions(DEAL_ID)
    igclient.setdebug(False)
        
    ##########################################
    ##########READ IN INITIAL PROFIT##########
    ##########################################
    
    if DIRECTION_TO_TRADE == "SELL":
        PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
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
        while PROFIT_OR_LOSS < float(float(limitDistance_value) * float(size_value)) - 1: #Take something from the market, Before Take Profit.
            elapsed_time = round((time() - Start_loop_time), 1) 

            igclient.json = False
            auth_r = igclient.positions(DEAL_ID)
            igclient.json = True
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
                d = igclient.positions(DEAL_ID)
               
            if DIRECTION_TO_TRADE == "SELL":
                PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
            else:
                PROFIT_OR_LOSS = float(d['market'][DIRECTION_TO_COMPARE] - float(d['position']['openLevel']))
            PROFIT_OR_LOSS = float(PROFIT_OR_LOSS * float(size_value))
            print ("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS) + " Order Time : " + str(humanize_time(elapsed_time)))
            systime.sleep(2) #Don't be too keen to read price
                
            ARTIFICIAL_STOP_LOSS = float(max_range) * float(size_value)
            if ARTIFICIAL_STOP_LOSS > 100:
                print ("!!!!WARNING!!!! STOP LOSS MIGHT BE TOO HIGH :- Current Value is " + str(ARTIFICIAL_STOP_LOSS))
            ARTIFICIAL_STOP_LOSS = ARTIFICIAL_STOP_LOSS * -1 #Make Negative, DO NOT REMOVE!!

            def close_trade():
                SIZE = size_value
                ORDER_TYPE = orderType_value
                data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
                igclient.setdebug(True)
                auth_r = igclient.positions_otc_close(data)
                igclient.setdebug(False)
               
            if PROFIT_OR_LOSS < ARTIFICIAL_STOP_LOSS:
                #CLOSE TRADE/GTFO
                print ("!!!WARNING!!! POTENTIAL DIRECTION CHANGE!!")
                close_trade()
                print ("!!DEBUG TIME!! Direction Change Wait: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                Prediction_Wait_Timer = 900 #15Mins
                systime.sleep(Prediction_Wait_Timer)
                
            if elapsed_time > 12600:
                print ("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER TIME")
                if float (PROFIT_OR_LOSS) > 0:
                    print ("!!DEBUG!! TRADE OPEN OVER TIME AND IN PROFIT")
                    close_trade()
                    print ("!!DEBUG!! : TIME AND IN PROFIT :- CLOSED")
                    
          
            if elapsed_time > 18000:
                print ("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER 5 HOURS")
                if -9 <= float (PROFIT_OR_LOSS) <= 0:
                    print ("!!DEBUG!! TRADE OPEN OVER 5 HOURS, CUT LOSSES")
                    close_trade()
                    print ("DEBUG : TIME AND IN PROFIT :- CLOSED")
            
            if (float(PROFIT_OR_LOSS) > 9 and elapsed_time < 2700) or (float (PROFIT_OR_LOSS) > 20 and elapsed_time > 7200):
                close_trade()
                print ("DEBUG : TIME AND IN PROFIT :- CLOSED")

                        
    except Exception as e:
        print(e) #Yeah, I know now. 
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
        
        #CLOSE TRADE
        data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
        igclient.setdebug(True)
        auth_r = igclient.positions_otc_close(data)
        igclient.setdebug(False)
        
        # #CONFIRM CLOSE - FUTURE
        # d = igclient.confirms(deal_ref)
        # DEAL_ID = d['dealId']
        # print("DEAL ID : " + str(d['dealId']))
        # print(d['dealStatus'])
        # print(d['reason'])
        
        systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER)) #Obligatory Wait before doing next order
        previous_traded_epic_id = str(epic_id)
