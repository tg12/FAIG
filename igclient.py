import configparser
import requests
import json

class IGClient(object):

  def __init__(self):
    self.loggedin = False
    self.json = True # return json or obj
    self.config = configparser.ConfigParser()
    self.config.read("default.conf")
    self.config.read("config.conf")
    self.auth = {}
    self.debug = False

    self.API_ENDPOINT = self.config['Config']['API_ENDPOINT']
    self.API_KEY = self.config['Config']['API_KEY']

  def setdebug(self, value=True):
    self.debug = value
    try:
            import http.client as http_client
    except ImportError:
            import httplib as http_client
    http_client.HTTPConnection.debuglevel = (0, 1)[ self.debug == True]

  def session(self, set_default=True):
    data = { "identifier": self.config['Auth']['USERNAME'], "password": self.config['Auth']['PASSWORD'] }

    self.headers = { 'Content-Type': 'application/json; charset=utf-8',
                     'Accept':       'application/json; charset=utf-8'
                   }

    self.headers.update({ 'X-IG-API-KEY': self.API_KEY })
    self.session_headers = self.headers.copy()
    self.session_headers.update({ 'Version': '2' })

    curr_json = self.json
    self.json = False # force off to let us use handlereq
    r = self._handlereq( requests.post(self.API_ENDPOINT + '/session', data=json.dumps(data), headers=self.session_headers) )
    self.json = curr_json # set it back
    headers_json = dict(r.headers)
    for h in ['CST', 'X-SECURITY-TOKEN']:
      self.auth[h] = headers_json[h]

    self.headers.update(self.auth)
    self.authenticated_headers = self.headers

    self.loggedin = True

    #GET ACCOUNTS
    d = self.accounts()

    for i in d['accounts']:
      if str(i['accountType']) == self.config['Config']['ACCOUNT_TYPE']:
        #print ("Spreadbet Account ID is : " + str(i['accountId']))
        self.accountId = str(i['accountId'])
        break

    if set_default:
        #SET SPREAD BET ACCOUNT AS DEFAULT
        self.update_session({"accountId":self.accountId,"defaultAccount": "True"})
        #ERROR about account ID been the same, Ignore! 

    return ((r, json.loads(r.text))[ self.json == True ])

  def _handlereq(self, r):
    if self.debug == True:
      try:
        print(r.text)
      except Exception:
        pass
    return ((r, json.loads(r.text))[ self.json == True ])

  def _authheadersfordelete(self):
    # WORKAROUND AS PER .... https://labs.ig.com/node/36
    delete_headers = self.authenticated_headers.copy()
    delete_headers.update({ '_method': "DELETE" })
    return delete_headers

  def accounts(self):
    return self._handlereq( requests.get(self.API_ENDPOINT + '/accounts', headers=self.authenticated_headers) )

  def update_session(self, data):
    return self._handlereq( requests.put(self.API_ENDPOINT + '/session', data=data, headers=self.authenticated_headers) )

  def markets(self, epic_id):
    return self._handlereq( requests.get(self.API_ENDPOINT + '/markets/' + epic_id, headers=self.authenticated_headers) )

  def clientsentiment(self, market_id):
    return self._handlereq( requests.get(self.API_ENDPOINT + '/clientsentiment/'+market_id, headers=self.authenticated_headers) )

  def prices(self, epic_id, resolution):
    return self._handlereq( requests.get(self.API_ENDPOINT + '/prices/' + epic_id + '/' + resolution, headers=self.authenticated_headers) )

  def positions(self, deal_id=None):
    if deal_id is None:
      url = '/positions'
    else:
      url = '/positions/' + deal_id
    return self._handlereq( requests.get(self.API_ENDPOINT + url, headers=self.authenticated_headers) )

  def positions_otc(self, data):
    return self._handlereq( requests.post(self.API_ENDPOINT + '/positions/otc', data=json.dumps(data), headers=self.authenticated_headers) )

  def positions_otc_close(self, data):
    return self._handlereq( requests.post(self.API_ENDPOINT + '/positions/otc', data=json.dumps(data), headers=self._authheadersfordelete()) )

  def confirms(self, deal_ref):
    return self._handlereq( requests.get(self.API_ENDPOINT + '/confirms/' + deal_ref, headers=self.authenticated_headers) )

  def handleDealingRules(self, data):

    market = self.markets(data['epic'])
    dealingRules = market['dealingRules']

    current_price = float(market['snapshot']['bid'])

    r = 'marketOrderPreference'
    if dealingRules[r] == 'NOT_AVAILABLE':
      print("!!ERROR!! This market is not available for this dealing account")

    r = 'maxStopOrLimitDistance'
    if dealingRules[r]['unit'] == 'PERCENTAGE':
      if current_price/100 * float(dealingRules[r]['value']) < float(data['limitDistance']):
        data['limitDistance'] = str(format(current_price/100 * float(dealingRules[r]['value']), '.2f'))
    elif dealingRules[r]['unit'] == 'POINTS':
      if float(dealingRules[r]['value']) < float(data['limitDistance']):
        data['limitDistance'] = str(dealingRules[r]['value'])

    if data['guaranteedStop'] == True:
      r = 'minControlledRiskStopDistance'
    else: # data['guaranteedStop'] == False
      r = 'minNormalStopOrLimitDistance'
    if dealingRules[r]['unit'] == 'PERCENTAGE':
      if current_price/100 * float(dealingRules[r]['value']) > float(data['stopDistance']):
        data['stopDistance'] = str(format(current_price/100 * float(dealingRules[r]['value']), '.2f'))
    elif dealingRules[r]['unit'] == 'POINTS':
      if float(dealingRules[r]['value']) > float(data['stopDistance']):
        data['stopDistance'] = str(dealingRules[r]['value'])

    r = 'minDealSize'
    if dealingRules[r]['unit'] == 'POINTS':
      if float(dealingRules[r]['value']) > float(data['size']):
        data['size'] = str(dealingRules[r]['value'])
    elif dealingRules[r]['unit'] == 'PERCENTAGE':
      pass # err...what? we have to buy sell a percentage of everything?

    # minStepDistance
    # hmmm...i'm not doing this one :D
    # if our bid is smaller than the permitted amount, that's because:
    # we have no faith in the step being big enough;
    # or we don't have permission to make a step that big
    # either way, we shouldn't change it just to let the trade go through
    # it should fail 

    # trailingStopsPreference # TODO

    return data
