import os
import urllib.request
from re import findall, sub
from bs4 import BeautifulSoup
from flask import Flask, render_template
import time

title = 'AceAdvisor'
year = time.strftime("%Y")
app = Flask(__name__)

class ScrapeSite:
	def __init__(self, url):
		self.url = url
		self.data = urllib.request.urlopen(url)
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
		ScrapeSite.__init__(self, 'http://www.bloomberg.com')

	def scrape_news(self):
		headlines = list(self.soup.find_all('a', {"class":"icon-article-headline"}))
		
		for link in headlines:
			if 'http://www.bloomberg.com' not in link['href']:
		 		link['href'] = link['href'].replace('/news/', r'http://www.bloomberg.com/news/')

		return headlines

class OptionsScreener:

	def pull_data(self, symbol):
		url = 'http://finance.yahoo.com/q/op?s={symbol}'.format(symbol=symbol)

		data = urllib.request.urlopen(url)
		soup = BeautifulSoup(data)
		body = soup.get_text()

		return soup.find_all('table', {"class":"yfnc_datamodoutline1"})

class ScreenerScraper(ScrapeSite):

	def pull_table(self):
		for link in self.soup.find_all('a'):
			if 'http://www.finviz.com' not in link['href']:
				link['href'] = link['href'].replace('quote.ashx', 'http://www.finviz.com/quote.ashx')

		table = self.soup.find_all('table', {'bgcolor':'#d3d3d3'})

		return table

		

OS = OptionsScreener()
Bloomberg_News = BloombergNews()
BMScraper = BloombergMarkets()
Income = ScreenerScraper('http://finviz.com/screener.ashx?v=152&f=an_recom_buybetter,fa_div_high,sh_avgvol_o500,sh_price_o10&ft=4&o=-dividendyield&c=0,1,2,3,4,5,6,7,14,65,66,67')
Growth = ScreenerScraper('http://finviz.com/screener.ashx?v=151&f=fa_eps5years_pos,fa_estltgrowth_high,fa_pe_profitable,sh_avgvol_o500,sh_price_o10&ft=4&o=pe')

@app.context_processor
def scrapers():
	return {'income_stocks':Income.pull_table(), 'growth_stocks':Growth.pull_table(), 'headlines':Bloomberg_News.scrape_news()}

@app.context_processor
def info():
	return {'title':title, 'year':year}

@app.route('/')
def index():
	return render_template('index.html', stock_markets=BMScraper.pull_data('stock_markets'), futures=BMScraper.pull_data('futures'), currencies=BMScraper.pull_data('currencies'))

@app.route('/options')
def options():
	return render_template('options.html', table=OS.pull_data)

if __name__ == '__main__':
	app.run(debug=True, port=8001)
