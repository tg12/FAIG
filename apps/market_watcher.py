'''This is to check is price change is within required range.'''
import random
from time import sleep
import logging

logging.basicConfig(level='INFO', format='%(asctime)s %(message)s')


class MarketWatcher():
    '''

    This is an observer of market and report when certain criteria meet.

    There are 2 types of information to observe.
    1) When absolute price change is within range.
    2) When spread is smaller than a limit.

    '''
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
    min_change = 0.48
    max_change = 1.9
    max_spread = 2

    def __init__(self, client, epics):
        assert isinstance(epics, list)
        self.client = client
        self.epics = epics

    def watch(self):
        '''This is to keep updating the market data until a valid price movement is observed.'''
        while not self.ok:
            self.epic = self.__get_random_epic_id()
            self.__update_market_data()
            if self.__price_change_is_in_range():
                self.__do_if_price_change_in_range()
            else:
                self.__do_if_price_change_outside_range()

    def __get_random_epic_id(self):
        '''

        This is to get random epic ID. It must be different from last traded epic ID.

        If previous traded epic ID os not provided, same epic may be chosen.

        '''
        random.shuffle(self.epics)
        epic = random.choice(self.epics)
        sleep(2)
        return epic

    def __update_market_data(self):
        '''This is to update market data.'''
        i = self.client.markets(self.epic)
        instrument, snapshot = i['instrument'], i['snapshot']

        self.market_id = instrument['marketId']
        self.current_price = snapshot['bid']
        self.price_change = snapshot['netChange']

        def to_float(x):
            if x is None:
                return 0
            else:
                return float(x)

        # Convert percentage change to float. It could be None.
        if snapshot['percentageChange'] is None:
            self.percent_change = 0
        else:
            self.percent_change = to_float(snapshot['percentageChange'])

#       # Convert bid ask prices to float.
        self.bid = to_float(snapshot['bid'])
        self.ask = to_float(snapshot['offer'])

        # Calculate spread.
        self.spread = self.ask - self.bid

    def __price_change_is_in_range(self):
        '''This is to check if price change is in range.'''
        x = self.percent_change
        return (self.min_change < abs(x) < self.max_change)

    def __do_if_price_change_in_range(self):
        '''

        This is to check if spread is in range.

        Examples
        Spread is -30, That is too big, In-fact way too big.
        Spread is -1.7, This is not too bad, We can trade on this reasonably well.
        Spread is 0.8. This is considered a tight spread.

        '''
        if self.data["spread"] > self.max_spread:
            self.__do_if_spread_larger_than_limit()
        elif self.spread < self.max_spread:
            self.__do_if_spread_smaller_than_limit()
        else:
            self.__do_if_spread_equal_limit()

    def __do_if_spread_larger_than_limit(self):
        self.__log('Pass')
        self.ok = False
        systime.sleep(2)

    def __do_if_spread_smaller_than_limit(self):
        self.__log('Hit')
        self.ok = True

    def __do_if_spread_equal_limit(self):
        self.__log('Pass')
        self.ok = False

    def __do_if_price_change_outside_range(self):
        self.__log('Pass')

    def __log(self, msg):
        logging.info('epic: {epic}, price: {bid}/{ask}, spread: {spread}, price change: {price_change}, percentage change: {percent_change} -> {msg}'.format(msg=msg, epic=self.epic, bid=int(self.bid), ask=int(self.ask), spread=int(self.spread), price_change=round(self.price_change, 2), percent_change=round(self.percent_change, 2)))
