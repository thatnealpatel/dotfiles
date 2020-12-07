#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import typing as t
from cli_stonks.util import refresh_access_token

def get_quotes(symbols: t.List[str], fmt: str) -> t.List[t.Tuple]:
        
    try:
        if fmt == 'polybar': return get_quotes_polybar_fmt(symbols)
        elif fmt == 'terminal': return get_quotes_term_fmt(symbols)
    except Exception as e:
        print('An exception has occured in quotes.py')
        # refresh_access_token()

    return 'unexpected behavior.'


def get_quotes_term_fmt(symbols: t.List[str]) -> str:
    pass


def get_quotes_polybar_fmt(symbols: t.List[str]) -> str:
    pass 