#IF YOU FOUND THIS USEFUL, Please Donate some Bitcoin .... 1FWt366i5PdrxCC6ydyhD8iywUHQ2C7BWC

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import datetime
import json
from time import time, sleep
import random
import time as systime
#from statistics import mean, median
import numpy as np
#Scikit's LinearRegression model
from sklearn.linear_model import LinearRegression

import sys, os
import configparser

from ig import API

from lib.prediction import Prediction
import lib.util

config = configparser.ConfigParser()
config.read("default.conf")
config.read("config.conf")

api = API()
api.init()
 
orderType_value = "MARKET"
size_value = "1"
expiry_value = "DFB"
currencyCode_value = "GBP"
stopDistance_value = str(config['Trade']['stopDistance_value'])

epics = json.loads(config['Epics']['EPICS'])

#*******************************************************************
caution = float(config['Trade']['caution']) #Let's not miss out on some profits! 

print ("START TIME : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))    

high_resolution = eval(config['Trade']['high_resolution'])

for times_round_loop in range(1, 9999):
    Start_loop_time = time()

    d = api.find_next_trade(list(epics.keys()))

    epic_id = d['values']['EPIC']
    current_price = float(d['values']['BID'])

    prediction = Prediction(api.config)
    prediction.set_marketdata( api.clientsentiment(epic_id) )
    if prediction.quick_check() is None:
      # no point pulling in market data (right now), we'll reject this later on anyway
      continue
    
    DIRECTION_TO_TRADE = None
    while DIRECTION_TO_TRADE is None:
        print ("!!Internal Notes only - Top of Loop!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
        systime.sleep(1.5)
        # Your input data, X and Y are lists (or Numpy Arrays)
        #THIS IS YOUR TRAINING DATA
        x = [] #This is Low Price, Volume
        y = [] #This is High Price
       
        ############################################################
        resolutions = ['DAY/14'] #This is just for the Average True Range, Base it on the last 14 days trading. (14 is the default in ATR)
        for resolution in resolutions:
          d = api.prices(epic_id, resolution)

        print ("-----------------DEBUG-----------------")
        print ("Remaining API Calls left : " + str(api.allowance['remainingAllowance']))
        print ("Time to API Key reset : " + str(lib.util.humanize_time(int(api.allowance['allowanceExpiry']))))
        print ("-----------------DEBUG-----------------")

        price_ranges = []
        closing_prices = []
        TR_prices = []
        price_compare = "bid"

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
        systime.sleep(1.5)
        
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_2, HOUR_4, DAY, WEEK, MONTH)
        # This is the high roller, For the price prediction. 
        if high_resolution:
          resolutions = ['HOUR/5', 'HOUR_2/5', 'HOUR_3/5', 'HOUR_4/5', 'DAY/5']
        else:
          resolutions = ['MINUTE_15/30', 'MINUTE_30/30']
        for resolution in resolutions:
            d = api.prices(epic_id, resolution)
            
            for i in d['prices']:
                tmp_list = []
                high_price = i['highPrice'][price_compare]
                low_price = i['lowPrice'][price_compare]
                close_price = i['closePrice'][price_compare]
                ############################################
                volume = i['lastTradedVolume']
                #---------------------------------
                tmp_list.append(float(high_price))
                tmp_list.append(float(low_price))
                x.append(tmp_list)
                #x is Low Price and Volume
                y.append(float(close_price))
                #y = High Prices

        ###################################################################################
        ###################################################################################
        #Here we just need a value to predict the next one of. 
        
        if high_resolution:
          d = api.prices(epic_id, 'DAY/1')
        
          for i in d['prices']:
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
        else:
          res = api.fetch_day_highlow(epic_id)
          low_price = float(res['values']['DAY_LOW'])
          high_price = float(res['values']['DAY_HIGH']) # this is (now) an hourly volume - will that be an issue?

        #####################################################################
        #########################PREDICTION CODE#############################
        #####################################################################
        
        x = np.asarray(x)
        y = np.asarray(y)
        # Initialize the model then train it on the data
        genius_regression_model = LinearRegression()
        genius_regression_model.fit(x,y)
        # Predict the corresponding value of Y for X
        pred_ict = [high_price,low_price]
        pred_ict = np.asarray(pred_ict) #To Numpy Array, hacky but good!! 
        pred_ict = pred_ict.reshape(1, -1)
        price_prediction = genius_regression_model.predict(pred_ict)
        print ("PRICE PREDICTION FOR PRICE " + epic_id + " IS : " + str(price_prediction))


        score = genius_regression_model.score(x,y)
        predictions = {'intercept': genius_regression_model.intercept_, 'coefficient': genius_regression_model.coef_, 'current_price': current_price, 'predicted_value': price_prediction, 'accuracy' : score}
        print ("-----------------DEBUG-----------------")
        print (score)
        print (predictions)
        print ("-----------------DEBUG-----------------")
            
        price_diff = current_price - price_prediction
        
        prediction.limitDistance_value = int(price_diff * score * float(config['Trade']['greed'])) # vary according to certainty and greed
        if float(prediction.limitDistance_value) < 0:
            prediction.limitDistance_value *= -1 
            
        DIRECTION_TO_TRADE = prediction.determine_trade_direction(score, current_price, price_prediction)
        
        if DIRECTION_TO_TRADE is None:
            #No trade direction
            print ("!!DEBUG!! Literally NO decent trade direction could be determined")
            break

    # LET'S DO THIS
    if DIRECTION_TO_TRADE == 'SELL':
      DIRECTION_TO_CLOSE = 'BUY'
      DIRECTION_TO_COMPARE = 'offer'
    else:
      DIRECTION_TO_CLOSE = 'SELL'
      DIRECTION_TO_COMPARE = 'bid'

    data = {"direction":DIRECTION_TO_TRADE,"epic": epic_id, "limitDistance":str(prediction.limitDistance_value), "orderType":orderType_value, "size":size_value,"expiry":expiry_value,"currencyCode":currencyCode_value,"forceOpen":True,"stopDistance":stopDistance_value}
    data = api.handleDealingRules(data)

    d = api.positions_otc(data)
    try:
        deal_ref = d['dealReference']
    except:
        continue
        
    systime.sleep(2)
    # MAKE AN ORDER

    #CONFIRM MARKET ORDER
    d = api.confirms(deal_ref)    
    DEAL_ID = d['dealId']
    print("DEAL ID : {} - {} - {}".format(str(d['dealId']), d['dealStatus'], d['reason']))
   
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

    # let account stream provide updates, and let limit close it (for now)
    # TODO: monitor trades with stream thread or waste of a stream?
    systime.sleep(random.randint(1, 60)) #Obligatory Wait before doing next order
    api.open_positions = api.positions()
    continue
    
    # api.setdebug(True)
    # d = api.positions(DEAL_ID)
    # api.setdebug(False)
        
    # TIME_WAIT_MULTIPLIER = 60
    # if DIRECTION_TO_TRADE == "SELL":
    #     PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
    # else:
    #     PROFIT_OR_LOSS = float(d['market'][DIRECTION_TO_COMPARE] - float(d['position']['openLevel']))
    # PROFIT_OR_LOSS = PROFIT_OR_LOSS * float(size_value)
    # print ("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS))
     
    # ##########################################
    # #####KEEP READING IN FOR PROFIT###########
    # ##########################################
    # try:
    #     #while PROFIT_OR_LOSS < float(prediction.limitDistance_value): 
    #     while PROFIT_OR_LOSS < float(float(prediction.limitDistance_value) * float(size_value)) - 1: #Take something from the market, Before Take Profit.
    #         elapsed_time = round((time() - Start_loop_time), 1) 

    #         api.json = False
    #         auth_r = api.positions(DEAL_ID)
    #         api.json = True
    #         d = json.loads(auth_r.text)
            
    #         while not int(auth_r.status_code) == 200:
    #             if int(auth_r.status_code) == 400 or int(auth_r.status_code) == 404:
    #                 break
    #                 #This is a good thing!! It means that It cannot find the Deal ID, Your take profit has been hit. 
                    
    #             #Cannot read from API, Wait and try again
    #             #Give the Internet/IG 30s to sort it's shit out and try again
    #             systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))
    #             print ("-----------------DEBUG-----------------")
    #             print ("HTTP API ERROR!! Please check your Internet connection and Try again...")
    #             print ("Check Ping and Latency between you and IG Index Servers")
    #             # print(auth_r.status_code)
    #             # print(auth_r.reason)
    #             # print (auth_r.text)
    #             print ("-----------------DEBUG-----------------")
    #             #Got some "basic" error checking after all
    #             d = api.positions(DEAL_ID)
               
    #         if DIRECTION_TO_TRADE == "SELL":
    #             PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
    #         else:
    #             PROFIT_OR_LOSS = float(d['market'][DIRECTION_TO_COMPARE] - float(d['position']['openLevel']))
    #         PROFIT_OR_LOSS = float(PROFIT_OR_LOSS * float(size_value))
    #         print ("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS) + " Order Time : " + str(humanize_time(elapsed_time)))
    #         systime.sleep(2) #Don't be too keen to read price
                
    #         ARTIFICIAL_STOP_LOSS = float(max_range) * float(size_value)
    #         if ARTIFICIAL_STOP_LOSS > 100:
    #             print ("!!!!WARNING!!!! STOP LOSS MIGHT BE TOO HIGH :- Current Value is " + str(ARTIFICIAL_STOP_LOSS))
    #         ARTIFICIAL_STOP_LOSS = ARTIFICIAL_STOP_LOSS * -1 #Make Negative, DO NOT REMOVE!!

    #         def close_trade():
    #             SIZE = size_value
    #             ORDER_TYPE = orderType_value
    #             data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
    #             api.setdebug(True)
    #             auth_r = api.positions_otc_close(data)
    #             api.setdebug(False)
               
    #         if PROFIT_OR_LOSS < ARTIFICIAL_STOP_LOSS:
    #             #CLOSE TRADE/GTFO
    #             print ("!!!WARNING!!! POTENTIAL DIRECTION CHANGE!!")
    #             close_trade()
    #             print ("!!DEBUG TIME!! Direction Change Wait: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
    #             Prediction_Wait_Timer = 900 #15Mins
    #             systime.sleep(Prediction_Wait_Timer)
                
    #         if elapsed_time > 12600:
    #             print ("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER TIME")
    #             if float (PROFIT_OR_LOSS) > 0:
    #                 print ("!!DEBUG!! TRADE OPEN OVER TIME AND IN PROFIT")
    #                 close_trade()
    #                 print ("!!DEBUG!! : TIME AND IN PROFIT :- CLOSED")
                    
          
    #         if elapsed_time > 18000:
    #             print ("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER 5 HOURS")
    #             if -9 <= float (PROFIT_OR_LOSS) <= 0:
    #                 print ("!!DEBUG!! TRADE OPEN OVER 5 HOURS, CUT LOSSES")
    #                 close_trade()
    #                 print ("DEBUG : TIME AND IN PROFIT :- CLOSED")
            
    #         if (float(PROFIT_OR_LOSS) > 9 and elapsed_time < 2700) or (float (PROFIT_OR_LOSS) > 20 and elapsed_time > 7200):
    #             close_trade()
    #             print ("DEBUG : TIME AND IN PROFIT :- CLOSED")

                        
    # except Exception as e:
    #     print(e) #Yeah, I know now. 
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     print(exc_type, fname, exc_tb.tb_lineno)
    #     print ("ERROR : ORDER MIGHT NOT BE OPEN FOR WHATEVER REASON")
    #     #WOAH CALM DOWN! WAIT .... STOP LOSS MIGHT HAVE BEEN HIT (Or take Profit)
    #     systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))
    #     pass
    
           
    # if PROFIT_OR_LOSS > 0:
    #     profitable_trade_count = int(profitable_trade_count) + 1
    #     print ("DEBUG : ASSUME PROFIT!! Profitable Trade Count " + str(profitable_trade_count))
    #     SIZE = size_value
    #     ORDER_TYPE = orderType_value
        
    #     #CLOSE TRADE
    #     data = {"dealId":DEAL_ID,"direction":DIRECTION_TO_CLOSE,"size":SIZE,"orderType":ORDER_TYPE}
    #     api.setdebug(True)
    #     auth_r = api.positions_otc_close(data)
    #     api.setdebug(False)
        
    #     # #CONFIRM CLOSE - FUTURE
    #     # d = api.confirms(deal_ref)
    #     # DEAL_ID = d['dealId']
    #     # print("DEAL ID : " + str(d['dealId']))
    #     # print(d['dealStatus'])
    #     # print(d['reason'])
        
    #     systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER)) #Obligatory Wait before doing next order
