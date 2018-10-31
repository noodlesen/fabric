from trading import Trade #, close_all
from random import randint, choice
from indi import CCI, SMA

TS_NAME = 'HOUND'

def ts_name():
    return (TS_NAME)

def manage(cc, f, symbol, all_trades, params):
    trades = [t for t in all_trades if t.symbol==symbol and t.is_open]
    for trade in trades:
        trade.update_trade(cc)

        if not trade.is_closed:
            tp_base = sum([d['high'] for d in trade.data])/len(trade.data)
            tp_base = sum([d['high'] for d in trade.data])/len(trade.data)
            trade.takeprofit = tp_base*params.get('tp_koef', 2.1)

        # FIA — low profit - good winrate
        if not trade.is_closed and params.get('use_FIA', False):
            fia_dmin = params.get('fia_dmin', 5)
            fia_dmax = params.get('fia_dmax', 15)
            fia_treshold = params.get('fia_treshold', 0.1)
            if trade.days > fia_dmin and trade.days < fia_dmax and (trade.profit/trade.days)/trade.open_price*100 < fia_treshold and trade.profit > 0:
                trade.close_trade(cc, cc.close_price, 'FIA')

        #BREAKEVEN
        if not trade.is_closed and params.get('use_BREAKEVEN', False):
            if trade.stoploss < trade.open_price and cc.low_price > trade.open_price:
                trade.stoploss = cc.low_price

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
                    nsl = trade.stoploss*pth+cc.low_price*(1-pth)
                    pull = True

            if cc.is_shooting_star():
                if params.get('use_PTSS', False):
                    ptss = params.get('ptss_mix', 0.25)
                    nsl = trade.stoploss*ptss+cc.low_price*(1-ptss)
                    pull = True

            if cc.is_doji():
                if params.get('use_PTDJ', False):
                    ptdj = params.get('ptdj_mix', 0.25)
                    nsl = trade.stoploss*ptdj+cc.low_price*(1-ptdj)
                    pull = True

        if f.pointer > 5 and params.get('use_PTTF', False):
            ff = f.last(symbol, 5, figure=True)
            if ff.is_top_fractal():
                ptf = params.get('pttf_mix', 0.25)
                nsl = trade.stoploss*ptf+cc.low_price*(1-ptf)
                pull = True

        if f.pointer > 5 and params.get('use_PTBF', False):
            ff = f.last(symbol, 5, figure=True)
            if ff.is_bottom_fractal():
                ptf = params.get('ptbf_mix', 0.25)
                nsl = trade.stoploss*ptf+cc.low_price*(1-ptf)
                pull = True

        # if f.pointer > 10 and params.get('use_PTP', False):
        #     if f.last(symbol, 10, figure=True).is_power_growth:
        #         ptf = params.get('ptp_mix', 0.5)
        #         nsl = trade.stoploss*ptf+cc.low_price*(1-ptf)
        #         pull = True

        if params.get('use_PTC2', False):
            ptf = params.get('ptc2_mix', 0.25)
            if CCI(f.last(symbol, 2)) < CCI(f.last(symbol, 2, -1)):
                nsl = trade.stoploss*ptf+cc.low_price*(1-ptf)
                pull = True

        if pull:
            if nsl > trade.stoploss:
                trade.stoploss = nsl
            pull = False


def open(cc, f, symbol, trades, params):

    trade = None

    #ts = trade_stats(trades)

    allowed_to_buy = False

    has_buy_signal = False

    open_reason = None

    if True:

        # TAIL
        if params.get('open_TAIL', False):
            bs = 0.01 if cc.body_size() == 0 else cc.body_size()
            if cc.low_tail()/bs > 0.2:
                has_buy_signal = True
                open_reason = 'TAIL_BUY'

        if f.pointer > 50:

            # BREAKUP
            if params.get('open_BREAK', False):
                ff = f.last(symbol, 5, figure=True)
                if ff.is_breakup():
                    has_buy_signal = True
                    open_reason = 'BREAKUP_BUY'

            #HAMMER
            if params.get('open_HAMMER', False):
                ff = f.last(symbol, 3, figure=True)
                if ff.summary().is_hammer() or ff.summary(last=2).is_hammer():
                    has_buy_signal = True
                    open_reason = 'HAMMER_BUY'

            #DOUBLE HAMMER
            if params.get('open_DOUBLE_HAMMER', False):
                pf = params.get('dh_fast', 2)
                ps = params.get('dh_slow', 20)

                if f.last(symbol, pf, figure=True).summary().is_hammer() and f.last(symbol, ps, figure=True).summary().is_hammer():
                    has_buy_signal = True
                    open_reason = 'DOUBLE_HAMMER'

            #FRACTAL
            if params.get('open_FRACTAL', False):
                ff = f.last(symbol,5, figure=True)
                if ff.is_bottom_fractal():
                    has_buy_signal = True
                    open_reason = 'FRAC_BUY'

            #C2
            if params.get('open_C2', False):
                if CCI(f.last(symbol, 2)) > CCI(f.last(symbol, 2, -1)):
                    has_buy_signal = True
                    open_reason = 'C2_BUY'


        passed_filters = []

        if params.get('use_HIGH_FILTER', False):

            high_filter_passed = 0
            max_per = params.get('hf_max_per', 250)
            th = params.get('hf_max_th', 0.8)
            if f.pointer > max_per:
                m = max(bar['high'] for bar in f.last(symbol,max_per))
                if cc.close_price > m*th:
                    high_filter_passed = 1
            passed_filters.append(high_filter_passed)

        if params.get('use_CCI_FILTER', False):
            cci_filter_passed = 0
            per = params.get('cci_f_per', 14)
            if CCI(f.last(symbol, per)) > CCI(f.last(symbol, per, -1)):
                cci_filter_passed = 1     
            passed_filters.append(cci_filter_passed)

        # if params.get('use_COS_FILTER', False):
        #     cos_filter_passed = 0
        #     per = params.get('cos_f_per', 14)
        #     if CCI(f.last(symbol, per)) > params.get('cos_f_val', 50):
        #         cos_filter_passed = 1     
        #     passed_filters.append(cos_filter_passed)

        if params.get('use_SMA_FILTER', False):
            sma_filter_passed = 0
            per1 = params.get('sma_f_per_1', 12) # 5 - 15
            per2 = params.get('sma_f_per_2', 24) # 16 - 30
            per3 = params.get('sma_f_per_3', 50) # 31 - 50
            if SMA(f.last(symbol, per1)) > SMA(f.last(symbol, per2)) > SMA(f.last(symbol, per3)):
                sma_filter_passed = 1     
            passed_filters.append(sma_filter_passed)

        all_filters_passed = sum(passed_filters) == len(passed_filters)


        if all_filters_passed and has_buy_signal:

            tp_value = cc.close_price*params.get('rel_tp_k', 0.2)

            if has_buy_signal:
                
                allowed_to_buy = True

            if allowed_to_buy:
                trade = Trade()
                trade.open_trade(symbol, 'BUY', cc, cc.close_price, cc.low_price*params.get('init_sl_k', 0.98), cc.close_price + tp_value, open_reason)

    return trade


def get_random_ts_params():
    params = {

        # INITIAL

        'tp_koef': randint(1, 40)/10,
        'init_sl_k': randint(500, 999)/1000,
        'rel_tp_k': randint(5, 1000)/1000,

        # OPENING SIGNALS

        'open_FRACTAL': choice([True, False]),
        'open_HAMMER': choice([True, False]),
        'open_TAIL': choice([True, False]),
        'open_BREAK': choice([True, False]),
        'open_DOUBLE_HAMMER': choice([True, False]),
        'open_C2': choice([True, False]),

        # MANAGEMENT

        'use_FIA': choice([True, False]),
        'use_CUT': choice([True, False]),
        'use_BREAKEVEN': choice([True, False]),
        'use_FTP': choice([True, False]),
        'fia_dmin': randint(2, 12),
        'fia_dmax': randint(12, 50),
        'fia_treshold': randint(2, 20)/100,
        'cut_mix': randint(1, 100)/100,
        'cut_treshold': randint(1, 100)/1000,
        'cut_period': randint(1, 20),
        'dh_fast': randint(1, 5),
        'dh_slow': randint(8, 50),
        'FTP': randint(1, 3000)/10000,
        'use_PTH': choice([True, False]),
        'use_PTSS': choice([True, False]),
        'use_PTDJ': choice([True, False]),
        'pth_mix': randint(5, 90)/100,
        'ptss_mix': randint(5, 90)/100,
        'ptdj_mix': randint(5, 90)/100,
        'pttf_mix': randint(5, 90)/100,
        'ptbf_mix': randint(5, 90)/100,
        'use_PTTF': choice([True, False]),
        'use_PTBF': choice([True, False]),
        'use_PTC2': choice([True, False]),
        'ptc2_mix': randint(5, 90)/100,

        # FILTERS

        'use_HIGH_FILTER': choice([True, False]),
        'hf_max_per': randint(20, 301),
        'hf_max_th': randint(50, 95)/100,

        'use_CCI_FILTER': choice([True, False]),
        'cci_f_per': randint(8, 20),

        'use_SMA_FILTER': choice([True, False]),
        'sma_f_per_1': randint(5, 15),
        'sma_f_per_2': randint(15, 30),
        'sma_f_per_3': randint(30, 50),
        # 'use_PTP': choice([True, False]),
        # 'ptp_mix': randint(5, 90)/100,
        # 'use_COS_FILTER': choice([True, False]),
        # 'cos_f_per': randint(12, 30),
        # 'cos_f_val': randint(0, 100)



    }

    return params
