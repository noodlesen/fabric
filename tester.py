# TESTING TRADING STRATEGY OVER HISTORICAL DATA

from trading import get_trades_stats
from config import TS
from time import sleep


def test(f, symbol, params, **kwargs):
    trades = []
    f.reset()

    last_cc = None


    for i in range(f.range_from, f.range_to):
        cc = f.get(symbol)
        last_cc = cc
        TS.manage(cc, f, symbol, trades, params)
        trade = TS.open(cc, f, symbol, trades, params)
        if trade:
            trades.append(trade)

        f.next()

    inst_used = []
    closed_trades = []
    for t in trades:

        if t.is_closed:
            closed_trades.append(t)

    total_inv = sum([t.open_price for t in closed_trades])

    ts = get_trades_stats(closed_trades, **kwargs)
    if ts:
        ts['TOTAL_INV'] = total_inv
        ts['ROI'] = ts['PROFIT']/total_inv
    return ts
