from termcolor import colored
from config import TS
from fabric import Fabric
from drawer import draw_candles

def multitest(f, params, **kwargs):
    trades = []

    current_stats = []
    for i in range(f.range_from, f.range_to):
        for symbol in f.canvas.keys():
            cc = f.get(symbol)
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

    verbose = True

    days_max = 0
    days_min = 10000000
    number_of_wins = 0
    number_of_loses = 0
    max_loses_in_a_row = 0
    max_wins_in_a_row = 0
    current_loses_in_a_row = 0
    current_wins_in_a_row = 0
    sum_of_wins = 0
    sum_of_loses = 0
    max_profit_per_trade = 0
    max_loss_per_trade = 0

    open_reasons = {}
    close_reasons = {}

    res = None
    if trades:
        i = 0
        for t in trades:

            if t.is_closed:
                i += 1

                if t.open_reason in open_reasons.keys():
                    open_reasons[t.open_reason][0] += 1
                    open_reasons[t.open_reason][1] += t.profit
                else:
                    open_reasons[t.open_reason] = [0, 0]

                if t.close_reason in close_reasons.keys():
                    close_reasons[t.close_reason][0] += 1
                    close_reasons[t.close_reason][1] += t.profit
                else:
                    close_reasons[t.close_reason] = [0, 0]

                if kwargs.get('draw', False):
                    context = {
                        'number': len(t.data),
                        'width': 1000,
                        'height': 500,
                        'offset': 0
                    }
                    draw_candles(t.data, 'images/'+t.symbol+str(i)+'_'+t.direction+'_'+t.close_reason, context)

                if t.days > days_max:
                    days_max = t.days
                if t.days < days_min:
                    days_min = t.days

                if t.profit < 0:
                    if verbose:
                        print(colored(t, 'red'))
                    number_of_loses += 1
                    current_loses_in_a_row += 1
                    if current_wins_in_a_row > max_wins_in_a_row:
                        max_wins_in_a_row = current_wins_in_a_row
                    current_wins_in_a_row = 0
                    sum_of_loses += t.profit
                    if t.profit < max_loss_per_trade:
                        max_loss_per_trade = t.profit

                else:
                    if verbose:
                        print(t)
                    number_of_wins += 1
                    current_wins_in_a_row += 1
                    if current_loses_in_a_row > max_loses_in_a_row:
                        max_loses_in_a_row = current_loses_in_a_row
                    current_loses_in_a_row = 0
                    sum_of_wins += t.profit
                    if t.profit > max_profit_per_trade:
                        max_profit_per_trade = t.profit

        number_of_trades = len(trades)
        if number_of_loses:
            average_loss = sum_of_loses/number_of_loses
        else:
            average_loss = 0

        if number_of_wins:
            average_win = sum_of_wins/number_of_wins
        else:
            average_win = 0

        res = {}

        #res['SYMBOL'] = trades[0].symbol
        res['PROFIT'] = sum_of_wins+sum_of_loses
        res['TRADES'] = number_of_trades
        res['WINS'] = number_of_wins
        res['LOSES'] = number_of_loses
        res['WINS_TO_LOSES'] = number_of_wins/number_of_loses if number_of_loses > 0 else None
        res['WINRATE'] = number_of_wins/number_of_trades if number_of_trades > 0 else None
        res['AVG_WIN'] = average_win
        res['AVG_LOSS'] = average_loss
        res['MAX_PROFIT_PER_TRADE'] = max_profit_per_trade
        res['MAX_LOSS_PER_TRADE'] = max_loss_per_trade
        res['MAX_WINS_IN_A_ROW'] = max_wins_in_a_row
        res['MAX_LOSES_IN_A_ROW'] = max_loses_in_a_row
        res['DAYS_MAX'] = days_max
        res['DAYS_MIN'] = days_min
        res['OPEN_REASONS'] = open_reasons
        res['CLOSE_REASONS'] = close_reasons

    if res:
        res['TOTAL_INV'] = total_inv
        res['ROI'] = res['PROFIT']/total_inv


    print (res)
    return (res)


symbols = ['KO', 'T', 'ADBE', 'INTC']
f = Fabric()
f.load_data(symbols, 'ASTOCKS', 'DAILY')
f.trim()
if f.check():
    
    roi = 0
    best_params = None
    while roi<50:
        f.set_range_from_last(500)
        params = TS.get_random_ts_params()
        r = multitest(f, params, draw=False)
        if r and r['ROI']>roi:
            best_params = params
            roi = r['ROI']

    print(best_params)



