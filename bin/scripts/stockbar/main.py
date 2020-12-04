#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import sys
from cli_stonks.constants import Constants as const
from cli_stonks import quotes

print(f'debug:\n{const.WATCHLIST}')

symbols = ['$AAPL', '/es', 'bynd', '^vix']
quotes.get_quotes(symbols)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        operation = sys.argv[1]
        if operation == 'watchlist':
            # display_out = update_polybar_tape()
            # print(f'{display_out}') # polybar's final output
            pass
        elif operation == 'status':
            # print(get_td_acc_status())
            pass
        elif operation == 'quotes':
            # print(display_terminal_quote(sys.argv[2:]))
            pass
    else:
        print('Please provide a command line argument.')