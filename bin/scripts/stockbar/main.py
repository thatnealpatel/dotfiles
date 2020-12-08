#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import sys
from cli_stonks.constants import Constants as const
from cli_stonks.quotes import get_quotes
from cli_stonks.account import get_account_information

if __name__ == "__main__":
    if len(sys.argv) > 1:
        operation = sys.argv[1]
        if operation == 'watchlist':
            print(get_quotes())
        elif operation == 'status':
            print(get_account_information())
        elif operation == 'quotes':
            print(get_quotes(sys.argv[2:], 'terminal'))
    else:
        print('Please provide a command line argument.')