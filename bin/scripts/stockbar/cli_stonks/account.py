#!/home/neal/bin/scripts/stockbar/stonks/bin/python3

import typing as t
import datetime
from cli_stonks.constants import Constants as const
from cli_stonks.util import query_account, annualize, calculate_sharpe, wrap_text

def get_account_information() -> str:
    return format_response(query_account())


def format_response(response: t.Dict) -> str:
    account_summary = create_account_summary(response)
    position_summary = create_position_summary(response)

    header_summary = f'summary{const.TERM_LINE1[len("summary")+1:]}'
    header_pos_text = 'positions'
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
    port_return = (net_liq - const.TDA_PRINCIPLE) / const.TDA_PRINCIPLE
    annualized_return = annualize(const.TDA_PRINCIPLE, net_liq, period_in_days.days)
    
    current_sharpe_ratio, annualized_sharpe_ratio, rfr = calculate_sharpe(port_return, annualized_return)

    port_return, annualized_return = round(port_return*100, 2), round(annualized_return*100, 2)
    current_sharpe_ratio = round(current_sharpe_ratio,2)
    annualized_sharpe_ratio = round(annualized_sharpe_ratio,2)

    rfr_err, rfr = rfr == const.DEFAULT_RISK_FREE_RATE, f'{round(rfr * 100, 2):>11}%' 
    rfr = [f'{rfr}', f'{wrap_text("red", rfr)}'][rfr_err]
    
    avail_funds = f'${curr_acc["availableFunds"]}'
    net_liq = f'${curr_acc["liquidationValue"]}'
    equity = f'${curr_acc["equity"]}'

    fmt_avail_funds = f'funds available{avail_funds:>11}'
    fmt_net_liq = f'net liquidity{net_liq:>13}'
    fmt_equity = f'equity{equity:>20}'
    fmt_port_return = f'return({period_in_days.days}){port_return:>14}%'
    annualized_return = f'annualized{annualized_return:>15}%' 
    fmt_annualized = f'{wrap_text("yellow", annualized_return)}'
    fmt_current_rfr = f'risk-free rate{rfr}'
    fmt_curr_sharpe = f'sharpe{current_sharpe_ratio:>20}'
    annualized_sharpe = f'annualized sharpe{annualized_sharpe_ratio:>9}'
    fmt_ann_sharpe = f'{wrap_text("yellow", annualized_sharpe)}'

    return f'{fmt_avail_funds}\n{fmt_net_liq}\n{fmt_equity}\n{fmt_port_return}\n{fmt_annualized}\
                \n{fmt_current_rfr}\n{fmt_curr_sharpe}\n{fmt_ann_sharpe}'


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
        curr_pnl_per = round(pos['currentDayProfitLossPercentage']*100, 2)
        sign = ['-', '+'][curr_pnl >= 0.0]

        curr_pnl = str(curr_pnl).replace("-","")
        color = ['red', 'green'][sign == '+']
        line_fmt = f'{pos_fmt}\t{sign}{curr_pnl:9}{curr_pnl_per:6}%'
        pos_summary = f'{pos_summary}{wrap_text(color, line_fmt)}\n'

    return pos_summary


def create_order_summary(response: t.Dict) -> str:
    pass