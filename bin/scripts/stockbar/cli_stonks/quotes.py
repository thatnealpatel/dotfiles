#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import typing as t
from cli_stonks.constants import Constants as const
from cli_stonks.util import refresh_access_token, query_quotes, write_to_log, create_polybar_tape

def get_quotes(symbols: t.List[str], fmt: str) -> str:
        
    try:
        response = query_quotes(symbols)

        if -1 in response:
            return 'Refresh complete (hopefully).'
        
        symbols_data = extract_data(response, symbols)

        if fmt == 'polybar': return create_polybar_tape(symbols_data)
        elif fmt == 'terminal': return get_quotes_term_fmt(symbols_data)
    except Exception as e:
        print(f'{const.RED}An exception has occured in quotes.py{const.CLEAR}')
        write_to_log(e)

    return 'unexpected behavior.'


def extract_data(symbols_json: t.Dict, keys: t.List[str]) -> t.List[t.Tuple]:
    symbols_data = []
    
    for symbol in keys:
        last_price, percent_change = 'err', 'err'
        delayed = symbols_json[symbol]['delayed']
        desc = symbols_json[symbol]['description']
        volume = symbols_json[symbol]['totalVolume']

        if symbol[0] == '$': # was an index search e.g. $VIX.X $SPX.X
            last_price = round(symbols_json[symbol]['lastPrice'], 2)
            percent_change = round(symbols_json[symbol]['netPercentChangeInDouble'], 2)
            symbol = f'^{symbol[1:-2]}'
        elif symbol[0] == '/': # was a futures search e.g. /ES
            last_price = round(symbols_json[symbol]['mark'], 2)
            percent_change = round(symbols_json[symbol]['futurePercentChange']*100, 2)
            symbol = f'{symbol}'
        else: # was a regular quote e.g. aapl, goog, xlf
            last_price = round(symbols_json[symbol]['mark'], 2)
            percent_change = round(symbols_json[symbol]['markPercentChangeInDouble'], 2)
            symbol = f'${symbol}'

        data = [last_price, percent_change, delayed, desc, volume]
        symbols_data.append((symbol.lower(), data))

    return symbols_data


def get_quotes_term_fmt(symbol_data: t.List[t.Tuple]) -> str:
    terminal_out = f'\n'
    
    for symbol, data in symbol_data:
        last_price, per_change = data[0], data[1]
        neg, is_delayed = per_change < 0.0, data[2]
        desc, volume = data[3], data[4]

        color_fmt = f'{const.TERM_RED if neg else const.TERM_GREEN}'

        tab = ' '
        line1 = f'{color_fmt}{symbol} ${last_price} ({per_change}%){const.TERM_RESET}'
        line2 = f'{tab}{desc}'
        line3 = f'{tab}Volume: {volume}\n{tab}Real-Time: {not is_delayed}'

        display_string = f'{line1}\n{line2}\n{line3}\n\n'
        terminal_out += display_string

    return terminal_out[:-1] # -1 to remove the final newline