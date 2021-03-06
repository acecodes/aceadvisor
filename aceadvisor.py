import urllib.request
import time
from re import findall
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length
from flask.ext.cache import Cache


title = 'AceAdvisor'
year = time.strftime("%Y")
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


CSRF_ENABLED = True

app.config.from_object('config')

""" Base class for scraping websites """


class ScrapeSite:

    def __init__(self, url):
        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                       'Accept-Encoding': 'none',
                       'Accept-Language': 'en-US,en;q=0.8',
                       'Connection': 'keep-alive'}
        self.url = url
        self.req = urllib.request.Request(self.url, headers=self.header)
        self.data = urllib.request.urlopen(self.req)
        self.soup = BeautifulSoup(self.data)
        self.body = self.soup.get_text()

    def regex(self, string):
        return findall(string, self.body)


""" Bloomberg Markets """


class BloombergMarkets(ScrapeSite):

    def __init__(self):
        ScrapeSite.__init__(self, 'http://www.bloomberg.com/markets/world/')

    # Gather data from Bloomberg's markets page
    def pull_data(self, market_choice=""):
        names = self.soup.find_all('td', {"class": "name"})
        values = self.soup.find_all('td', {"class": "value"})
        change = self.soup.find_all('td', {"class": "percent_change"})

        count = 0
        full_table = []

        # Creates a series of nested lists for the various markets listed on
        # the page
        for items in values:
            full_table.append([str(names[count].get_text()), str(
                values[count].get_text()), str(change[count].get_text())])
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

""" Bloomberg News """


class BloombergNews(ScrapeSite):

    def __init__(self):
        ScrapeSite.__init__(self, 'http://www.bloomberg.com')

    def scrape_news(self):
        headlines = list(
            self.soup.find_all('a', {"class": "feed-item__link"}))

        for link in headlines:
            link['href'] = link['href'].replace(
                '/news/', r'http://www.bloomberg.com/news/')

        return headlines

""" Options Screener """


class OptionsScreener:

    def __init__(self, ticker):

        self.ticker = ticker
        self.url = 'http://finance.yahoo.com/q/op?s={ticker}'.format(
            ticker=ticker)
        self.data = urllib.request.urlopen(self.url)
        self.soup = BeautifulSoup(self.data)
        self.body = self.soup.get_text()
        self.table = self.soup.find_all(
            'table', {"class": "yfnc_datamodoutline1"})

    def expiration_dates(self):
        table = self.soup.find_all('tr', {"valign": "top"})
        return table[0]

    def calls(self, timeframe=None):

        if timeframe != None:
            self.url = 'http://finance.yahoo.com/q/op?s={symbol}&m={timeframe}'.format(
                symbol=self.ticker, timeframe=timeframe)

        return self.table[0]

    def puts(self, timeframe=None):
        if timeframe != None:
            self.url = 'http://finance.yahoo.com/q/op?s={symbol}&m={timeframe}'.format(
                symbol=self.ticker, timeframe=timeframe)

        return self.table[1]

    def company_name(self, symbol):

        first_title = findall(r'SheetCash Flow\s.+\(.+\w+\)', self.body)
        final_title = [item.replace('SheetCash Flow\n', '')
                       for item in first_title]

        try:
            return final_title[0]
        except:
            return None

""" Options form """


class OptionsForm(Form):
    symbol = StringField(
        'Enter a ticker symbol:', validators=[Required(), Length(min=1, max=5)])
    submit = SubmitField('Get Options Quotes')

""" Stock Screeners """


class ScreenerScraper(ScrapeSite):

    def pull_table(self):
        for link in self.soup.find_all('a'):
            if 'http://www.finviz.com' not in link['href']:
                link['href'] = link['href'].replace(
                    'quote.ashx', 'http://www.finviz.com/quote.ashx')

        table = self.soup.find_all('table', {'bgcolor': '#d3d3d3'})

        return table

""" Determine if the market is open or closed """


class MarketStatus(ScrapeSite):

    def __init__(self):
        ScrapeSite.__init__(
            self, 'https://secure.marketwatch.com/investing/index/DJIA')

    def open_closed(self):

        return self.soup.find(class_="column marketstate").string

Bloomberg_News = BloombergNews()
BMScraper = BloombergMarkets()
Income = ScreenerScraper(
    'http://finviz.com/screener.ashx?v=152&f=an_recom_buybetter,fa_div_high,sh_avgvol_o500,sh_price_o10&ft=4&o=-dividendyield&c=0,1,2,3,4,5,6,7,14,65,66,67')
Growth = ScreenerScraper(
    'http://finviz.com/screener.ashx?v=151&f=fa_eps5years_pos,fa_estltgrowth_high,fa_pe_profitable,sh_avgvol_o500,sh_price_o10&ft=4&o=pe')
Status = MarketStatus()


@app.context_processor
def scrapers():
    return {'income_stocks': Income.pull_table(),
            'growth_stocks': Growth.pull_table(),
            'headlines': Bloomberg_News.scrape_news(),
            'open_closed': Status.open_closed()}


@app.context_processor
def info():
    return {'title': title, 'year': year}


@cache.cached(timeout=60)
@app.route('/options', methods=['GET', 'POST'])
def options():
    try:
        symbol = request.form['symbol']
    except:
        symbol = None

    OS = OptionsScreener(symbol)
    return render_template('options.html',
                           symbol=symbol, calls=OS.calls(symbol),
                           puts=OS.puts(symbol),
                           company_name=OS.company_name(symbol),
                           expiration_dates=OS.expiration_dates())


@cache.cached(timeout=60)
@app.route('/', methods=['GET', 'POST'])
def index():
    form = OptionsForm()
    print(form.errors)
    if form.validate_on_submit():
        return redirect(url_for('options', symbol=form.symbol.data))
    return render_template('index.html',
                           stock_markets=BMScraper.pull_data('stock_markets'),
                           futures=BMScraper.pull_data('futures'),
                           currencies=BMScraper.pull_data('currencies'),
                           options_form=form)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
