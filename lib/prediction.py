class Prediction(object):

	def __init__(self, config):
		self.config = config
		self.predict_accuracy = float(config['Trade']['predict_accuracy'])
		self.use_clientsentiment = eval(config['Trade']['use_clientsentiment'])
		self.clientsentiment_contrarian = eval(config['Trade']['clientsentiment_contrarian'])
		self.clientsentiment_value = float(config['Trade']['clientsentiment_value'])
		self.hightrend_watermark = float(config['Trade']['hightrend_watermark'])
		self.caution = float(config['Trade']['caution'])
		self.limitDistance_value = "4"

	def set_marketdata(self, market_data):
		self.longPositionPercentage = float(market_data['longPositionPercentage'])
		self.shortPositionPercentage = float(market_data['shortPositionPercentage'])		


	def quick_check(self):
		check = None
		if self.use_clientsentiment:
			check = self.trade_type()

		return check


	def trade_type(self):
		if self.shortPositionPercentage > self.longPositionPercentage and self.shortPositionPercentage >= self.clientsentiment_value:
				return "SELL"
		elif self.longPositionPercentage > self.shortPositionPercentage and self.longPositionPercentage >= self.clientsentiment_value:
				return "BUY"
		elif self.longPositionPercentage >= self.hightrend_watermark:
				return "BUY"
		elif self.shortPositionPercentage >= self.hightrend_watermark:
				return "SELL"
		else:
				print ("!!DEBUG No Trade This time")
				print ("!!DEBUG shortPositionPercentage:{} longPositionPercentage:{} clientsentiment_value:{} hightrend_watermark:{}".format(self.shortPositionPercentage, self.longPositionPercentage, self.clientsentiment_value, self.hightrend_watermark))
				return None


	def determine_trade_direction(self, score, current_price, price_prediction):

		price_diff = float(current_price - price_prediction)

		print ("price_diff:{} score:{} current_price:{} limitDistance_value:{} predict_accuracy:{} price_prediction:{}".format(price_diff, score, current_price, self.limitDistance_value, self.predict_accuracy, price_prediction))

		if self.use_clientsentiment:

			direction_to_return = None

			# TODO clean this up! 
			# there's a LOT of replication, duplicated conditions, and i'm not 100% that the logic is correct, but may be replacing anyway

			if score >= self.predict_accuracy:
					direction_to_return = self.trade_type()
			elif current_price < price_prediction and self.shortPositionPercentage > self.longPositionPercentage:
					print ("!!DEBUG!! TAKE SHORT TRADE ON RUBBISH PREDICTION!! ")
					self.limitDistance_value = int(price_diff * score * self.caution) # vary according to certainty and greed
					if self.limitDistance_value == 0:
							return None 
					#####################################################################    
					if self.limitDistance_value < 0:
						self.limitDistance_value *= -1
					print ("Cautious trade: " + str(self.limitDistance_value))
					return "BUY"
			elif current_price > price_prediction and self.shortPositionPercentage < self.longPositionPercentage:
					print ("!!DEBUG!! TAKE SHORT TRADE ON RUBBISH PREDICTION!! ")
					self.limitDistance_value = int(price_diff * score * self.caution) # vary according to certainty and greed
					if self.limitDistance_value == 0:
						return None 
					#####################################################################    
					if self.limitDistance_value < 0:
						self.limitDistance_value *= -1
					print ("Cautious trade: " + str(self.limitDistance_value))
					return "SELL"
		
			if self.clientsentiment_contrarian == True:
					# reverse position to go against sentiment
					if direction_to_return == "SELL":
							return "BUY"
					elif direction_to_return == "BUY":
							return "SELL"

			return direction_to_return

		else:
			# no client sentiment, we only care about price
			if score < self.predict_accuracy:
				return None
			elif price_prediction > current_price:
				return "BUY"
			else:
				return "SELL"

		return None
