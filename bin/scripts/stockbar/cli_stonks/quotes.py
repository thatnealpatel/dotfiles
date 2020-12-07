#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import typing as t
from cli_stonks.util import refresh_access_token, query_quotes, write_to_log, create_polybar_tape

def get_quotes(symbols: t.List[str], fmt: str) -> str:
        
    try:
        response = query_quotes(symbols)

        if -1 in response:
            return 'Refresh complete (hopefully).'
        
        symbols_data = extract_data(response, symbols)

        if fmt == 'polybar': return create_polybar_tape(symbols_data)
        elif fmt == 'terminal': return create_polybar_tape(symbols_data) #get_quotes_term_fmt(symbols_data)
    except Exception as e:
        print('An exception has occured in quotes.py')
        print(e)
        write_to_log(e)

    return 'unexpected behavior.'


def extract_data(symbols_json: t.Dict, keys: t.List[str]) -> t.List[t.Tuple]:
    symbols_data = []
    
    for symbol in keys:
        last_price, percent_change = 'err', 'err'
        delayed = symbols_json[symbol]['delayed']
        if symbol[0] == '$': # was an index search e.g. $VIX.X $SPX.X
            last_price = round(symbols_json[symbol]['lastPrice'], 2)
            percent_change = round(symbols_json[symbol]['netPercentChangeInDouble'], 2)
            symbol = f'^{symbol[1:-2]}'
        elif symbol[0] == '/': # was a futures search e.g. /ES
            last_price = round(symbols_json[symbol]['mark'], 2)
            percent_change = round(symbols_json[symbol]['futurePercentChange']*100, 2)
            symbol = f'{symbol}'
        else: # was a regular quote e.g. aapl, goog
            last_price = round(symbols_json[symbol]['mark'], 2)
            percent_change = round(symbols_json[symbol]['markPercentChangeInDouble'], 2)
            symbol = f'${symbol}'
        symbols_data.append((symbol.lower(), [last_price, percent_change, delayed]))

    return symbols_data


def get_quotes_term_fmt(symbols: t.List[t.Tuple]) -> str:
    pass


def get_quotes_polybar_fmt(symbols: t.List[t.Tuple]) -> str:
    pass 