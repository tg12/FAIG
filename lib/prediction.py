#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import numpy as np


class Prediction(object):
    def __init__(self, config):
        self.config = config
        self.predict_accuracy = float(config["Trade"]["predict_accuracy"])
        self.use_clientsentiment = eval(config["Trade"]["use_clientsentiment"])
        self.clientsentiment_contrarian = eval(
            config["Trade"]["clientsentiment_contrarian"]
        )
        self.clientsentiment_value = float(config["Trade"]["clientsentiment_value"])
        self.hightrend_watermark = float(config["Trade"]["hightrend_watermark"])
        self.greed = float(config["Trade"]["greed"])

        self.epic_id = None
        self.current_price = None
        self.direction_to_trade = None
        self.stopdistance = float(config["Trade"]["stopDistance_value"])

        self.limitDistance = 4  # initial setting to be overridden
        self.ordertype = "MARKET"
        self.expirytype = "DFB"
        self.currencycode = "GBP"
        self.forceopen = True
        self.size = float(config["Trade"]["size"])

    def get_tradedata(self):
        return {
            "direction": self.direction_to_trade,
            "epic": self.epic_id,
            "limitDistance": str(self.limitDistance),
            "orderType": self.ordertype,
            "size": str(self.size),
            "expiry": self.expirytype,
            "currencyCode": self.currencycode,
            "forceOpen": self.forceopen,
            "stopDistance": str(self.stopdistance),
        }

    def set_marketdata(self, market_data):
        self.longPositionPercentage = float(market_data["longPositionPercentage"])
        self.shortPositionPercentage = float(market_data["shortPositionPercentage"])

    def quick_check(self):
        if self.use_clientsentiment:
            self.trade_type_by_sentiment()
        else:
            return True

        return self.direction_to_trade

    def trade_type_by_sentiment(self):
        if (
            self.shortPositionPercentage > self.longPositionPercentage
            and self.shortPositionPercentage >= self.clientsentiment_value
        ):
            self.direction_to_trade = "SELL"
        elif (
            self.longPositionPercentage > self.shortPositionPercentage
            and self.longPositionPercentage >= self.clientsentiment_value
        ):
            self.direction_to_trade = "BUY"
        elif self.shortPositionPercentage >= self.hightrend_watermark:
            self.direction_to_trade = "SELL"
        elif self.longPositionPercentage >= self.hightrend_watermark:
            self.direction_to_trade = "BUY"
        else:
            print("No Trade This time")
            print(
                "!!DEBUG shortPositionPercentage:{} longPositionPercentage:{} clientsentiment_value:{} hightrend_watermark:{}".format(
                    self.shortPositionPercentage,
                    self.longPositionPercentage,
                    self.clientsentiment_value,
                    self.hightrend_watermark,
                )
            )
            return None

    def trade_type_by_priceprediction(self):
        if self.price_prediction > self.current_price:
            self.direction_to_trade = "BUY"
        elif self.price_prediction < self.current_price:
            self.direction_to_trade = "SELL"
        else:
            self.direction_to_trade = None

    def reverse_direction(self):
        if self.direction_to_trade == "SELL":
            self.direction_to_trade = "BUY"
        elif self.direction_to_trade == "BUY":
            self.direction_to_trade = "SELL"

    def determine_trade_direction(self):

        current_price = self.current_price
        score = self.score
        price_prediction = self.price_prediction
        price_diff = float(current_price - price_prediction)

        print(
            "price_diff:{} score:{} current_price:{} limitDistance:{} predict_accuracy:{} price_prediction:{}".format(
                price_diff,
                score,
                current_price,
                self.limitDistance,
                self.predict_accuracy,
                price_prediction,
            )
        )

        self.limitDistance = round(
            price_diff * score * self.greed, 1
        )  # vary according to certainty and greed
        if self.limitDistance < 0:
            self.limitDistance *= -1
        if self.limitDistance == 0:
            # calculated risk isn't valid for a trade
            return None

        if score >= self.predict_accuracy:
            # highly accurate score - go with that
            self.trade_type_by_priceprediction()
        elif self.use_clientsentiment:
            self.trade_type_by_sentiment()
            if self.clientsentiment_contrarian:
                # reverse position to go against sentiment
                self.reverse_direction()
        else:
            pass

        return self.direction_to_trade

    def linear_regression(self, x, y, high_price, low_price):

        from sklearn.linear_model import LinearRegression

        x = np.asarray(x)
        y = np.asarray(y)

        # Initialize the model then train it on the data
        genius_regression_model = LinearRegression()
        genius_regression_model.fit(x, y)

        # Predict the corresponding value of Y for X
        pred_ict = [high_price, low_price]
        pred_ict = np.asarray(pred_ict)  # To Numpy Array, hacky but good!!
        pred_ict = pred_ict.reshape(1, -1)
        self.price_prediction = genius_regression_model.predict(pred_ict)
        print(
            "PRICE PREDICTION FOR PRICE "
            + self.epic_id
            + " IS : "
            + str(self.price_prediction)
        )

        self.score = genius_regression_model.score(x, y)
        predictions = {
            "intercept": genius_regression_model.intercept_,
            "coefficient": genius_regression_model.coef_,
            "current_price": self.current_price,
            "predicted_value": self.price_prediction,
            "accuracy": self.score,
        }
        print("-----------------DEBUG-----------------")
        print(predictions)
        print("-----------------DEBUG-----------------")
        self.determine_trade_direction()
