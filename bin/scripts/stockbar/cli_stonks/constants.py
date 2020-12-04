#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

from dotenv import set_key, load_dotenv, find_dotenv
import os, pathlib, configparser

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

root_path = str(pathlib.Path(__file__).parent.parent.absolute()) + '/'
config_parser = configparser.ConfigParser()
config_parser.read(root_path + 'config') # config file in dir

class Constants:

    RED = '%{F#f00000}'
    GREEN = '%{F#00ff00}'
    YELLOW = '%{F#fba922}'
    GREY = '%{F#969896}'
    CLEAR = '%{F-}'
    MARGIN = f'{YELLOW} · {CLEAR}'

    # URXVT Color Codes
    TERM_GREEN = '\x1b[6;30;42m'
    TERM_RED = '\x1b[0;30;41m'
    TERM_RESET = '\x1b[0m'

    TRADE_START_DATE = (2020, 8, 24)
    TDA_PRINCIPLE = float(os.environ.get('TDA_PRINCIPLE'))
    TDA_ID = os.environ.get('TDA_ID')
    API_KEY = os.environ.get('API_KEY')
    AUTH_URL = os.environ.get('AUTH_URL')
    # ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')

    WATCHLIST = config_parser['watchlist']
    LOGFILE = root_path + 'log'
    ACCESS_TOKEN_FILE = root_path + '.access_token'

    TD_ENDPOINT_QUOTES = f'https://api.tdameritrade.com/v1/marketdata/quotes?'
    TD_ENDPOINT_TOKEN = f'https://api.tdameritrade.com/v1/oauth2/token'
    TD_ENDPOINT_ACCOUNTS = f'https://api.tdameritrade.com/v1/accounts/{TDA_ID}?'