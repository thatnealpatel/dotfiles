#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import datetime, requests, json
from cli_stonks.constants import Constants as const

def refresh_access_token() -> None:

    current_str_time = str(datetime.datetime.now())

    try:
        
        print(f'{const.GREEN}Refreshing ACCESS_TOKEN...{const.CLEAR}')

        token_url = 'https://api.tdameritrade.com/v1/oauth2/token'
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        payload = {
            'grant_type': 'refresh_token', 
            'client_id': const.API_KEY, 
            'refresh_token': const.REFRESH_TOKEN
        }

        token_reply = requests.post(
            'https://api.tdameritrade.com/v1/oauth2/token', 
            headers=headers, data=payload
        ).json()

        with open(const.ACCESS_TOKEN_FILE, 'w') as at: at.write(token_reply["access_token"])
        
        log_output = f'{current_str_time}: updated access_token using refresh_token.\n'
        with open(const.LOGFILE, 'a') as log: log.write(log_output)

    except Exception as e:

        print(f'{const.RED}An error occured updating ACCESS_TOKEN. See log.{const.CLEAR}')
        log_output = f'{current_str_time}: an error occured updating ACCESS_TOKEN:\n{e}\n'
        with open(logfile, 'a') as log: log.write(log_output)