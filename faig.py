'''THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR ANYONE
DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR OTHER LIABILITY,
WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

# Bitcoin Cash (BCH)   qpz32c4lg7x7lnk9jg6qg7s4uavdce89myax5v5nuk
# Ether (ETH) -        0x843d3DEC2A4705BD4f45F674F641cE2D0022c9FB
# Litecoin (LTC) -     Lfk5y4F7KZa9oRxpazETwjQnHszEPvqPvu
# Bitcoin (BTC) -      34L8qWiQyKr8k4TnHDacfjbaSqQASbBtTd



# IF YOU FOUND THIS USEFUL, Please Donate some Bitcoin ....
# 1FWt366i5PdrxCC6ydyhD8iywUHQ2C7BWC

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from ig import API
from lib.prediction import Prediction

api = API()

while True:
    d = api.find_next_trade()

    epic_id = d["values"]["EPIC"]

    prediction = Prediction(api.config)
    prediction.epic_id = epic_id
    prediction.current_price = float(d["values"]["BID"])
    prediction.set_marketdata(api.clientsentiment(epic_id))
    if (
            prediction.quick_check() is None
    ):  # no point pulling in market data (right now), we'll reject this later on anyway
        continue  # find a different trade

    if api.config["Trade"]["algorithm"] == "LinearRegression":
        (x, y) = api.fetch_lg_prices(epic_id)
        (high_price, low_price) = api.fetch_lg_highlow(epic_id)

        prediction.linear_regression(x=x,
                                     y=y,
                                     high_price=high_price,
                                     low_price=low_price)
    else:
        sys.exit("Trading Algorithm: {} not found".format(
            api.config["Trade"]["algorithm"]))

    if prediction.direction_to_trade is None:
        print(
            "!!DEBUG!! Literally NO decent trade direction could be determined")
        continue

    api.placeOrder(prediction)
    continue
