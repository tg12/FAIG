from igclient import IGClient
import igstream

import random

def on_item_update(item_update):
	print(item_update)

class API(IGClient):
	def __init__(self):
		super().__init__()

	def init(self):
		d = super().session()
		self.igstreamclient = igstream.IGStream(igclient=self, loginresponse=d)

		subscription = igstream.Subscription(
			mode="DISTINCT",
			items=["TRADE:"+str(self.accountId)],
			fields=["OPU"])

		self.igstreamclient.subscribe(subscription=subscription, listener=on_item_update)
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
			self.market_ids[epic_id] = d['instrument']['marketId']
			MARKET_ID = self.market_ids[epic_id]
		return MARKET_ID

	def fetch_day_highlow(self, epic_id):
		subscription = igstream.Subscription(
			mode="MERGE",
			items=["CHART:{}:HOUR".format(epic_id)],
			fields=["LTV", "DAY_LOW", "DAY_HIGH"]
		)
		res = self.igstreamclient.fetch_one(subscription)
		return res

	def fetch_current_price(self, epic_id):
		try:
			subscription = igstream.Subscription(
				mode="MERGE",
				items=["MARKET:{}".format(epic_id)],
				fields=["MID_OPEN","HIGH","LOW","CHANGE","CHANGE_PCT","UPDATE_TIME","MARKET_DELAY","MARKET_STATE","BID","OFFER"]
			)
			res = self.igstreamclient.fetch_one(subscription)
		except IndexError:
			# fall back to non-stream version
			res = super().markets(epic_id)
			res['values'] = {}
			res['values']['BID'] = res['snapshot']['bid']
			res['values']['OFFER'] = res['snapshot']['offer']
			res['values']['CHANGE'] = res['snapshot']['netChange']
			res['values']['CHANGE_PCT'] = res['snapshot']['percentageChange']
		return res

	def find_next_trade(self, epic_ids):
		while(1):
			random.shuffle(epic_ids)
			for epic_id in epic_ids:
				print("!!DEBUG!! : " + str(epic_id), end='')
				if epic_id in map(lambda x: x['market']['epic'], self.open_positions['positions']):
					print( " already have an open position here")
					continue
				#systime.sleep(2) # we only get 30 API calls per minute :( but streaming doesn't count, so no sleep

				res = self.fetch_current_price(epic_id)
				res['values']['EPIC'] = epic_id

				current_price = res['values']['BID']
				Price_Change_Day = res['values']['CHANGE']
				
				if res['values']['CHANGE_PCT'] is None:
					Price_Change_Day_percent = 0.0
				else:
					Price_Change_Day_percent = float(res['values']['CHANGE_PCT'])

				Price_Change_Day_percent_h = float(self.config['Trade']['Price_Change_Day_percent_high'])
				Price_Change_Day_percent_l = float(self.config['Trade']['Price_Change_Day_percent_low'])

				if (Price_Change_Day_percent_h > Price_Change_Day_percent > Price_Change_Day_percent_l) or ((Price_Change_Day_percent_h * -1) < Price_Change_Day_percent < (Price_Change_Day_percent_l * -1)): 
						print (" Day Price Change {}% ".format(str(Price_Change_Day_percent)), end='')
						bid_price = res['values']['BID']
						ask_price = res['values']['OFFER']
						spread = float(bid_price) - float(ask_price)

						if eval(self.config['Trade']['use_max_spread']) == True:
							max_permitted_spread = float(self.config['Trade']['max_spread'])
						else:
							max_permitted_spread = float(epics[epic_id]['minspread'] * float(self.config['Trade']['spread_multiplier']) * -1)

						#if spread is less than -2, It's too big
						if float(spread) > max_permitted_spread:
							print (":- GOOD SPREAD {0:.2f}>{1:.2f}".format(spread,max_permitted_spread), end="\n", flush=True)
							return res
						else:
							print (":- spread not ok {0:.2f}<={1:.2f}".format(spread,max_permitted_spread), end="\n", flush=True)
				else:
					print(": !Price change {}%".format(Price_Change_Day_percent), end="\n", flush=True) 

			print ("sleeping for 30s, since we've hit the end of the epic list")
			systime.sleep(30) # that's all of them
