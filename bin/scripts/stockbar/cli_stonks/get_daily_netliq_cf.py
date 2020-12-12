'''
Google Cloud Platform
Cloud Function
Executed via Cloud Scheduler

Purpose: Get daily net liquidition value in order to accurately calculate standard deviations
in portfolio returns which in turn is used to calculate sharpe ratios and adjust strategies.
'''

# LOCAL ONLY
from dotenv import set_key, load_dotenv, find_dotenv
dotenv_file = find_dotenv()
load_dotenv(dotenv_file)
# LOCAL ONLY

import os, requests, datetime, pandas
from google.cloud import bigquery

TDA_ID = os.environ.get('TDA_ID')
API_KEY = os.environ.get('API_KEY')
REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')

DAYS_SINCE_START = (datetime.date.today() - datetime.date(2020, 8, 24)).days

TD_ENDPOINT_TOKEN = f'https://api.tdameritrade.com/v1/oauth2/token'
TD_ENDPOINT_ACCOUNTS = f'https://api.tdameritrade.com/v1/accounts/{TDA_ID}?'

def get_access_token():
    try:     
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        payload = {
            'grant_type': 'refresh_token', 
            'client_id': API_KEY, 
            'refresh_token': REFRESH_TOKEN
        }
        token_reply = requests.post(
            TD_ENDPOINT_TOKEN, 
            headers=headers, data=payload
        ).json()

        return token_reply['access_token']
    except Exception as e:
        print(f'An error occured while fetching the access token.\n  {e}')


def get_netliq():
    try:
        payload = {'fields': 'positions,orders'}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {get_access_token()}'
        }

        acc_reply = requests.get(url=TD_ENDPOINT_ACCOUNTS, params=payload, headers=headers).json()
        net_liq = acc_reply['securitiesAccount']['currentBalances']['liquidationValue']
        
        return float(net_liq)
    except Exception as e:
        print(f'An error occured while fetching the net liquidition value.\n  {e}')


def write_to_bigquery_table(event = None, context = None):
    client = bigquery.Client()
    table_id = 'cli-stocks.daily_portfolio_stats.daily_netliq_test' # BQT doesn't allow deletion
    payload = [{u'day': DAYS_SINCE_START, u'netliq': get_netliq()}]
    errors = client.insert_rows_json(table_id, payload)
    if not errors:
        print('Successfully added netliq payload to the BQ Table.')
    else:
        print(f'Encountered error(s) while inserting payload:\n{errors}')
