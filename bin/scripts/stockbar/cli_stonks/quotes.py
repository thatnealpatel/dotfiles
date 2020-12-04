#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import typing as t
from cli_stonks.util import refresh_access_token, clean_symbols

def get_quotes(symbols: t.List[str]) -> t.List[t.Tuple]:

    cleaned_symbols = clean_symbols(symbols)
    # print(cleaned_symbols)
    # print(','.join(cleaned_symbols))    

    
    
    # error only:
    # refresh_access_token()