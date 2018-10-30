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

        self.open_datetime = None
        self.close_datetime = None

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
        self.drawdown = None


    def open_trade(self, symbol, direction, this_day, price, stoploss, takeprofit, open_reason):
        self.direction = direction
        self.days += 1
        self.is_open = True
        self.symbol = symbol
        self.open_price = price
        self.open_reason = open_reason
        self.stoploss = stoploss
        self.takeprofit = takeprofit
        dd = this_day.get_dict()
        dd['stoploss'] = stoploss
        dd['takeprofit'] = takeprofit
        self.data.append(dd)
        self.low = this_day.close_price
        self.high = this_day.close_price
        self.open_datetime = this_day.datetime


    def close_trade(self, this_day, price, close_reason):
        self.close_price = price
        self.close_datetime = this_day.datetime

        #delta = round(self.close_price - self.open_price, 2)
        delta = self.close_price - self.open_price
        if self.direction:
            if self.direction == 'BUY':
                self.profit = delta
                self.drawdown = self.open_price - min([d['low'] for d in self.data])
            elif self.direction == 'SELL':
                self.profit = -1*delta
                self.drawdown = max([d['high'] for d in self.data])-self.open_price

        self.is_open = False
        self.is_closed = True
        self.close_reason = close_reason
        
       


    def update_trade(self, this_day):
        self.days += 1

        dd = this_day.get_dict()
        dd['stoploss'] = self.stoploss
        dd['takeprofit'] = self.takeprofit
        self.data.append(dd)

        if this_day.high_price > self.high:
            self.high = this_day.high_price
        if this_day.low_price < self.low:
            self.low = this_day.low_price

        if self.direction == 'BUY':
            if this_day.low_price <= self.stoploss:
                self.close_trade(this_day, self.stoploss, 'SL')
            if this_day.high_price >= self.takeprofit:
                self.close_trade(this_day, self.takeprofit, 'TP')
        elif self.direction == 'SELL':
            if this_day.high_price >= self.stoploss:
                self.close_trade(this_day, self.stoploss, 'SL')
            if this_day.low_price <= self.takeprofit:
                self.close_trade(this_day, self.takeprofit, 'TP')

        if not self.is_closed:
            self.profit = this_day.close_price - self.open_price




