#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import sys
from cli_stonks.constants import Constants as const
from cli_stonks.quotes import get_quotes
from cli_stonks.account import get_account_information
from cli_stonks.util import clean_symbols

if __name__ == "__main__":
    if len(sys.argv) > 1:
        operation = sys.argv[1]
        if operation == 'watchlist':
            cleaned_symbols = clean_symbols(map(lambda x: ''.join(x).upper(), \
                zip(const.WATCHLIST.values(), const.WATCHLIST.keys())))
            print(get_quotes(cleaned_symbols, 'polybar'))
            # display_out = update_polybar_tape()
            # print(f'{display_out}') # polybar's final output
            pass
        elif operation == 'status':
            print(get_account_information())
        elif operation == 'quotes':
            cleaned_symbols = clean_symbols(sys.argv[2:])
            print(get_quotes(cleaned_symbols, 'terminal'))
    else:
        print('Please provide a command line argument.')