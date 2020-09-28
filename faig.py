# IF YOU FOUND THIS USEFUL, Please Donate some Bitcoin ....
# 1FWt366i5PdrxCC6ydyhD8iywUHQ2C7BWC

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from ig import API
from lib.prediction import Prediction

api = API()

while(True):
    d = api.find_next_trade()

    epic_id = d['values']['EPIC']

    prediction = Prediction(api.config)
    prediction.epic_id = epic_id
    prediction.current_price = float(d['values']['BID'])
    prediction.set_marketdata(api.clientsentiment(epic_id))
    if prediction.quick_check(
    ) is None:  # no point pulling in market data (right now), we'll reject this later on anyway
        continue  # find a different trade

    if api.config['Trade']['algorithm'] == 'LinearRegression':
        (x, y) = api.fetch_lg_prices(epic_id)
        (high_price, low_price) = api.fetch_lg_highlow(epic_id)

        prediction.linear_regression(
            x=x, y=y, high_price=high_price, low_price=low_price)
    else:
        sys.exit(
            'Trading Algorithm: {} not found'.format(
                api.config['Trade']['algorithm']))

    if prediction.direction_to_trade is None:
        print ("!!DEBUG!! Literally NO decent trade direction could be determined")
        continue

    api.placeOrder(prediction)
    continue
