#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import sys
from cli_stonks.constants import Constants as constants

print(f'debug:\n{constants.WATCHLIST}')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        operation = sys.argv[1]
        if operation == 'watchlist':
            # display_out = update_polybar_tape()
            # print(f'{display_out}') # polybar's final output
        elif operation == 'acc_status':
            # print(get_td_acc_status())
        elif operation == 'get_quotes':
            # print(display_terminal_quote(sys.argv[2:]))
    else:
        print('Please provide a command line argument.')