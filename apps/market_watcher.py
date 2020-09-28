"""This is to check is price change is within required range."""
import random
from time import sleep
import logging

logging.basicConfig(level="INFO", format="%(asctime)s %(message)s")


class MarketWatcher:
    """

    This is an observer of market and report when certain criteria meet.

    There are 2 types of information to observe.
    1) When absolute price change is within range.
    2) When spread is within range.

    """

    ok = False  # Whether price changes obey rules.
    client = None  # IG client
    epics = []  # List of epic IDs.
    epic = None  # Current epic ID.
    # Market data.
    market_id = None
    current_price = None
    price_change = None
    percent_change = None
    bid = None
    ask = None
    # Range of price changes and spread to consider trading.
    min_change = None
    max_change = None
    min_spread = None
    max_spread = None

    def __init__(self,
                 client,
                 epics,
                 change_range=(0.48, 1.9),
                 spread_range=(0.0, 2.0)):

        assert isinstance(epics, list)

        def is_valid_range(x):
            assert isinstance(x, (tuple, list))
            assert all([isinstance(i, float) and i >= 0 for i in x])
            return True

        assert is_valid_range(change_range)
        assert is_valid_range(spread_range)

        self.client = client
        self.epics = epics
        self.min_change = min(change_range)
        self.max_change = max(change_range)
        self.min_spread = min(spread_range)
        self.max_spread = max(spread_range)

    def watch(self):
        """This is to keep updating the market data until a valid price movement is observed."""
        while not self.ok:
            self.epic = self.__get_epic_id()
            self.__update_market_data()
            if self.__price_change_is_in_range() and self.__spread_is_in_range(
            ):
                self.ok = True
                self.__log("Hit")
            else:
                self.ok = False
                self.__log("Pass")
                sleep(2)  # Wait for a while before refresh.

    def __get_epic_id(self):
        """This is to get a random epic in list."""
        random.shuffle(self.epics)
        epic = random.choice(self.epics)
        return epic

    def __update_market_data(self):
        """This is to update market data."""
        i = self.client.markets(self.epic)
        instrument, snapshot = i["instrument"], i["snapshot"]

        self.market_id = instrument["marketId"]
        self.current_price = snapshot["bid"]
        self.price_change = snapshot["netChange"]

        def to_float(x):
            if x is None:
                return 0
            else:
                return float(x)

        # Convert percentage change to float.
        self.percent_change = to_float(snapshot["percentageChange"])

        #       # Convert bid ask prices to float.
        self.bid = to_float(snapshot["bid"])
        self.ask = to_float(snapshot["offer"])

        # Calculate spread.
        self.spread = self.ask - self.bid
        assert self.spread >= 0

    def __price_change_is_in_range(self):
        """This is to check if price change is in range."""
        return self.min_change < abs(self.percent_change) < self.max_change

    def __spread_is_in_range(self):
        """

        This is to check if spread is in range.

        Examples
        Spread is -30, That is too big, In-fact way too big.
        Spread is -1.7, This is not too bad, We can trade on this reasonably well.
        Spread is 0.8. This is considered a tight spread.

        """
        return self.min_spread < self.data["spread"] < self.max_spread

    def __log(self, msg):
        logging.info(
            "epic: {epic}, price: {bid}/{ask}, spread: {spread}, price change: {price_change}, percentage change: {percent_change} -> {msg}"
            .format(
                msg=msg,
                epic=self.epic,
                bid=int(self.bid),
                ask=int(self.ask),
                spread=int(self.spread),
                price_change=round(self.price_change, 2),
                percent_change=round(self.percent_change, 2),
            ))
