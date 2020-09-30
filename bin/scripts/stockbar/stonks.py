#!/home/neal/bin/scripts/stockbar/scripts/bin/python3
# load the virtual environment interpretter so you can use packages installed in venv.

import configparser, requests, pytz, datetime, holidays, pathlib, os, json
from functools import reduce

# define some color constants for polybar formatting:
RED = '%{F#f00000}'
GREEN = '%{F#00ff00}'
YELLOW = '%{F#fba922}'
GREY = '%{F#969896}'
CLEAR = '%{F-}'

# margin constant for spacing in polybar
MARGIN = ' · '

# PATH to this file, CACHE name
PATH = str(pathlib.Path(__file__).parent.absolute()) + '/'
CACHE = 'res.cache'

config = configparser.ConfigParser()
config.read(PATH + 'config') # config file in dir
watchlist = config['watchlist']

display_info = []
display_out = ''

# custom query class because wrappers are unreliable?
class WatchlistInfo():

    def __init__(self, watchlist, contains_indexes = True):

        # Process data
        def clean(watchlist):
            watchlist = map(lambda x: ''.join(x).upper(), zip(watchlist.values(), watchlist.keys()))
            # print(list(watchlist))
            return watchlist

        if contains_indexes: watchlist = clean(watchlist)

        self.csv_symbols = ''.join( \
            reduce(lambda agg,ticker: \
                agg + ['$' + str(ticker[1:]) + '.X', str(ticker[1:])][ticker[0] == '$'] + ',', watchlist, ''))[:-1]
        
        # Initialize object
        self.tape = []

        # MULTI-SYMBOL REQUEST : 
        api_key = open(PATH + '.apikey', 'r')
        oauth = open(PATH + '.oauth', 'r')
        self.url = f'https://api.tdameritrade.com/v1/marketdata/quotes?'
        self.params = {
            'apikey': f'{api_key.readline()}',
            'symbol': self.csv_symbols,
            'Authorization': f'{oauth.readline()}'
        }
        api_key.close()
        oauth.close()

        # Populate object
        self.get_data()


    def get_data(self):

        def per_diff(prev_price: float, curr_price: float, decimal = 2) -> float:
            return round((curr_price - prev_price) / prev_price * 100, decimal)

        response = requests.get(url=self.url, params=self.params).json()

        for symbol in self.csv_symbols.split(','):
            last_price, percent_change = 'err', 'err'

            if symbol[0] == "$": # was an index search e.g. $VIX.X $SPX.X
                last_price = round(response[symbol]['lastPrice'], 2)
                percent_change = round(response[symbol]['netPercentChangeInDouble'], 2)
                symbol = f'^{symbol[1:-2]}'
            else:
                last_price = round(response[symbol]['regularMarketLastPrice'], 2)
                percent_change = round(response[symbol]['regularMarketPercentChangeInDouble'], 2)
                symbol = f'${symbol}'

            self.tape.append((symbol.lower(), [last_price, percent_change]))


class MarketHours():

    def __init__(self):
        self.tz = pytz.timezone('US/Eastern')
        self.us_holidays = holidays.US()

        self.premarket_open = datetime.time(hour = 6, minute = 30, second = 0)
        self.market_open = datetime.time(hour = 9, minute = 30, second = 0) # i.e. pre-market close
        self.market_close = datetime.time(hour = 16, minute = 0, second = 0)
        self.afterhours_close = datetime.time(hour = 20, minute = 0, second = 0)
    
    def is_holiday(self):
        now = datetime.datetime.now(self.tz)
        return now.strftime('%Y-%m-%d') in self.us_holidays

    def is_weekend(self):
        now = datetime.datetime.now(self.tz)
        return now.date().weekday() > 4

    def is_premarket(self):
        now = datetime.datetime.now(self.tz)
        return self.premarket_open <= now.time() < self.market_open  

    def is_open(self):
        now = datetime.datetime.now(self.tz)
        return self.market_open <= now.time() < self.market_close

    def is_afterhours(self):
        now = datetime.datetime.now(self.tz)
        return self.market_close <= now.time() < self.afterhours_close        

    def get_flag(self):
        flag = 'oopsie!'

        if self.is_holiday or self.is_weekend: flag = 'closed'
        if self.is_premarket: flag = 'pre-market'
        if self.is_open: flag = 'open'
        if self.is_afterhours: flag = 'after-hours'

        return flag

# generates polybar-compliant formatted string based on config file
def generate_polybar_res() -> str:
    
    res = ''
    watchlist_info = WatchlistInfo(watchlist)

    for ticker, values in watchlist_info.tape:
        # tuple<'$ticker', [<last>, <% change>, <mark change>]>
        v = values # 'alias'
        neg = v[1] < 0.0
        display_string = f'{[GREEN, RED][neg]}{ticker}: {v[0]} ({v[1]}%){CLEAR}{MARGIN}'
        res += display_string

    return res

# controls whether or not to pull from local cache or live feed
def update_tape() -> str:
    
    def make_cache():
        res_cache = open(PATH + CACHE, 'w+')
        final_res = f'{generate_polybar_res()}'
        res_cache.write(final_res)
        res_cache.close()

    final_res = '' # leetcoder pro btw
    cache_exists = os.path.exists(PATH + 'res.cache')
    market_hours = MarketHours()
    flag = market_hours.get_flag()

    # print(market_hours.is_holiday() or market_hours.is_weekend())

    if market_hours.is_holiday() or market_hours.is_weekend():
        if not cache_exists: make_cache()
        res_cache = open(PATH + CACHE, 'r')
        final_res = f'{res_cache.readline()}{GREY}({flag}){CLEAR}'
        res_cache.close()

    else:
        if cache_exists: os.remove(PATH + CACHE)
        final_res = f'{generate_polybar_res()}{YELLOW}({flag}){CLEAR}'

    return final_res

# following is run every <interval> seconds as set in polybar:
display_out = update_tape()
print(display_out) # polybar's final output