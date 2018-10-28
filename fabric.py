from assets import Asset
from reader import ask_av_history, get_history_path


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
        path = get_history_path(itype, timeframe)
        for s in symbols:
            a = Asset()
            try:
                a.load_av_data(s, itype, timeframe)
            except FileNotFoundError:
                missing.append(s)
            else:
                assets.append(a)

        if missing:
            print ('Missing: ', ', '.join(missing) )
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
        return (assets)

f = Fabric()
symbols = ['FB', 'AMZN', 'F', 'KO']
print(f.load_data(['GBPUSD'], 'FX', 'DAILY'))
