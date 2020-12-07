#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import datetime, requests, json 
import typing as t
from cli_stonks.constants import Constants as const


def annualize(start_bal: float, curr_bal: float, time_in_days: int) -> float:
    return (1 + (curr_bal - start_bal)/start_bal)**(365/time_in_days) - 1


def write_to_log(message: str) -> None:
    with open(const.LOGFILE, 'a') as log: log.write(f'{str(datetime.datetime.now())}\n{message}')


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
    payload = {'fields': 'positions'}
    with open(const.ACCESS_TOKEN_FILE, 'r') as at: access_token = at.read()
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    return requests.get(url=const.TD_ENDPOINT_ACCOUNTS, params=payload, headers=headers).json()


def refresh_access_token() -> None:

    current_str_time = str(datetime.datetime.now())

    try:
        print(f'{const.GREEN}Refreshing ACCESS_TOKEN...{const.CLEAR}') # for polybar

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
        print(f'{const.RED}An error occured updating ACCESS_TOKEN. See log.{const.CLEAR}')
        log_output = f'An error occured updating ACCESS_TOKEN:\n{e}\n'
        write_to_log(log_output)


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

