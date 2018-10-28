from drawer import draw_candles
from termcolor import colored


class Trade():

    def __str__(self):
        return '%s | %r > %r | = %r [%s][%s] %r %r' % (
            self.direction,
            self.open_price,
            self.close_price,
            self.profit,
            self.open_reason,
            self.close_reason,
            self.is_open,
            self.is_closed
        )

    def __init__(self):
        self.open_price = None
        self.close_price = None
        self.stoploss = None
        self.takeprofit = None

        self.days = 0
        self.data = []

        self.low = None
        self.high = None

        self.open_date = None
        self.close_date = None

        self.profit = None

        self.open_reason = None
        self.close_reason = None

        self.direction = None

        self.is_open = False
        self.is_closed = False

        self.is_real = False
        self.created_by = None
        self.ticket = None
        self.magic_number = None
        self.symbol = None


    def open_trade(self, symbol, direction, daydata, price, stoploss, takeprofit, open_reason):
        self.direction = direction
        self.days += 1
        self.is_open = True
        self.symbol = symbol
        self.open_price = price
        self.open_reason = open_reason
        self.stoploss = stoploss
        self.takeprofit = takeprofit
        dd = daydata.get_dict()
        dd['stoploss'] = stoploss
        dd['takeprofit'] = takeprofit
        self.data.append(dd)
        self.low = daydata.close_price
        self.high = daydata.close_price
        self.open_date = daydata.date
        self.open_time = daydata.time


    def close_trade(self, daydata, price, close_reason):
        self.close_price = price
        self.close_date = daydata.date
        self.close_time = daydata.time

        delta = round(self.close_price - self.open_price, 2)
        if self.direction:
            if self.direction == 'BUY':
                self.profit = delta
            elif self.direction == 'SELL':
                self.profit = -1*delta

        self.is_open = False
        self.is_closed = True
        self.close_reason = close_reason


    def update_trade(self, daydata):
        self.days += 1

        dd = daydata.get_dict()
        dd['stoploss'] = self.stoploss
        dd['takeprofit'] = self.takeprofit
        self.data.append(dd)

        if daydata.high_price > self.high:
            self.high = daydata.high_price
        if daydata.low_price < self.low:
            self.low = daydata.low_price

        if daydata.low_price <= self.stoploss:
            self.close_trade(daydata, self.stoploss, 'SL')
        if daydata.high_price >= self.takeprofit:
            self.close_trade(daydata, self.takeprofit, 'TP')

        if not self.is_closed:
            self.profit = daydata.close_price - self.open_price


def get_trades_stats(trades, **kwargs):

    verbose = kwargs.get('verbose', False)

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

        res['SYMBOL'] = trades[0].symbol
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
        #res['TRADES_LIST'] = trades

        return res

    else:
        return None

