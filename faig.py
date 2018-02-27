# IF YOU FOUND THIS USEFUL, Please Donate some Bitcoin .... 1FWt366i5PdrxCC6ydyhD8iywUHQ2C7BWC

#!/usr/bin/env python3
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
# Scikit's LinearRegression model
from sklearn.linear_model import LinearRegression
##################################################
import sys
import os
import configparser

from igclient import IGClient
import igstream
from apps.market_watcher import MarketWatcher

igclient = IGClient()

config = configparser.ConfigParser()
config.read("default.conf")
config.read("config.conf")

d = igclient.session()
igstreamclient = igstream.IGStream(igclient=igclient, loginresponse=d)

subscription = igstream.Subscription(
    mode="DISTINCT",
    items=["TRADE:"+str(igclient.accountId)],
    fields=["OPU"])


def on_item_update(item_update):
    print(item_update)


igstreamclient.subscribe(subscription=subscription, listener=on_item_update)

# get open positions
open_positions = igclient.positions()

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
# SET INITIAL VARIABLES, SOME ARE CALCUALTED LATER
limitDistance_value = "4"
orderType_value = "MARKET"
size_value = "2"
expiry_value = "DFB"
guaranteedStop_value = True
currencyCode_value = "GBP"
forceOpen_value = True
stopDistance_value = str(config['Trade']['stopDistance_value'])  # Initial Stop loss, Worked out later per trade

epics = json.loads(config['Epics']['EPICS'])
epic_ids = list(epics.keys())

#*******************************************************************
predict_accuracy = float(config['Trade']['predict_accuracy'])
TIME_WAIT_MULTIPLIER = 60
Client_Sentiment_Check = 69
profitable_trade_count = 0
High_Trend_Watermark = 89

print("START TIME : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def fetch_day_highlow(epic_id):
    subscription = igstream.Subscription(
        mode="MERGE",
        items=["CHART:{}:HOUR".format(epic_id)],
        fields=["LTV", "DAY_LOW", "DAY_HIGH"]
    )
    res = igstreamclient.fetch_one(subscription)
    return res


def fetch_current_price(epic_id):
    try:
        subscription = igstream.Subscription(
            mode="MERGE",
            items=["MARKET:{}".format(epic_id)],
            fields=["MID_OPEN", "HIGH", "LOW", "CHANGE", "CHANGE_PCT", "UPDATE_TIME", "MARKET_DELAY", "MARKET_STATE", "BID", "OFFER"]
        )
        res = igstreamclient.fetch_one(subscription)
    except IndexError:
        # fall back to non-stream version
        res = igclient.markets(epic_id)
        res['values'] = {}
        res['values']['BID'] = res['snapshot']['bid']
        res['values']['OFFER'] = res['snapshot']['offer']
        res['values']['CHANGE'] = res['snapshot']['netChange']
        res['values']['CHANGE_PCT'] = res['snapshot']['percentageChange']
    return res


def trade_type_buy_short(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark):
    if float(shortPositionPercentage) > float(longPositionPercentage) and float(shortPositionPercentage) > Client_Sentiment_Check:
        return "BUY"
    elif float(longPositionPercentage) > float(shortPositionPercentage) and float(longPositionPercentage) > Client_Sentiment_Check:
        return "SELL"
    elif longPositionPercentage >= High_Trend_Watermark:
        return "BUY"
    elif shortPositionPercentage >= High_Trend_Watermark:
        return "SELL"
    else:
        print("!!DEBUG No Trade This time BS")
        print("!!DEBUG shortPositionPercentage:{} longPositionPercentage:{} Client_Sentiment_Check:{} High_Trend_Watermark:{}".format(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark))


def trade_type_buy_long(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark):
    if float(longPositionPercentage) > float(shortPositionPercentage) and float(longPositionPercentage) > Client_Sentiment_Check:
        return "BUY"
    elif float(shortPositionPercentage) > float(longPositionPercentage) and float(shortPositionPercentage) > Client_Sentiment_Check:
        return "SELL"
    elif longPositionPercentage >= High_Trend_Watermark:
        return "BUY"
    elif shortPositionPercentage >= High_Trend_Watermark:
        return "SELL"
    else:
        print("!!DEBUG No Trade This time BL")
        print("!!DEBUG longPositionPercentage:{} shortPositionPercentage:{} Client_Sentiment_Check:{} High_Trend_Watermark:{}".format(longPositionPercentage, shortPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark))


use_clientsentiment = eval(config['Trade']['use_clientsentiment'])
b_contrarian = eval(config['Trade']['b_contrarian'])  # THIS MUST BE SET IF use_clientsentiment == True
high_resolution = eval(config['Trade']['high_resolution'])

market_ids = {}


def get_market_id(epic_id):
    try:
        MARKET_ID = market_ids[epic_id]
    except KeyError:
        # lookup and cache - these won't change
        d = igclient.markets(epic_id)
        market_ids[epic_id] = d['instrument']['marketId']
        MARKET_ID = market_ids[epic_id]
    return MARKET_ID


def determine_trade_direction():
    if use_clientsentiment:
        if b_contrarian == True:
                #print ("!!DEBUG!! b_contrarian SET!!")
            if price_diff < 0 and score > predict_accuracy and float(current_price) < float(price_prediction):
                return trade_type_buy_short(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark)
            elif float(price_diff) > float(limitDistance_value) and score > predict_accuracy and float(current_price) > float(price_prediction):
                    #!!!!Above Predicted Target!!!!
                    # Tight limit (Take Profit)
                return trade_type_buy_short(shortPositionPercentage, longPositionPercentage,  Client_Sentiment_Check, High_Trend_Watermark)
                # limitDistance_value = "2"
            else:
                print("!!DEBUG!! NO CRITERIA YET - SLEEPING!!: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                systime.sleep(Prediction_Wait_Timer)
                print("!!DEBUG!! NO CRITERIA!! " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))

        else:  # b_contrarian == False:
            #print ("!!DEBUG!! b_contrarian is false!! :- You are following the client sentiment")
            if price_diff < 0 and score > predict_accuracy and float(current_price) < float(price_prediction):
                return trade_type_buy_long(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark)
            elif float(price_diff) > float(limitDistance_value) and score > predict_accuracy and float(current_price) > float(price_prediction):
                #!!!!Above Predicted Target!!!!
                # Tight limit (Take Profit)
                return trade_type_buy_long(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark)
            else:
                print("!!DEBUG!! NO CRITERIA YET - SLEEPING!!: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                systime.sleep(Prediction_Wait_Timer)
                print("!!DEBUG!! NO CRITERIA!! " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
    else:
        # no client sentiment, we only care about price
        #print ("price_diff:{} score:{} current_price:{} limitDistance_value:{} predict_accuracy:{} price_prediction:{}".format(price_diff, score, current_price, limitDistance_value, predict_accuracy, price_prediction))
        if score < predict_accuracy:
            return None
        elif price_prediction > current_price:
            return "BUY"
        else:
            return "SELL"

    return None


for times_round_loop in range(1, 9999):

    #*******************************************************************
    Start_loop_time = time()

    # Watch market for opportunity.
    watcher = MarketWatcher(client=igclient, epics=list(epics), change_range=(0.48, 1.9), spread_range=(0.0, 2.0))
    watcher.watch()
    epic_id = watcher.epic
    current_price = watcher.bid

    price_compare = "bid"

    if use_clientsentiment:
        MARKET_ID = get_market_id(epic_id)
        # Good ol "Crowd-sourcing" check.....
        d = igclient.clientsentiment(MARKET_ID)

        longPositionPercentage = float(d['longPositionPercentage'])
        shortPositionPercentage = float(d['shortPositionPercentage'])

        # we can check this right now! before pulling in all the market data
        EARLY_CHECK = None
        if b_contrarian == True:
            EARLY_CHECK = trade_type_buy_short(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark)
        else:
            EARLY_CHECK = trade_type_buy_long(shortPositionPercentage, longPositionPercentage, Client_Sentiment_Check, High_Trend_Watermark)

        if EARLY_CHECK is None:
            # no point pulling in market data (right now), we'll reject this later on anyway
            continue

    DIRECTION_TO_TRADE = None
    while DIRECTION_TO_TRADE is None:
        print("!!Internal Notes only - Top of Loop!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
        # Your input data, X and Y are lists (or Numpy Arrays)
        # THIS IS YOUR TRAINING DATA
        x = []  # This is Low Price, Volume
        y = []  # This is High Price

        if high_resolution:
            d = igclient.prices(epic_id, 'DAY/30')

            # I only need this API call for real world values
            remaining_allowance = d['allowance']['remainingAllowance']
            reset_time = humanize_time(int(d['allowance']['allowanceExpiry']))

            print("-----------------DEBUG-----------------")
            print("Remaining API Calls left : " + str(remaining_allowance))
            print("Time to API Key reset : " + str(reset_time))
            print("-----------------DEBUG-----------------")

            # day_moving_avg_30 = []
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
                # x is Low Price and Volume
                y.append(float(high_price))
                # y = High Prices
                # price_change_on_day = close_price - open_price
                #print ("DEBUG price_change_day : " + str(price_change_on_day))
                # day_moving_avg_30.append(float(price_change_on_day))

            # avg_price_movement_day = np.mean(day_moving_avg_30)
            # print ("-----------------DEBUG-----------------")
            # print ("DEBUG average movement over last 30 days : " + str(avg_price_movement_day))
            # print ("-----------------DEBUG-----------------")

        ############################################################

        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        if high_resolution:
            resolutions = ['HOUR_4/30', 'HOUR_3/30', 'HOUR_2/30', 'HOUR/30']
        else:
            resolutions = ['HOUR_4/30']
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
                    # x is Low Price and Volume
                    y.append(float(high_price))
                    # y = High Prices

        ###################################################################################

        # Cut down on API Calls by using this again!

        price_ranges = []
        closing_prices = []
        TR_prices = []

        for count, i in enumerate(d['prices']):
            if count == 0:
                # First time round loop cannot get previous
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
                    print("No data for {e}.{r}".format(e=epic_id, r=resolution))
                    # sys.exit(1)
                price_ranges.append(price_range)
                TR = max(high_price-low_price, abs(high_price-prev_close), abs(low_price-prev_close))
                #print (TR)
                TR_prices.append(TR)

        max_range = max(TR_prices)
        low_range = min(TR_prices)
        print("stopDistance_value for " + str(epic_id) + " will bet set at " + str(float(max_range)))
        print("limitDistance_value for " + str(epic_id) + " will bet set at " + str(float(low_range)))
        if low_range > 10:
            print("!!DEBUG!! WARNING - Take Profit over high value, Might take a while for this trade!!")

        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH)
        if high_resolution:
            resolutions = ['MINUTE_30/30', 'MINUTE_15/30', 'MINUTE_10/30', 'MINUTE_5/30', 'MINUTE_3/30', 'MINUTE_2/30', 'MINUTE/30']
        else:
            resolutions = ['MINUTE_30/30', 'MINUTE/30']
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
                # x is Low Price and Volume
                y.append(float(high_price))
                # y = High Prices

        ###################################################################################
        ###################################################################################

        if high_resolution:
            d = igclient.prices(epic_id, 'DAY/1')

            for i in d['prices']:
                low_price = i['lowPrice'][price_compare]
                volume = i['lastTradedVolume']
        else:
            res = fetch_day_highlow(epic_id)
            low_price = float(res['values']['DAY_LOW'])
            volume = float(res['values']['LTV'])  # this is (now) an hourly volume - will that be an issue?

        #####################################################################
        #########################PREDICTION CODE#############################
        #####################################################################

        x = np.asarray(x)
        y = np.asarray(y)
        # Initialize the model then train it on the data
        genius_regression_model = LinearRegression()
        genius_regression_model.fit(x, y)
        # Predict the corresponding value of Y for X
        pred_ict = [low_price, volume]
        pred_ict = np.asarray(pred_ict)  # To Numpy Array, hacky but good!!
        pred_ict = pred_ict.reshape(1, -1)
        price_prediction = genius_regression_model.predict(pred_ict)
        print("PRICE PREDICTION FOR PRICE " + epic_id + " IS : " + str(price_prediction))

        score = genius_regression_model.score(x, y)
        predictions = {'intercept': genius_regression_model.intercept_, 'coefficient': genius_regression_model.coef_, 'current_price': current_price, 'predicted_value': price_prediction, 'accuracy': score}
        print("-----------------DEBUG-----------------")
        print(score)
        print(predictions)
        print("-----------------DEBUG-----------------")

        price_diff = current_price - price_prediction

        # limitDistance_value = int((low_range/2) * score) #  vary according to our certainty
        limitDistance_value = int(price_diff * score * float(config['Trade']['greed']))  # vary according to certainty and greed
        if float(limitDistance_value) < 0:
            limitDistance_value = limitDistance_value * -1

        print("!!DEBUG current_price={}, price_diff={}, target={}".format(current_price, price_diff, limitDistance_value))

        # Fixing a weird bug with some exotic fx, Where the prediction is 0.
        # Fixing a weird bug with some exotic fx, Where the prediction is 0.
#        if int(limitDistance_value) <= 0:
#            limitDistance_value = "1"

        #stopDistance_value = int(max_range)
        # NOTE Sometimes IG Index want a massive stop loss for Guaranteed, Either don't use Guaranteed or "sell at market" with Artificial Stop loss
        # MUST NOTE :- IF THIS PRICE IS - i.e NOT HIT TARGET YET, CONVERSELY IF THIS PRICE IS POSITIVE IT IS ALREADY ABOVE PREDICTION!!!
        #print ("TRUE GUARANTEED STOP LOSS DISTANCE WILL BE SET AT : " + str(stopDistance_value))
        #print ("Price Difference Away (Point's) : " + str(price_diff))

        ################################################################
        #########################ORDER CODE#############################
        ################################################################

        ################################################################
        #############Predict Accuracy isn't that great. ################
        ################################################################
        Prediction_Wait_Timer = int(TIME_WAIT_MULTIPLIER)  # Wait

        if float(score) < float(predict_accuracy):
            # NOT ACCURATE ENOUGH (YET)
            print("!!DEBUG!! : " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
            print("!!DEBUG!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
            systime.sleep(Prediction_Wait_Timer)
            print("!!DEBUG!! Prediction Wait Algo: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
            break

        # Three things, Price difference is less than target, Accuracy is OK, Current Price is less than Price Prediction
        # Added a fourth thing "contrarian indicator"

        print("price_diff:{} score:{} current_price:{} limitDistance_value:{} predict_accuracy:{} price_prediction:{}".format(price_diff, score, current_price, limitDistance_value, predict_accuracy, price_prediction))
        DIRECTION_TO_TRADE = determine_trade_direction()

    # LET'S DO THIS
    if DIRECTION_TO_TRADE == 'SELL':
        DIRECTION_TO_CLOSE = 'BUY'
        DIRECTION_TO_COMPARE = 'offer'
    else:
        DIRECTION_TO_CLOSE = 'SELL'
        DIRECTION_TO_COMPARE = 'bid'
        #limitDistance_value *= -1

    data = {"direction": DIRECTION_TO_TRADE, "epic": epic_id, "limitDistance": str(limitDistance_value), "orderType": orderType_value, "size": size_value, "expiry": expiry_value, "guaranteedStop": guaranteedStop_value, "currencyCode": currencyCode_value, "forceOpen": forceOpen_value, "stopDistance": stopDistance_value}
    data = igclient.handleDealingRules(data)

    # igclient.setdebug(True)
    d = igclient.positions_otc(data)

    deal_ref = d['dealReference']
    systime.sleep(2)
    # MAKE AN ORDER

    # CONFIRM MARKET ORDER
    d = igclient.confirms(deal_ref)
    # igclient.setdebug(False)
    DEAL_ID = d['dealId']
    print("DEAL ID : {} - {} - {}".format(str(d['dealId']), d['dealStatus'], d['reason']))

    #######################################################################################
    # This gets triggered if IG want a daft amount in your account for the margin, More than you specified initially. This happens sometimes... deal with it!
    # This is fine, Whilst it is a bit hacky basically start over again.
    #######################################################################################
    if str(d['reason']) == "ATTACHED_ORDER_LEVEL_ERROR" or str(d['reason']) == "MINIMUM_ORDER_SIZE_ERROR" or str(d['reason']) == "INSUFFICIENT_FUNDS" or str(d['reason']) == "MARKET_OFFLINE":
        print("!!DEBUG!! Not enough wonga in your account for this type of trade!!, Try again!!")
        continue

    # the trade will only break even once the price of the asset being traded has surpassed the sell price (for long trades) or buy price (for short trades).
    ##########################################
    ##########READ IN INITIAL PROFIT##########
    ##########################################

    # let account stream provide updates, and let limit close it (for now)
    # TODO: monitor trades with stream thread or waste of a stream?
    systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))  # Obligatory Wait before doing next order
    open_positions = igclient.positions()
    continue

    igclient.setdebug(True)
    d = igclient.positions(DEAL_ID)
    igclient.setdebug(False)

    if DIRECTION_TO_TRADE == "SELL":
        PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
    else:
        PROFIT_OR_LOSS = float(d['market'][DIRECTION_TO_COMPARE] - float(d['position']['openLevel']))
    PROFIT_OR_LOSS = PROFIT_OR_LOSS * float(size_value)
    print("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS))

    ##########################################
    #####KEEP READING IN FOR PROFIT###########
    ##########################################
    try:
        # while PROFIT_OR_LOSS < float(limitDistance_value):
        while PROFIT_OR_LOSS < float(float(limitDistance_value) * float(size_value)) - 1:  # Take something from the market, Before Take Profit.
            elapsed_time = round((time() - Start_loop_time), 1)

            igclient.json = False
            auth_r = igclient.positions(DEAL_ID)
            igclient.json = True
            d = json.loads(auth_r.text)

            while not int(auth_r.status_code) == 200:
                if int(auth_r.status_code) == 400 or int(auth_r.status_code) == 404:
                    break
                    # This is a good thing!! It means that It cannot find the Deal ID, Your take profit has been hit.

                # Cannot read from API, Wait and try again
                # Give the Internet/IG 30s to sort it's shit out and try again
                systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))
                print("-----------------DEBUG-----------------")
                print("HTTP API ERROR!! Please check your Internet connection and Try again...")
                print("Check Ping and Latency between you and IG Index Servers")
                # print(auth_r.status_code)
                # print(auth_r.reason)
                # print (auth_r.text)
                print("-----------------DEBUG-----------------")
                # Got some "basic" error checking after all
                d = igclient.positions(DEAL_ID)

            if DIRECTION_TO_TRADE == "SELL":
                PROFIT_OR_LOSS = float(d['position']['openLevel']) - float(d['market'][DIRECTION_TO_COMPARE])
            else:
                PROFIT_OR_LOSS = float(d['market'][DIRECTION_TO_COMPARE] - float(d['position']['openLevel']))
            PROFIT_OR_LOSS = float(PROFIT_OR_LOSS * float(size_value))
            print("Deal Number : " + str(times_round_loop) + " Profit/Loss : " + str(PROFIT_OR_LOSS) + " Order Time : " + str(humanize_time(elapsed_time)))
            systime.sleep(2)  # Don't be too keen to read price

            ARTIFICIAL_STOP_LOSS = float(max_range) * float(size_value)
            if ARTIFICIAL_STOP_LOSS > 100:
                print("!!!!WARNING!!!! STOP LOSS MIGHT BE TOO HIGH :- Current Value is " + str(ARTIFICIAL_STOP_LOSS))
            ARTIFICIAL_STOP_LOSS = ARTIFICIAL_STOP_LOSS * -1  # Make Negative, DO NOT REMOVE!!

            def close_trade():
                SIZE = size_value
                ORDER_TYPE = orderType_value
                data = {"dealId": DEAL_ID, "direction": DIRECTION_TO_CLOSE, "size": SIZE, "orderType": ORDER_TYPE}
                igclient.setdebug(True)
                auth_r = igclient.positions_otc_close(data)
                igclient.setdebug(False)

            if PROFIT_OR_LOSS < ARTIFICIAL_STOP_LOSS:
                # CLOSE TRADE/GTFO
                print("!!!WARNING!!! POTENTIAL DIRECTION CHANGE!!")
                close_trade()
                print("!!DEBUG TIME!! Direction Change Wait: " + str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")))
                Prediction_Wait_Timer = 900  # 15Mins
                systime.sleep(Prediction_Wait_Timer)

            if elapsed_time > 12600:
                print("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER TIME")
                if float(PROFIT_OR_LOSS) > 0:
                    print("!!DEBUG!! TRADE OPEN OVER TIME AND IN PROFIT")
                    close_trade()
                    print("!!DEBUG!! : TIME AND IN PROFIT :- CLOSED")

            if elapsed_time > 18000:
                print("!!DEBUG!! WARNING: TRADE HAS BEEN OPEN OVER 5 HOURS")
                if -9 <= float(PROFIT_OR_LOSS) <= 0:
                    print("!!DEBUG!! TRADE OPEN OVER 5 HOURS, CUT LOSSES")
                    close_trade()
                    print("DEBUG : TIME AND IN PROFIT :- CLOSED")

            if (float(PROFIT_OR_LOSS) > 9 and elapsed_time < 2700) or (float(PROFIT_OR_LOSS) > 20 and elapsed_time > 7200):
                close_trade()
                print("DEBUG : TIME AND IN PROFIT :- CLOSED")

    except Exception as e:
        print(e)  # Yeah, I know now.
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("ERROR : ORDER MIGHT NOT BE OPEN FOR WHATEVER REASON")
        # WOAH CALM DOWN! WAIT .... STOP LOSS MIGHT HAVE BEEN HIT (Or take Profit)
        systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))
        pass

        # systime.sleep(1)

    if PROFIT_OR_LOSS > 0:
        profitable_trade_count = int(profitable_trade_count) + 1
        print("DEBUG : ASSUME PROFIT!! Profitable Trade Count " + str(profitable_trade_count))
        SIZE = size_value
        ORDER_TYPE = orderType_value

        # CLOSE TRADE
        data = {"dealId": DEAL_ID, "direction": DIRECTION_TO_CLOSE, "size": SIZE, "orderType": ORDER_TYPE}
        igclient.setdebug(True)
        auth_r = igclient.positions_otc_close(data)
        igclient.setdebug(False)

        # #CONFIRM CLOSE - FUTURE
        # d = igclient.confirms(deal_ref)
        # DEAL_ID = d['dealId']
        # print("DEAL ID : " + str(d['dealId']))
        # print(d['dealStatus'])
        # print(d['reason'])

        systime.sleep(random.randint(1, TIME_WAIT_MULTIPLIER))  # Obligatory Wait before doing next order
