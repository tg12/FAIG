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

from igclient import IGClient
import igstream
import time as systime
import lib.util
import json

import random


def on_item_update(item_update):
    print(item_update)


class API(IGClient):
    def __init__(self):
        super().__init__()
        d = super().session()
        self.igstreamclient = igstream.IGStream(igclient=self, loginresponse=d)

        subscription = igstream.Subscription(
            mode="DISTINCT", items=["TRADE:" + str(self.accountId)], fields=["OPU"]
        )

        self.igstreamclient.subscribe(
            subscription=subscription, listener=on_item_update
        )
        self.market_ids = {}

        # get open positions
        self.open_positions = super().positions()

    def clientsentiment(self, epic_id):
        market_id = self.get_market_id(epic_id)
        return super().clientsentiment(market_id)

    def get_market_id(self, epic_id):
        try:
            MARKET_ID = self.market_ids[epic_id]
        except KeyError:
            # lookup and cache - these won't change
            d = super().markets(epic_id)
            self.market_ids[epic_id] = d["instrument"]["marketId"]
            MARKET_ID = self.market_ids[epic_id]
        return MARKET_ID

    def fetch_day_highlow(self, epic_id):
        subscription = igstream.Subscription(
            mode="MERGE",
            items=["CHART:{}:HOUR".format(epic_id)],
            fields=["LTV", "DAY_LOW", "DAY_HIGH"],
        )
        res = self.igstreamclient.fetch_one(subscription)
        return res

    def fetch_current_price(self, epic_id):
        try:
            subscription = igstream.Subscription(
                mode="MERGE",
                items=["MARKET:{}".format(epic_id)],
                fields=[
                    "MID_OPEN",
                    "HIGH",
                    "LOW",
                    "CHANGE",
                    "CHANGE_PCT",
                    "UPDATE_TIME",
                    "MARKET_DELAY",
                    "MARKET_STATE",
                    "BID",
                    "OFFER",
                ],
            )
            res = self.igstreamclient.fetch_one(subscription)
        except IndexError:
            # fall back to non-stream version
            res = super().markets(epic_id)
            res["values"] = {}
            res["values"]["BID"] = res["snapshot"]["bid"]
            res["values"]["OFFER"] = res["snapshot"]["offer"]
            res["values"]["CHANGE"] = res["snapshot"]["netChange"]
            res["values"]["CHANGE_PCT"] = res["snapshot"]["percentageChange"]
        return res

    def placeOrder(self, prediction):
        data = self.handleDealingRules(prediction.get_tradedata())

        d = self.positions_otc(data)
        try:
            deal_ref = d["dealReference"]
        except BaseException:
            return

        systime.sleep(2)
        # MAKE AN ORDER

        # CONFIRM MARKET ORDER
        d = self.confirms(deal_ref)
        print(
            "DEAL ID : {} - {} - {}".format(
                str(d["dealId"]), d["dealStatus"], d["reason"]
            )
        )

        if (
            str(d["reason"]) == "ATTACHED_ORDER_LEVEL_ERROR"
            or str(d["reason"]) == "MINIMUM_ORDER_SIZE_ERROR"
            or str(d["reason"]) == "INSUFFICIENT_FUNDS"
            or str(d["reason"]) == "MARKET_OFFLINE"
        ):
            print(
                "!!DEBUG!! Not enough wonga in your account for this type of trade!!, Try again!!"
            )
            return None

        # let account stream provide updates, and let limit close it (for now)
        # TODO: monitor trades with stream thread or waste of a stream?
        # Obligatory Wait before doing next order
        systime.sleep(random.randint(1, 60))
        self.open_positions = super().positions()

    def find_next_trade(self):
        """
        Find our next trade.

        1) suitable daily price change as %
        2) suitable spread as absolute or %
        """

        epics = json.loads(self.config["Epics"]["EPICS"])
        epic_ids = list(epics.keys())

        while 1:
            random.shuffle(epic_ids)
            for epic_id in epic_ids:
                print(str(epic_id), end="")
                if epic_id in map(
                    lambda x: x["market"]["epic"], self.open_positions["positions"]
                ):
                    print(" already have an open position here")
                    continue
                # systime.sleep(2) # we only get 30 API calls per minute :( but
                # streaming doesn't count, so no sleep

                res = self.fetch_current_price(epic_id)
                res["values"]["EPIC"] = epic_id

                current_price = res["values"]["BID"]
                Price_Change_Day = res["values"]["CHANGE"]

                if res["values"]["CHANGE_PCT"] is None:
                    Price_Change_Day_percent = 0.0
                else:
                    Price_Change_Day_percent = float(res["values"]["CHANGE_PCT"])

                Price_Change_Day_percent_h = float(
                    self.config["Trade"]["Price_Change_Day_percent_high"]
                )
                Price_Change_Day_percent_l = float(
                    self.config["Trade"]["Price_Change_Day_percent_low"]
                )

                if (
                    Price_Change_Day_percent_h
                    > Price_Change_Day_percent
                    > Price_Change_Day_percent_l
                ) or (
                    (Price_Change_Day_percent_h * -1)
                    < Price_Change_Day_percent
                    < (Price_Change_Day_percent_l * -1)
                ):
                    print(
                        " Day Price Change {}% ".format(str(Price_Change_Day_percent)),
                        end="",
                    )
                    bid_price = res["values"]["BID"]
                    ask_price = res["values"]["OFFER"]
                    spread = float(bid_price) - float(ask_price)

                    if eval(self.config["Trade"]["use_max_spread"]):
                        max_permitted_spread = float(self.config["Trade"]["max_spread"])
                    else:
                        max_permitted_spread = float(
                            epics[epic_id]["minspread"]
                            * float(self.config["Trade"]["spread_multiplier"])
                            * -1
                        )

                    # if spread is less than -2, It's too big
                    if float(spread) > max_permitted_spread:
                        print(
                            ":- GOOD SPREAD {0:.2f}>{1:.2f}".format(
                                spread, max_permitted_spread
                            ),
                            end="\n",
                            flush=True,
                        )
                        return res
                    else:
                        print(
                            ":- spread not ok {0:.2f}<={1:.2f}".format(
                                spread, max_permitted_spread
                            ),
                            end="\n",
                            flush=True,
                        )
                else:
                    print(
                        ": Price change {}%".format(Price_Change_Day_percent),
                        end="\n",
                        flush=True,
                    )

            print("sleeping for 30s, since we've hit the end of the epic list")
            systime.sleep(30)  # that's all of them
            # refresh in case a limit's been hit while we were sleeping
            self.open_positions = super().positions()

    def fetch_lg_prices(self, epic_id):
        """
        just....don't look

        This fetches the data required for Prediction.linear_regression
        This needs a LOT of work to expand/reuse/cleanup, but we might bin it, so...let's see
        """
        # Your input data, X and Y are lists (or Numpy Arrays)
        # THIS IS YOUR TRAINING DATA
        x = []  # This is Low Price, Volume
        y = []  # This is High Price

        # disabled - this doesn't actually do anything!
        # resolutions = ['DAY/14'] #This is just for the Average True Range, Base it on the last 14 days trading. (14 is the default in ATR)
        # for resolution in resolutions:
        # 	d = self.prices(epic_id, resolution)

        # print ("-----------------DEBUG-----------------")
        # print ("Remaining API Calls left : " + str(self.allowance['remainingAllowance']))
        # print ("Time to API Key reset : " + str(lib.util.humanize_time(int(self.allowance['allowanceExpiry']))))
        # print ("-----------------DEBUG-----------------")

        # price_ranges = []
        # closing_prices = []
        # TR_prices = []

        # for count, i in enumerate(d['prices']):
        # 		closePrice = i['closePrice']["bid"]
        # 		closing_prices.append(closePrice)
        # 		high_price = i['highPrice']["bid"]
        # 		low_price = i['lowPrice']["bid"]
        # 		if count == 0:
        # 				#First time round loop cannot get previous
        # 				price_range = float(high_price - closePrice)
        # 				price_ranges.append(price_range)
        # 		else:
        # 				prev_close = closing_prices[-1]
        # 				try:
        # 					price_range = float(high_price - closePrice)
        # 				except Exception:
        # 					print ("No data for {e}.{r}".format(e=epic_id, r=resolution))
        # 				price_ranges.append(price_range)
        # 				TR = max(high_price-low_price, abs(high_price-prev_close), abs(low_price-prev_close))
        # 				TR_prices.append(TR)

        # max_range = max(TR_prices)
        # # prediction.stopdistance = max_range
        # low_range = min(TR_prices)
        # if low_range > 10:
        # 		print ("!!DEBUG!! WARNING - Take Profit over high value, Might take a while for this trade!!")
        # systime.sleep(1.5)

        high_resolution = eval(self.config["Trade"]["high_resolution"])

        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_2, HOUR_4, DAY, WEEK, MONTH)
        # This is the high roller, For the price prediction.
        if high_resolution:
            resolutions = ["HOUR/5", "HOUR_2/5", "HOUR_3/5", "HOUR_4/5", "DAY/5"]
        else:
            resolutions = ["HOUR_4/5", "MINUTE_30/5"]
        for resolution in resolutions:
            d = self.prices(epic_id, resolution)

            for i in d["prices"]:
                tmp_list = []
                high_price = i["highPrice"]["bid"]
                low_price = i["lowPrice"]["bid"]
                close_price = i["closePrice"]["bid"]
                ############################################
                volume = i["lastTradedVolume"]
                # ---------------------------------
                tmp_list.append(float(high_price))
                tmp_list.append(float(low_price))
                x.append(tmp_list)
                y.append(float(close_price))

        return (x, y)

    def fetch_lg_highlow(self, epic_id):
        """
        This fetches the data required for Prediction.linear_regression
        """

        #######################################################################
        # Here we just need a value to predict the next one of.

        if eval(self.config["Trade"]["high_resolution"]):
            d = self.prices(epic_id, "DAY/1")

            for i in d["prices"]:
                high_price = i["highPrice"]["bid"]
                low_price = i["lowPrice"]["bid"]
        else:
            res = self.fetch_day_highlow(epic_id)
            low_price = float(res["values"]["DAY_LOW"])
            # this is (now) an hourly volume - will that be an issue?
            high_price = float(res["values"]["DAY_HIGH"])

        return (high_price, low_price)
