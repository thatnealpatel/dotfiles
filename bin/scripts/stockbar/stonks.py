#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import configparser, requests, pytz, datetime, holidays, pathlib, os, json, traceback, sys

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
TRADE_START_DATE = (2020, 8, 24)
TDA_PRINCIPLE = float(os.environ.get('TDA_PRINCIPLE'))

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

# Utility Class for Market Hours
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
        final_res = f'{RED}an error occurred; see /home/neal/bin/scripts/stockbar/log;{CLEAR}'

    return final_res

# query accounts for the command line utility {td-acc}
def query_acc(fields):
    with open(PATH + '.access_token', 'r') as at: access_token = at.read()
    tda_id = os.environ.get('TDA_ID')
    td_endpoint = f'https://api.tdameritrade.com/v1/accounts/{tda_id}?'
    payload = {'fields': fields}
    headers = { 
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}' 
    }
    return requests.get(url=td_endpoint, params=payload, headers=headers).json()

def get_beta_of(ticker):
    with open(PATH + '.access_token', 'r') as at: access_token = at.read()
    td_endpoint = f'https://api.tdameritrade.com/v1/instruments?'
    payload = {
        'symbol': ticker,
        'projection': 'fundamental'
    }
    headers = { 
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}' 
    }
    response = requests.get(url=td_endpoint, params=payload, headers=headers).json()
    return response[f'{ticker.upper()}']['fundamental']['beta']


# string format account summary for command line output
def create_acc_summary(response, annualize):
    curr_acc = response['securitiesAccount']['currentBalances']
    avail_funds = curr_acc['availableFunds']
    net_liq = curr_acc['liquidationValue']
    equity = curr_acc['equity']

    period_in_days = datetime.date.today() - datetime.date(*TRADE_START_DATE)
    annualized_return = round(annualize(TDA_PRINCIPLE, net_liq, period_in_days.days) * 100, 2)
    
    fmt_avail_funds = f'funds available\t${avail_funds}'
    fmt_net_liq = f'net liquidity\t${net_liq}'
    fmt_equity = f'cash & sweep\t${equity}'
    fmt_annualized = f'annualized({period_in_days.days})\t{annualized_return}%'
    # NEED TO RECALCULATE BETA

    return f'{fmt_avail_funds}\n{fmt_net_liq}\n{fmt_equity}\n{fmt_annualized}'

# string format positions summary for command line output
def create_pos_summary(response):
    positions = response['securitiesAccount']['positions']
    pos_summary = f''

    for pos in positions:
        if pos['instrument']['assetType'].lower() != "option": continue 
        qty = pos['shortQuantity']
        contract = pos['instrument']['symbol'].lower() # e.g. BYND_112020P155
        underlying = contract.split('_')[0]
        expiry = f'{contract.split("_")[1][:2]}/{contract.split("_")[1][2:4]}'
        contract_type, strike = contract.split('_')[1][6:7], contract.split('_')[1][7:]
        pos_fmt = f'-{int(qty)} {underlying}\t{expiry}\t{strike}{contract_type}'

        curr_pnl = pos['currentDayProfitLoss']
        curr_pnl_per = pos['currentDayProfitLossPercentage']
        sign = ['-', '+'][curr_pnl >= 0.0]

        line_fmt = f'{pos_fmt}\t{sign}{str(curr_pnl).replace("-","")}\t({curr_pnl_per}%)' 
        pos_summary = f'{pos_summary}{line_fmt}\n'
        # print(line_fmt)

    return pos_summary

# beta weighting
def get_position_beta():
    pass

def get_td_acc_status():
    
    def annualize(start_bal, curr_bal, time_in_days):
        return (1 + (curr_bal - start_bal)/start_bal)**(365/time_in_days) - 1

    # GET ACC INFO FROM QUERY
    response = query_acc('positions')

    # GENERAL
    term_line = f'\n{"-" * 26}\n'
    term_line2 = f'{"-" * 40}\n'

    # ACCOUNT SUMMARY
    acc_summary = create_acc_summary(response, annualize)
    
    # POSITIONS
    pos_summary = create_pos_summary(response)

    # HEADERS AND FORMATTING
    header_summary = f'summary{term_line[len("summary")+1:]}'
    header_positions = f'positions{term_line2[len("positions"):]}'
    summary_fmt = f'{header_summary}{acc_summary}{term_line}'
    positions_fmt = f'{header_positions}{pos_summary}{term_line2}'

    return f'\n{summary_fmt}\n{positions_fmt}'


class urxvt:
    GREEN = '\x1b[6;30;42m'
    RED = '\x1b[0;30;41m'
    RESET = '\x1b[0m'

def get_quote(ticker):
    with open(PATH + '.access_token', 'r') as at: access_token = at.read()
    td_endpoint = f'https://api.tdameritrade.com/v1/marketdata/quotes?'
    payload = {
        'symbol': ticker,
        'projection': 'fundamental'
    }
    headers = { 
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}' 
    }
    response = requests.get(url=td_endpoint, params=payload, headers=headers).json()
    return response[f'{ticker.upper()}']


def clean_input_for_td_endpoint(raw_ticker):
    if raw_ticker[0] == '^':
        return f'${raw_ticker[1:]}.X'
    else:
        return raw_ticker.upper()


def display_terminal_quote(ticker):
    valid_fields = {
        'future': ('mark', 'futurePercentChange'),
        'equity': ('mark', 'markPercentChangeInDouble'),
        'index': ('lastPrice', 'netPercentChangeInDouble')
    }

    ticker = clean_input_for_td_endpoint(ticker)
    ticker_info = get_quote(ticker)
    tab = ' '

    # shared between 3 classes
    symbol = ticker_info['symbol']
    desc = ticker_info['description']
    volume = ticker_info['totalVolume']
    delayed = ticker_info['delayed']

    # subject to change based on assetType
    adj_mark, adj_percent_change = valid_fields[ticker_info['assetType'].lower()]

    mark = ticker_info[adj_mark]
    mark_percent_change = ticker_info[adj_percent_change]

    neg = mark_percent_change < 0.0
    color_fmt = f'{urxvt.RED if neg else urxvt.GREEN}'

    line1 = f'{color_fmt}{symbol} ${mark} ({mark_percent_change}%){urxvt.RESET}'
    line2 = f'{tab}{desc}'
    line3 = f'{tab}Volume: {volume}\n{tab}Real-Time: {not delayed}'

    return f'{line1}\n{line2}\n{line3}'

def display_terminal_quotes(ticker_list):
    return 'coming soon :)'
    display_out = f''
    for ticker in ticker_list:
        display_terminal_quote(ticker)
        display_out += f''


# following is run every <interval> seconds as set in polybar:  
if __name__ == "__main__" and len(sys.argv) > 1:
    if sys.argv[1] == 'watchlist':
        display_out = update_polybar_tape()
        print(f'{display_out}') # polybar's final output
    elif sys.argv[1] == 'acc_status':
        print(get_td_acc_status())
    elif sys.argv[1] == 'get_quote':
        # print()
        print(display_terminal_quote(sys.argv[2]))
    elif sys.argv[1] == 'get_quotes':
        print(display_terminal_quotes(sys.argv[2:]))
else:
    print('please provide a command line argument.')