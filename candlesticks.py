
class Candle():

    def __init__(self, **kwargs):
        bar = kwargs.get('bar', None)
        if bar:
            self.high_price = bar['high']
            self.low_price = bar['low']
            self.open_price = bar['open']
            self.close_price = bar['close']
            self.volume = bar.get('volume', 0)
            self.date = bar.get('date', None)
            self.time = bar.get('time', None)
        else:
            self.high_price = kwargs['high']
            self.low_price = kwargs['low']
            self.open_price = kwargs['open']
            self.close_price = kwargs['close']
            self.volume = kwargs.get('volume', 0)
            self.date = kwargs.get('date', None)
            self.time = kwargs.get('time', None)

    def __str__(self):
        return ('%s %s O:%r H:%r L: %r C: %r V: %d' % (self.date, self.time, self.open_price, self.high_price, self.low_price, self.close_price, self.volume))

    def get_dict(self):
        return {
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume,
        }

    def is_bullish(self):
        return self.close_price > self.open_price

    def is_bearish(self):
        return self.close_price < self.open_price

    def is_doji(self):
        return self.close_price == self.open_price

    def body_size(self):
        return abs(self.close_price - self.open_price)

    def candle_size(self):
        return self.high_price - self.low_price

    def body_to_candle(self):
        try:
            return self.body_size()/self.candle_size()
        except:
            return 0

    def close_at_percent(self):
        try:
            return (self.close_price-self.low_price)/self.candle_size()*100
        except:
            return 0

    def open_at_percent(self):
        try:
            return (self.open_price-self.low_price)/self.candle_size()*100
        except:
            return 0

    def body_high(self):
        return self.open_price if self.is_bearish() else self.close_price

    def body_low(self):
        return self.open_price if self.is_bullish() else self.close_price

    def high_tail(self):
        return self.high_price - self.body_high()

    def low_tail(self):
        return self.body_low() - self.low_price

    def high_tail_to_candle(self):
        try:
            return self.high_tail()/self.candle_size()
        except:
            return 0

    def low_tail_to_candle(self):
        try:
            return self.low_tail()/self.candle_size()
        except:
            return 0

    def is_hammer(self):
        return self.low_tail() > self.body_size()*2 and self.high_tail() < self.low_tail()/4

    def is_shooting_star(self):
        return self.high_tail() > self.body_size()*2 and self.low_tail() < self.high_tail()/4


class Figure():

    def __init__(self, **kwargs):
        candles = kwargs.get('candles', None)
        raw = kwargs.get('raw', None)

        self.candles = []

        if candles:
            self.candles = candles
        elif raw:
            for r in raw:
                self.candles.append(Candle(bar=r))

    def summary(self, **kwargs):
        last = kwargs.get('last', None)
        candles = self.candles[-last:] if last else self.candles
        o = candles[0].open_price
        c = candles[-1].close_price
        h = max([cn.high_price for cn in candles])
        l = min([cn.low_price for cn in candles])
        return Candle(open=o, high=h, low=l, close=c)

    def is_harami(self):
        if self.candles[-1].body_high() < self.candles[-2].body_high() and self.candles[-1].body_low() > self.candles[-2].body_low():
            return True
        else:
            return False

    def is_harami_breakup(self):
        f = Figure(candles=self.candles[:-1])
        if f.is_harami() and self.candles[-1].close_price > self.candles[-3].body_high():
            return True
        else:
            return False

    def is_breakup(self, **kwargs):
        last = kwargs.get('last', None)
        candles = self.candles[-last:] if last else self.candles
        return candles[-1].close_price > max([cn.high_price for cn in candles[:-1]])

    def is_breakdown(self, **kwargs):
        last = kwargs.get('last', None)
        candles = self.candles[-last:] if last else self.candles
        return candles[-1].close_price < min([cn.low_price for cn in candles[:-1]])

    def is_top_fractal(self):
        candles = self.candles[-5:]
        return candles[-3].high_price == max([c.high_price for c in candles])

    def is_bottom_fractal(self):
        candles = self.candles[-5:]
        return candles[-3].low_price == min([c.low_price for c in candles])







