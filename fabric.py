from assets import Asset
from reader import ask_av_history
from datetime import datetime


class Fabric():

    def __init__(self):
        self.canvas = []
        self.helpers = []
        self.timeframe = None
        self.checked = False
        self.loaded = False

    def load_data(self, symbols, itype, timeframe):
        assets = []
        missing = []
        for s in symbols:
            a = Asset()
            try:
                a.load_av_data(s, itype, timeframe)
            except FileNotFoundError:
                missing.append(s)
            else:
                assets.append(a)

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
                    assets.append(a)

        self.timeframe = timeframe
        self.loaded = True
        self.canvas = assets
        return (assets)

    def trim(self):
        max_dt_from = max([a.dt_from for a in self.canvas])
        min_dt_to = min([a.dt_to for a in self.canvas])
        for a in self.canvas:
            a.trim(max_dt_from, min_dt_to)

    def check(self):  # checks canvas integrity
        ok = True
        if len(set([a.count for a in self.canvas]))!=1:
            ok = False
        else:
            for i in range(max([len(a.data) for a in self.canvas])):
                if len(set([a.data[i]["datetime"] for a in self.canvas]))!=1:
                    ok=False
        print(ok)



f = Fabric()
f.load_data(['GBPUSD', 'USDJPY', 'EURUSD'], 'FX', 'DAILY')
#f.load_data(['KO','F','T', 'INTC', 'AA'], 'ASTOCKS', 'DAILY')
for a in f.canvas:
    print(len(a.data))
#f.trim()

for a in f.canvas:
    print(len(a.data))

f.check()


