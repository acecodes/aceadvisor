import os
import urllib
from re import findall
from bs4 import BeautifulSoup
from flask import Flask, render_template
import time

# Individual scraper modules
import scrapers.income as income
import scrapers.growth as growth

title = 'AceAdvisor'
year = time.strftime("%Y")
app = Flask(__name__)

class ScrapeSite:
	def __init__(self, url):
		self.url = url
		self.data = urllib.urlopen(url)
		self.soup = BeautifulSoup(self.data)
		self.body = self.soup.get_text()

	def regex(self, string):
		return findall(string, self.body)

## Bloomberg Markets ##
class BloombergMarkets(ScrapeSite):

	def __init__(self):
		ScrapeSite.__init__(self, 'http://www.bloomberg.com/markets/')

	# Gather data from Bloomberg's markets page
	def pull_data(self, market_choice=""):
		names = self.soup.find_all('td', {"class":"name"})
		values = self.soup.find_all('td', {"class":"value"})
		change = self.soup.find_all('td', {"class":"percent_change"})

		count = 0
		full_table = []

		# Creates a series of nested lists for the various markets listed on the page
		for items in values:
			full_table.append([str(names[count].get_text()), str(values[count].get_text()), str(change[count].get_text())])
			count += 1

		# Creates individualized tuples for each marketplace
		stock_markets = tuple(full_table[:8])
		currencies = tuple(full_table[17:])
		futures = tuple(full_table[9:16])

		if market_choice == 'stock_markets':
			return stock_markets
		elif market_choice == 'currencies':
			return currencies
		elif market_choice == 'futures':
			return futures
		else:
			return stock_markets, currencies, futures

## Bloomberg News 

class BloombergNews(ScrapeSite):

	def __init__(self):
		ScrapeSite.__init__(self, 'http://www.bloomberg.com/news/stocks/')

	def scrape_news(self):
		headlines = self.soup.find_all('a', {"class":"q story_link black"})
		return headlines

BMNews = BloombergNews()
BMScraper = BloombergMarkets()

@app.context_processor
def scrapers():
	return {'income_stocks':income.stocks, 'growth_stocks':growth.stocks, 'headlines':BMNews.scrape_news()}

@app.context_processor
def info():
	return {'title':title, 'year':year}

@app.route('/')
def index():
	return render_template('index.html', stock_markets=BMScraper.pull_data('stock_markets'), futures=BMScraper.pull_data('futures'), currencies=BMScraper.pull_data('currencies'))

if __name__ == '__main__':
	app.run(debug=True, port=8001)