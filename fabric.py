from assets import Asset
from reader import ask_av_history
from candlesticks import Candle, Figure
from datetime import datetime

class Timeline():
    def __init__(self):
        self.data = []
        self.pointer = 0
        self.range_from = 0
        self.count = len(self.data)
        self.range_to = self.count-1


class Fabric(Timeline):

    def __init__(self):
        self.pointer = 0
        self.range_from = 0
        self.count = 0
        self.range_to = self.count-1
        self.canvas = {}
        self.helpers = []
        self.timeframe = None
        self.checked = False
        self.loaded = False

    ###METHODS FROM TIMELINE

    def reset(self):
        self.pointer = self.range_from

    def set_to_last(self):
        self.pointer = self.range_to

    def reset_range(self):
        self.range_from = 0
        self.range_to = self.count - 1
        self.range = self.range_to - self.range_from + 1
        self.pointer = 0

    def range_from_last(self, n):
        self.range_from = self.count - n - 1
        self.range_to = self.count - 1
        self.range = self.range_to - self.range_from + 1
        self.pointer = self.range_from

    def set(self, n):
        self.pointer = n

    def forth(self, n=1):
        self.pointer += n

    def back(self, n=1):
        self.pointer -= n

    def next(self):
        self.pointer += 1

    def prev(self):
        self.pointer -= 1

    ####

    def as_list(self):
        return list(self.canvas.values())

    def assets_number(self):
        return len(self.as_list())

    def load_data(self, symbols, itype, timeframe):
        assets = {}
        missing = []
        for s in symbols:
            a = Asset()
            try:
                a.load_av_data(s, itype, timeframe)
            except FileNotFoundError:
                missing.append(s)
            else:
                assets[s] = a

        if missing:
            print ('Missing: ', ', '.join(missing))
            print ('Downloading...')
            ask_av_history(missing, itype, timeframe)
            for m in missing:
                try:
                    a.load_av_data(m, itype, timeframe)
                except FileNotFoundError:
                    print('DATA LOADING ERROR')
                else:
                    assets[m] = a

        self.timeframe = timeframe
        self.loaded = True
        self.canvas.update(assets)
        self.reset_range()

    def trim(self):
        max_dt_from = max([a.dt_from for a in self.as_list()])
        min_dt_to = min([a.dt_to for a in self.as_list()])
        for a in self.as_list():
            a.trim(max_dt_from, min_dt_to)
        self.count = self.as_list()[0].count
        self.reset_range()

    def check(self):  # checks canvas integrity
        ok = True
        if len(set([a.count for a in self.as_list()]))!=1:
            ok = False
        else:
            for i in range(max([len(a.data) for a in self.as_list()])):
                if len(set([a.data[i]["datetime"] for a in self.as_list()]))!=1:
                    ok=False
        return ok

    def cut_last(self, n):
        for k,v in self.canvas.items():
            v.cut_last(n)
        self.count = self.as_list()[0].count
        self.reset_range()

    def set_range_from_last(self, n):
        self.range_from=self.count-n
        self.range_to=self.count-1
        self.pointer = self.range_from

    def reserve(self,n):
        self.pointer = n
        self.range_from=self.pointer
        self.range_to=self.count-1



    ## methods from asset VVV
    def last(self, symbol, n, of=0, **kwargs): 
        of = abs(of)
        row = []
        fr = -1*(n-1)-of+self.pointer
        to = 1-of+self.pointer
        row = self.canvas[symbol].data[fr:to]
        if kwargs.get('figure', False):
            return Figure(raw=row)
        else:
            return row

    # get bar by absoute index
    def bar(self, symbol, n=-1):
        p = n if n >= 0 else self.pointer
        return Candle(bar=self.canvas[symbol].data[p])

    # get bar by pointer relative index
    def get(self, symbol, n=0):
        return Candle(bar=self.canvas[symbol].data[self.pointer + n])




# f = Fabric()
# #f.load_data(['GBPUSD', 'USDJPY', 'EURUSD'], 'FX', 'DAILY')
# f.load_data(['KO','F','T', 'INTC', 'AA'], 'ASTOCKS', 'DAILY')
# for a in f.as_list():
#     print(len(a.data))
# f.trim()

# for a in f.as_list():
#     print(len(a.data))

# print(f.check())

# f.cut_last(50)

# for a in f.as_list():
#     print(len(a.data))


