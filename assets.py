from reader import read_av_json
import datetime





class Asset():

    def __init__(self, **kwargs):
        self.data = kwargs.get('data', [])
        self.symbol = kwargs.get('symbol', None)
        self.timeframe = kwargs.get('timeframe', None)
        self.itype = kwargs.get('itype', None)
        self.loaded = False
        self.count = 0
        self.dt_from = None
        self.dt_to = None

    def __str__(self):
        f = datetime.datetime.strftime(self.dt_from, '%Y-%m-%d %H:%M:%S')
        t = datetime.datetime.strftime(self.dt_to, '%Y-%m-%d %H:%M:%S')
        return ('Asset: %s %s (%s) %s->%s' % (self.symbol, self.timeframe, self.itype, f, t))

    def load_av_data(self, symbol, itype, timeframe):
        self.data = read_av_json(symbol, itype, timeframe)
        self.dt_from = self.data[0]['datetime']
        self.dt_to = self.data[self.count-1]['datetime']
        self.symbol = symbol
        self.timeframe = timeframe
        self.itype = itype
        self.count = len(self.data)
        self.loaded = True

    def trim(self, from_dt, to_dt):
        self.data = [d for d in self.data if d["datetime"] >= from_dt and d["datetime"] <= to_dt]
        self.count = len(self.data)
        self.dt_from = self.data[0]['datetime']
        self.dt_to = self.data[self.count-1]['datetime']

    def cut_last(self, n):
        self.data = self.data[-1*n:]
        self.count = len(self.data)





