#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import configparser, requests, pytz, datetime, holidays, pathlib, os, json, traceback

# this is so we can use os.environ.get() without having system wide secrets
from dotenv import load_dotenv
env_path = pathlib.Path('/home/neal/bin/scripts/stockbar') / '.env' # POSIX
load_dotenv(dotenv_path=env_path)

from functools import reduce

# define some color constants for polybar formatting:
RED = '%{F#f00000}'
GREEN = '%{F#00ff00}'
YELLOW = '%{F#fba922}'
GREY = '%{F#969896}'
CLEAR = '%{F-}'
MARGIN = f'{YELLOW} · {CLEAR}'

# PATH to this file
PATH = str(pathlib.Path(__file__).parent.absolute()) + '/'

# Specifically for INI files.
config = configparser.ConfigParser()
config.read(PATH + 'config') # config file in dir
watchlist = config['watchlist']

# Custom Real-Time (true 0 delay) WatchList Tickers Class
class WatchlistInfo():

    def __init__(self, watchlist, contains_indexes = True):            

        if contains_indexes: watchlist = self.clean_watchlist(watchlist)

        def prepare_symbols(agg, ticker):
            prepped_ticker = 'spy' # obvious display error if price for everything is $SPY
            
            is_stock, is_futures = ticker[0] == '$', ticker[0] == '/'

            if is_stock: prepped_ticker = ticker[1:] # $AAPL -> aapl
            elif is_futures: prepped_ticker = ticker # /ES -> /es
            else: prepped_ticker = f'${ticker[1:]}.X' # ^VIX -> $vix.x

            return f'{agg}{prepped_ticker},'

        '''
        According to TDA:
        - indexes must be queried as such:
            ^VIX -> $VIX.X
        - securities must be queried as such:
            $AAPL -> AAPL
        '''
        self.csv_symbols = ''.join(reduce(prepare_symbols, watchlist, ''))[:-1]

        with open(PATH + '.access_token', 'r') as at: self.access_token = at.read()
        self.tape = []
        self.api_key = os.environ.get('API_KEY')
        self.td_endpoint = f'https://api.tdameritrade.com/v1/marketdata/quotes?'
        self.payload = {
            'apikey': f'{self.api_key}',
            'symbol': self.csv_symbols,
        }
        self.headers = { 
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}' 
        }

    def clean_watchlist(self, watchlist):
        watchlist = map(lambda x: ''.join(x).upper(), \
            zip(watchlist.values(), watchlist.keys())) # keys are tickers, values are prefixes
        return watchlist

    # Refresh access_token in header for TD Ameritrade real-time    
    def refresh_headers(self):

        write_to_log = f'{str(datetime.datetime.now())} - updated access_token using refresh_token.\n'
        with open(PATH + 'log', 'a') as log: log.write(write_to_log)

        refresh_token = ''
        with open(PATH + '.refresh_token', 'r') as rt: refresh_token = rt.read()

        token_url = 'https://api.tdameritrade.com/v1/oauth2/token'
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        payload = {
            'grant_type': 'refresh_token', 
            'client_id': self.api_key, 
            'refresh_token': refresh_token
        }
        token_reply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=payload).json()
        
        self.headers['Authorization'] = f'Bearer {token_reply["access_token"]}'
        with open(PATH + '.access_token', 'w') as at: at.write(token_reply["access_token"])


    def make_tape(self):

        # print(self.headers) # debug
        response = requests.get(url=self.td_endpoint, params=self.payload, headers=self.headers)
        # print(response) # debug
        response = response.json()
        # print(response) # debug

        if 'error' in response:
            self.refresh_headers()
            response = requests.get(url=self.td_endpoint, params=self.payload, headers=self.headers).json()

        for symbol in self.csv_symbols.split(','):
            last_price, percent_change = 'err', 'err'
            delayed = response[symbol]['delayed']
            if symbol[0] == '$': # was an index search e.g. $VIX.X $SPX.X
                last_price = round(response[symbol]['lastPrice'], 2)
                percent_change = round(response[symbol]['netPercentChangeInDouble'], 2)
                symbol = f'^{symbol[1:-2]}'
            elif symbol[0] == '/': # was a futures search e.g. /ES
                last_price = round(response[symbol]['mark'], 2)
                percent_change = round(response[symbol]['futurePercentChange']*100, 2)
                symbol = f'{symbol}'
            else: # was a regular quote e.g. aapl, goog
                last_price = round(response[symbol]['mark'], 2)
                percent_change = round(response[symbol]['markPercentChangeInDouble'], 2)
                symbol = f'${symbol}'

            self.tape.append((symbol.lower(), [last_price, percent_change, delayed]))



class MarketHours():

    def __init__(self):
        self.tz = pytz.timezone('US/Eastern')
        self.us_holidays = holidays.US()

        self.premarket_open = datetime.time(hour = 6, minute = 30, second = 0)
        self.market_open = datetime.time(hour = 9, minute = 30, second = 0) # i.e. pre-market close
        self.market_close = datetime.time(hour = 16, minute = 0, second = 0)
        self.afterhours_close = datetime.time(hour = 20, minute = 0, second = 0)

        self.five_to_open = datetime.time(hour = 9, minute = 25, second = 0)
        self.five_to_close = datetime.time(hour = 15, minute = 55, second = 0)

        # self.test = datetime.time(hour = 18, minute = 10, second = 0)
    
    def rightnow(self):
        return datetime.datetime.now(self.tz)

    def is_holiday(self):
        return self.rightnow().strftime('%Y-%m-%d') in self.us_holidays

    def is_weekend(self):
        return self.rightnow().date().weekday() > 4

    def is_premarket(self):
        return self.premarket_open <= self.rightnow().time() < self.market_open  

    def is_open(self):
        return self.market_open <= self.rightnow().time() < self.market_close

    def is_afterhours(self):
        return self.market_close <= self.rightnow().time() < self.afterhours_close

    def is_closed(self):
        return self.is_weekend() or self.is_holiday() or (self.afterhours_close <= self.rightnow().time() < self.premarket_open)

    def now_to(self, period: str):
        dummy = datetime.date(1, 1, 1)
        res1 = datetime.datetime.combine(dummy, self.rightnow().time())
        choice = [self.market_close, self.market_open][period == 'open']
        res2 = datetime.datetime.combine(dummy, choice)
        return abs(res1 - res2).seconds

    def get_flag(self):
        flag = 'oopsie!'

        # if self.is_holiday() or self.is_weekend(): return 'closed'
        if self.is_premarket(): flag = 'pre-market'
        elif self.is_open(): flag = 'open'
        elif self.is_afterhours(): flag = 'after-hours'
        else: return f'{GREY}closed{CLEAR}' 

        about_to_open = self.five_to_open <= self.rightnow().time() < self.market_open
        about_to_close = self.five_to_close <= self.rightnow().time() < self.market_close
        
        # for adding countdown flags to 5 min before open/close
        period = (about_to_open and 'open') or (about_to_close and 'close') or 'null'
        color_flag = [RED, GREEN][period == 'open']

        return [f'{flag}: {color_flag}{self.now_to(period)}{YELLOW}', f'{flag}'][period == 'null']

# generates polybar-compliant formatted string based on config file
def generate_polybar_res(watchlist_info: WatchlistInfo) -> str:
    
    res = ''
    watchlist_info.make_tape() # actually create the tape in the object.

    for ticker, values in watchlist_info.tape:
        # tuple<'$/^ticker', [<last>, <% change>, <delayed>]>        
        last_price = values[0]
        per_change = values[1]
        neg, flat, is_delayed = per_change < 0.0, per_change == 0.0, values[2]

        # if negative -> red else if flat -> grey else -> green
        ticker_dir = [[GREEN, GREY][flat], RED][neg]

        # make any delayed ticker show up as YELLOW instead of GREEN/RED
        delayed = ["", YELLOW][is_delayed]

        display_string = f'{ticker_dir}{delayed}{ticker}: {last_price} ({per_change}%){CLEAR}{MARGIN}'
        
        res += display_string

    return res

# controls whether or not to pull from local cache or live feed
def update_polybar_tape() -> str:

    try:
        wl_info = WatchlistInfo(watchlist)
        market_hours = MarketHours()
        flag = market_hours.get_flag()
        final_res = f'{generate_polybar_res(wl_info)}{YELLOW}({flag}){CLEAR}' # leetcoder pro btw
    except Exception as e:
        write_to_log = f'{str(datetime.datetime.now())}\n{traceback.format_exc()}'
        with open(PATH + 'log', 'a') as log: log.write(write_to_log)
        final_res = f'{RED}an error occurred.{CLEAR}'

    return final_res

# following is run every <interval> seconds as set in polybar:
display_out = update_polybar_tape()
print(display_out) # polybar's final output