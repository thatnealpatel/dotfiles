#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import typing as t
import datetime
from cli_stonks.constants import Constants as const
from cli_stonks.util import query_account, annualize

def get_account_information() -> str:
    return format_response(query_account())


def format_response(response: t.Dict) -> str:
    account_summary = create_account_summary(response)
    position_summary = create_position_summary(response)

    header_summary = f'summary{const.TERM_LINE1[len("summary")+1:]}'
    header_pos_text = 'positions(today)'
    header_positions = f'{header_pos_text}{const.TERM_LINE2[len(header_pos_text):]}'
    summary_fmt = f'{header_summary}{account_summary}{const.TERM_LINE1}'
    positions_fmt = f'{header_positions}{position_summary}{const.TERM_LINE2}'

    return f'\n{summary_fmt}\n{positions_fmt}'


def create_account_summary(response: t.Dict) -> str:
    curr_acc = response['securitiesAccount']['currentBalances']
    avail_funds = curr_acc['availableFunds']
    net_liq = curr_acc['liquidationValue']
    equity = curr_acc['equity']

    period_in_days = datetime.date.today() - datetime.date(*const.TRADE_START_DATE)
    annualized_return = round(annualize(const.TDA_PRINCIPLE, net_liq, period_in_days.days) * 100, 2)
    
    fmt_avail_funds = f'funds available\t${avail_funds}'
    fmt_net_liq = f'net liquidity\t${net_liq}'
    fmt_equity = f'equity\t\t${equity}'
    fmt_annualized = f'annualized({period_in_days.days})\t{annualized_return}%' 

    return f'{fmt_avail_funds}\n{fmt_net_liq}\n{fmt_equity}\n{fmt_annualized}'


def create_position_summary(response: t.Dict) -> str:
    positions = response['securitiesAccount']['positions']
    pos_summary = f''

    for pos in positions:
        asset_type = pos['instrument']['assetType']
        if asset_type.lower() == "cash_equivalent": continue 
        qty = pos['shortQuantity'] if asset_type.lower() == 'option' else pos['longQuantity']
        contract = pos['instrument']['symbol'].lower() # e.g. BYND_112020P155
        
        if asset_type.lower() == 'option':
            underlying = pos['instrument']['underlyingSymbol'].lower()
            expiry = f'{contract.split("_")[1][:2]}/{contract.split("_")[1][2:4]}'
            contract_type, strike = contract.split('_')[1][6:7], contract.split('_')[1][7:]
            pos_fmt = f'-{int(qty)}\t{underlying}\t{expiry}\t{strike}{contract_type}'
        else:
            pos_fmt = f'{int(qty)}\t{contract}\t-\tLONG'

        curr_pnl = round(pos['currentDayProfitLoss'], 2)
        curr_pnl_per = round(pos['currentDayProfitLossPercentage'], 2)
        sign = ['-', '+'][curr_pnl >= 0.0]

        line_fmt = f'{pos_fmt}\t{sign}{str(curr_pnl).replace("-","")}\t({curr_pnl_per}%)' 
        pos_summary = f'{pos_summary}{line_fmt}\n'

    return pos_summary