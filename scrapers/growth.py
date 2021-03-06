import logging, json, importio, latch, os

try:
  from scrapers.config import user_id as user_id 
  from scrapers.config import api_key as api_key
except ImportError:
  user_id = os.environ['user_id']
  api_key = os.environ['api_key']

from random import randint

client = importio.importio(user_id=user_id, api_key=api_key, host="https://query.import.io")

# Once we have started the client and authenticated, we need to connect it to the server:
client.connect()

# Because import.io queries are asynchronous, for this simple script we will use a "latch"
# to stop the script from exiting before all of our queries are returned
# For more information on the latch class, see the latch.py file included in this client library
queryLatch = latch.latch(1)

# Define here a global variable that we can put all our results in to when they come back from
# the server, so we can use the data later on in the script
dataRows = []

# In order to receive the data from the queries we issue, we need to define a callback method
# This method will receive each message that comes back from the queries, and we can take that
# data and store it for use in our app
def callback(query, message):
  global dataRows
  
  # Disconnect messages happen if we disconnect the client library while a query is in progress
  if message["type"] == "DISCONNECT":
    print "Query in progress when library disconnected"
    print json.dumps(message["data"], indent = 4)

  # Check the message we receive actually has some data in it
  if message["type"] == "MESSAGE":
    if "errorType" in message["data"]:
      # In this case, we received a message, but it was an error from the external service
      print "Got an error!" 
      print json.dumps(message["data"], indent = 4)
    else:
      # We got a message and it was not an error, so we can process the data
      print "Got data!"
      print json.dumps(message["data"], indent = 4)
      # Save the data we got in our dataRows variable for later
      dataRows.extend(message["data"]["results"])
  
  # When the query is finished, countdown the latch so the program can continue when everything is done
  if query.finished(): queryLatch.countdown()

# Issue queries to your data sources and with your inputs
# You can modify the inputs and connectorGuids so as to query your own sources
# Query for tile Finviz - Income
client.query({
  "connectorGuids": [
    "a952b9e3-1f3e-4bf7-b2eb-209829ae52f4"
  ],
  "input": {
    "webpage/url": "http://finviz.com/screener.ashx?v=151&f=fa_eps5years_pos,fa_estltgrowth_high,fa_pe_profitable,sh_avgvol_o500,sh_price_o10&ft=4&o=pe"
  }
}, callback)

queryLatch.await()

client.disconnect()


def growth(number, random=False):
  if random == True:
    number = randint(0, 20)
  company_original = dataRows[number]
  keys = company_original.keys()
  values = company_original.values()

  company = dict(zip(keys, values))

  return company