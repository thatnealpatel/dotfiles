#!/home/neal/bin/scripts/stockbar/scripts/bin/python3
# load the virtual environment interpretter so you can use packages installed in venv.

from stockquotes import Stock
import configparser
import pytz, datetime, holidays, pathlib, os

# define some color constants for polybar formatting:
RED = '%{F#f00000}'
GREEN = '%{F#00ff00}'
CLEAR = '%{F-}'

# margin constant for spacing in polybar
MARGIN = '   '

# PATH to this file, CACHE name
PATH = str(pathlib.Path(__file__).parent.absolute()) + '/'
CACHE = 'res.cache'

config = configparser.ConfigParser()
config.read(PATH + 'config') # config file in dir
watchlist = config['watchlist']

display_info = {}
display_out = '' # classic pro leetcoder time

# market hours
def after_hours(now = None):

    tz = pytz.timezone('US/Eastern')
    us_holidays = holidays.US()

    if not now: now = datetime.datetime.now(tz)

    open_time = datetime.time(hour = 9, minute = 30, second = 0)
    close_time = datetime.time(hour = 16, minute = 0, second = 0)

    is_holiday = now.strftime('%Y-%m-%d') in us_holidays
    is_outside_hours = now.time() < open_time or now.time() > close_time
    is_weekend = now.date().weekday() > 4
    
    return is_holiday or is_weekend or is_outside_hours

# generates polybar-compliant formatted string based on config file
def generate_polybar_res() -> str:
    
    res = ''

    for ticker in watchlist:
        prefix = watchlist[ticker]
        query = ['', prefix][prefix != '$'] + ticker # we need to deal with stuff like ^spx and ^vix

        stock = Stock(query)
        stock_info = {
            'last': stock.current_price,
            'percent_change': stock.increase_percent,
            'mark_change': stock.increase_dollars
        }
        display_info[prefix+ticker] = stock_info


    for ticker in display_info:
        values = [] # order: [<last>, <% change>, <mark change>]
        
        for value in display_info[ticker].values():
            values.append(value)

        v = values # 'alias'
        neg = v[1] < 0.0
        display_string = f'{[GREEN, RED][neg]}{ticker}: {v[0]} ({v[1]}%){CLEAR}{MARGIN}'
        res += display_string

    return res

# controls whether or not to pull from local cache or live feed
def cache_or_pull() -> str:
    # the following control structure is ugly,
    # but for clarity in what conditions are taking place
    # the if/elif/else madness will remain
    # yes also global variables. it's python. it's fun. get over it.

    final_res = '' # it all starts here
    cache_exists = os.path.exists(PATH + 'res.cache')
    if after_hours() and cache_exists:
        # market is closed, we got a cache, no need to pull
        res_cache = open(PATH + CACHE, 'r')
        final_res = f'{res_cache.readline()}📁'
        res_cache.close()
    elif after_hours() and not cache_exists:
        # market is closed, but the cache doesn't exist yet!
        res_cache = open(PATH + CACHE, 'w+')
        final_res = f'{generate_polybar_res()}📈'
        res_cache.write(final_res)
        res_cache.close()
    elif not after_hours() and cache_exists:
        # market is open, get rid of cache. you don't want yesterday's closing data!
        os.remove(PATH + CACHE)
        final_res = f'{generate_polybar_res()}📈'
    elif not after_hours() and not cache_exists:
        # market is open, and no cache exists, business as usual!
        final_res = f'{generate_polybar_res()}📈'

    return final_res

# following is run every <interval> period as set in polybar:
display_out = cache_or_pull()
print(display_out) # polybar's final output