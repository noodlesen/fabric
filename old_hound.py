from trading import Trade, trade_stats, close_all
from random import randint, choice
from indi import CCI


def manage(cc, c, trades, params):
    for trade in trades:
        if trade.is_open:
            trade.update_trade(cc)

            if not trade.is_closed:
                if trade.direction == 'BUY':
                    tp_base = sum([d['high'] for d in trade.data])/len(trade.data)
                    trade.takeprofit = tp_base*params.get('tp_koef', 2.1)
                elif trade.direction == 'SELL':
                    tp_base = sum([d['low'] for d in trade.data])/len(trade.data)
                    trade.takeprofit = tp_base*1/params.get('tp_koef', 2.1)

            # FIA — low profit - good winrate
            if params.get('use_FIA', False):
                fia_dmin = params.get('fia_dmin', 5)
                fia_dmax = params.get('fia_dmax', 15)
                fia_treshold = params.get('fia_treshold', 0.1)
                if trade.days > fia_dmin and trade.days < fia_dmax and (trade.profit/trade.days)/trade.open_price*100 < fia_treshold and trade.profit > 0:
                    trade.close_trade(cc, cc.close_price, 'FIA')

            #BREAKEVEN
            if not trade.is_closed and params.get('use_BREAKEVEN', False):
                if trade.direction == 'BUY' and trade.stoploss < trade.open_price and cc.low_price > trade.open_price:
                    trade.stoploss = cc.low_price
                if trade.direction == 'SELL' and trade.stoploss > trade.open_price and cc.high_price < trade.open_price:
                    trade.stoploss = cc.high_price

            #FORCE TAKE PROFIT
            if not trade.is_closed and params.get('use_FTP', False):
                if (trade.profit/trade.days)/trade.open_price > params.get('FTP', 0.01):
                    trade.close_trade(cc, cc.close_price, 'FTP')

            # PULL TO HAMMER/DOJI/SHOOTING STAR
            pull = False
            if not trade.is_closed:

                if cc.is_hammer():
                    if params.get('use_PTH', False):
                        pth = params.get('pth_mix', 0.25)
                        if trade.direction == 'BUY':
                            nsl = trade.stoploss*pth+cc.low_price*(1-pth)
                        elif trade.direction == 'SELL':
                            nsl = trade.stoploss*pth+cc.high_price*(1-pth)
                        pull = True

                if cc.is_shooting_star():
                    if params.get('use_PTSS', False):
                        ptss = params.get('ptss_mix', 0.25)
                        if trade.direction == 'BUY':
                            nsl = trade.stoploss*ptss+cc.low_price*(1-ptss)
                        elif trade.direction == 'SELL':
                            nsl = trade.stoploss*ptss+cc.high_price*(1-ptss)
                        pull = True

                if cc.is_doji():
                    if params.get('use_PTDJ', False):
                        ptdj = params.get('ptdj_mix', 0.25)
                        if trade.direction == 'BUY':
                            nsl = trade.stoploss*ptdj+cc.low_price*(1-ptdj)
                        if trade.direction == 'SELL':
                            nsl = trade.stoploss*ptdj+cc.high_price*(1-ptdj)
                        pull = True

            if c.pointer > 5 and params.get('use_PTTF', False):
                f = c.last(5, figure=True)
                if f.is_top_fractal():
                    ptf = params.get('pttf_mix', 0.25)
                    if trade.direction == 'BUY':
                        nsl = trade.stoploss*ptf+cc.low_price*(1-ptf)
                    elif trade.direction == 'SELL':
                        nsl = trade.stoploss*ptf+cc.high_price*(1-ptf)
                    pull = True

            if c.pointer > 5 and params.get('use_PTBF', False):
                f = c.last(5, figure=True)
                if f.is_bottom_fractal():
                    ptf = params.get('ptbf_mix', 0.25)
                    if trade.direction == 'BUY':
                        nsl = trade.stoploss*ptf+cc.low_price*(1-ptf)
                    elif trade.direction == 'SELL':
                        nsl = trade.stoploss*ptf+cc.high_price*(1-ptf)
                    pull = True

            if params.get('use_PTC2', False):
                ptf = params.get('ptc2_mix', 0.25)
                if CCI(c.last(2)) < CCI(c.last(2, -1)):
                    if trade.direction == 'BUY':
                        nsl = trade.stoploss*ptf+cc.low_price*(1-ptf)
                        pull = True
                elif CCI(c.last(2)) > CCI(c.last(2, -1)):
                    if trade.direction == 'SELL':
                        nsl = trade.stoploss*ptf+cc.high_price*(1-ptf)
                        pull = True

            if pull:
                if (nsl > trade.stoploss and trade.direction == 'BUY') or (nsl < trade.stoploss and trade.direction == 'SELL'):
                    trade.stoploss = nsl
                pull = False


def open(cc, c, trades, params):

    trade = None

    ts = trade_stats(trades)

    allowed_to_buy = False
    allowed_to_sell = False

    has_buy_signal = False
    has_sell_signal = False
    open_reason = None

    if ts['open'] <= params.get('max_pos', 50):    

        # TAIL
        if params.get('open_TAIL', False):
            bs = 0.01 if cc.body_size() == 0 else cc.body_size()
            if cc.low_tail()/bs > 0.2:
                has_buy_signal = True
                open_reason = 'TAIL_BUY'
            elif cc.high_tail()/bs > 0.2:
                has_sell_signal = True
                open_reason = 'TAIL_SELL'

        if c.pointer > 5:

            # BREAKUP
            if params.get('open_BREAK', False):
                f = c.last(5, figure=True)
                if f.is_breakup():
                    has_buy_signal = True
                    open_reason = 'BREAKUP_BUY'
                if f.is_breakdown():
                    has_sell_signal = True
                    open_reason = 'BREAKDOWN_SELL'

            #HAMMER
            if params.get('open_HAMMER', False):
                f = c.last(3, figure=True)
                if f.summary().is_hammer() or f.summary(last=2).is_hammer():
                    has_buy_signal = True
                    open_reason = 'HAMMER_BUY'
                elif f.summary().is_shooting_star() or f.summary(last=2).is_shooting_star():
                    has_sell_signal = True
                    open_reason = "S_STAR_SELL"

            #FRACTAL
            if params.get('open_FRACTAL', False):
                f = c.last(5, figure=True)
                if f.is_bottom_fractal():
                    has_buy_signal = True
                    open_reason = 'FRAC_BUY'
                elif f.is_top_fractal():
                    has_sell_signal = True
                    open_reason = 'FRAC_SELL'

        if params.get('open_C2', False):
            if CCI(c.last(2)) > CCI(c.last(2, -1)):
                has_buy_signal = True
                open_reason = 'C2_BUY'
            elif CCI(c.last(2)) > CCI(c.last(2, -1)):
                has_buy_signal = True
                open_reason = 'C2_SELL'

        filter_passed = True

        if params.get('use_FILTERS', False):

            filter_passed = False
            max_per = params.get('f_max_per', 250)
            th = params.get('f_max_th', 0.8)
            if c.pointer > max_per:
                m = max(bar['high'] for bar in c.last(max_per))
                if cc.close_price > m*th:
                    filter_passed = True

        if filter_passed and (has_buy_signal or has_sell_signal):

            tp_value = cc.close_price*params.get('rel_tp_k', 0.2)

            if has_buy_signal:
                if ts['open_long'] > ts['open_short'] or ts['open'] == 0:
                    allowed_to_buy = True
                else:
                    if ts['open_profit'] > -0.5: # PARAMS!
                        if params.get('use_FLIP', False):
                            close_all(trades, cc, 'FLIP')
                            allowed_to_sell = True

            if has_sell_signal:
                if ts['open_long'] < ts['open_short'] or ts['open'] == 0:
                    allowed_to_sell = True
                else:
                    if ts['open_profit'] > -0.5:
                        if params.get('use_FLIP', False):
                            close_all(trades, cc, 'FLIP')
                            allowed_to_buy = True

            if allowed_to_buy and allowed_to_sell:
                allowed_to_buy = False
                allowed_to_sell = False

            if allowed_to_buy:
                trade = Trade()
                trade.open_trade('BUY', cc, cc.close_price, cc.low_price*params.get('init_sl_k', 0.98), cc.close_price + tp_value, open_reason)

            if allowed_to_sell and params.get('trade_short', False):
                trade = Trade()
                trade.open_trade('SELL', cc, cc.close_price, cc.high_price*(2-params.get('init_sl_k', 0.98)), cc.close_price - tp_value, open_reason)

    return trade


def get_random_params():
    params = {
        'tp_koef': randint(1, 40)/10,
        'use_FIA': choice([True, False]),
        'use_CUT': choice([True, False]),
        'use_BREAKEVEN': choice([True, False]),
        'use_FTP': choice([True, False]),
        'fia_dmin': randint(2, 12),
        'fia_dmax': randint(12, 50),
        'fia_treshold': randint(2, 20)/100,
        'init_sl_k': randint(930, 999)/1000,
        'cut_mix': randint(1, 100)/100,
        'cut_treshold': randint(1, 100)/1000,
        'cut_period': randint(1, 20),
        'FTP': randint(1, 3000)/10000,
        'use_PTH': choice([True, False]),
        'use_PTSS': choice([True, False]),
        'use_PTDJ': choice([True, False]),
        'rel_tp_k': randint(5, 1000)/1000,
        'pth_mix': randint(5, 90)/100,
        'ptss_mix': randint(5, 90)/100,
        'ptdj_mix': randint(5, 90)/100,
        'pttf_mix': randint(5, 90)/100,
        'ptbf_mix': randint(5, 90)/100,
        'use_PTTF': choice([True, False]),
        'use_PTBF': choice([True, False]),
        'use_FILTERS': choice([True, False]),
        'f_max_per': randint(20, 301),
        'f_max_th': randint(50, 95)/100,
        'open_C2': choice([True, False]),
        'open_FRACTAL': choice([True, False]),
        'open_HAMMER': choice([True, False]),
        'open_TAIL': choice([True, False]),
        'open_BREAK': choice([True, False]),
        'use_PTC2': choice([True, False]),
        'ptc2_mix': randint(5, 90)/100,
        'use_FLIP': choice([True, False]),
        'trade_short': choice([True, False])
    }

    params['max_pos'] = 100
    return params