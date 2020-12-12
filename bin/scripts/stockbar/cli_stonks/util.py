#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import datetime, requests, json 
import typing as t
import pandas as pd
from google.cloud import bigquery
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from cli_stonks.constants import Constants as const


T_BILL_SCRAPE_URL = f'https://ycharts.com/indicators/3_month_t_bill'


def annualize(start_bal: float, curr_bal: float, time_in_days: int) -> float:
    return (1 + (curr_bal - start_bal)/start_bal)**(365/time_in_days) - 1


def write_to_log(message: str, inclue_timestamp: bool = True) -> None:
    with open(const.LOGFILE, 'a') as log:
        timestamp = ['', f'{datetime.datetime.now()}\n'][inclue_timestamp]
        log.write(f'{timestamp}{message}')


def wrap_text(color: str, element: t.Any) -> str:
    colors = {
        'yellow': const.TERM_YELLOW_TEXT,
        'red': const.TERM_RED_TEXT,
        'green': const.TERM_GREEN_TEXT
    }
    return f'{colors[color]}{element}{const.TERM_RESET}'



def query_quotes(tickers: t.List[str]) -> t.Dict:
    csv_symbols = ','.join(tickers)
    with open(const.ACCESS_TOKEN_FILE, 'r') as at: access_token = at.read()
    payload = {
        'apikey': const.API_KEY,
        'symbol': csv_symbols,
    }
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'        
    }
    response = requests.get(url=const.TD_ENDPOINT_QUOTES, params=payload, headers=headers)

    if response.status_code == 401: # TD designated "access_token" has expired
        refresh_access_token()
        return {-1}
 
    return response.json()


def query_account() -> t.Dict:
    payload = {'fields': 'positions,orders'}
    with open(const.ACCESS_TOKEN_FILE, 'r') as at: access_token = at.read()
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    return requests.get(url=const.TD_ENDPOINT_ACCOUNTS, params=payload, headers=headers).json()


def refresh_access_token() -> None:

    current_str_time = str(datetime.datetime.now())

    try:
        #print(f'{const.GREEN}Refreshing ACCESS_TOKEN...{const.CLEAR}') # for polybar

        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        payload = {
            'grant_type': 'refresh_token', 
            'client_id': const.API_KEY, 
            'refresh_token': const.REFRESH_TOKEN
        }

        token_reply = requests.post(
            const.TD_ENDPOINT_TOKEN, 
            headers=headers, data=payload
        ).json()

        with open(const.ACCESS_TOKEN_FILE, 'w') as at: at.write(token_reply["access_token"])
        
        log_output = f'Updated access_token using refresh_token.\n'
        write_to_log(log_output)

    except Exception as e:
        #print(f'{const.RED}An error occured updating ACCESS_TOKEN. See log.{const.CLEAR}')
        log_output = f'An error occured updating ACCESS_TOKEN:\n{e}\n'
        write_to_log(log_output)


def get_watchlist_as_symbols() -> t.List[str]:
    return map(lambda x: ''.join(x).upper(), \
                zip(const.WATCHLIST.values(), const.WATCHLIST.keys()))


def clean_symbols(symbols: t.List[str]) -> t.List[str]:

    cleaned = []

    for symbol in symbols:
        if symbol[0] == '^': # index
            cleaned.append(f'${symbol[1:].upper()}.X')
        elif symbol[0] == '$': # verbose stock symbol
            cleaned.append(symbol[1:].upper())
        else: # futures/stock symbol
            cleaned.append(symbol.upper())

    return cleaned


def create_polybar_tape(symbol_data: t.List[t.Tuple]) -> str:
    # symbol_data[i]: tuple<str, list> :: ('AAPL', [115.0, -2.04, false])
    polybar_out = f''
    
    for symbol, data in symbol_data:
        last_price = data[0]
        per_change = data[1]
        neg, flat, is_delayed = per_change < 0.0, per_change == 0.0, data[2]

        # if negative -> .red else if flat -> .grey else -> .green
        ticker_dir = [[const.GREEN, const.GREY][flat], const.RED][neg]

        # make any delayed ticker show up as YELLOW instead of GREEN/RED
        delayed = ['', const.YELLOW][is_delayed]

        display_string = f'{ticker_dir}{delayed}{symbol}: '
        display_string += f'{last_price} ({per_change}%){const.CLEAR}{const.MARGIN}'
        
        polybar_out += display_string

    return polybar_out[:-19] # -19 to remove the extra const.MARGIN


def get_risk_free_rate(debug: bool = False) -> float:

    try: 
        options = Options()
        options.headless = True
        browser = webdriver.Chrome(executable_path=const.PATH_TO_CHROMEDRIVER, options=options)
        browser.implicitly_wait(0.3) # seconds
        browser.get(T_BILL_SCRAPE_URL)
        stat_element = browser.find_element_by_class_name('key-stat-title')
        risk_free_rate = float(stat_element.text.split(' ')[0][:-1]) / 100
    except Exception as e:
        if debug:
            print(f'error:\n{e}\n\n{e.message}')

        log_output = f'An error occured fetching the risk-free rate:\n{e}\n'
        write_to_log(log_output)
        return const.DEFAULT_RISK_FREE_RATE

    return risk_free_rate


def get_std_devs() -> float:

    client = bigquery.Client()
    table_id = 'cli-stocks.daily_portfolio_stats.daily_netliq'
    rows = client.list_rows(table_id)
    data = [(row[0], row[1]) for row in rows]
    returns_df = pd.DataFrame(data, columns=['day', 'netliq'])

    returns_df['per_change'] = returns_df.pct_change()['netliq']
    returns_df['days_since_last'] = returns_df.diff()['day']
    
    mean_return = returns_df.mean(axis=0)['per_change']
    mean_period = returns_df.mean(axis=0)['days_since_last']
    periods = 365 / mean_period

    current_stddev = returns_df.std(axis=0)['per_change']
    annualized_stddev = current_stddev * periods**(1/2)

    return current_stddev, annualized_stddev


def calculate_sharpe(current_return: float, annualized_return: float) -> float:

    risk_free_rate = get_risk_free_rate()
    
    current_stddev, annualized_stddev = get_std_devs()
    current_sharpe = (current_return - risk_free_rate) / current_stddev
    annualized_sharpe = (annualized_return - risk_free_rate) / annualized_stddev

    return current_sharpe, annualized_sharpe, risk_free_rate
