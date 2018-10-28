from assets import Asset
from reader import ask_av_history, get_history_path

symbols = ['FB', 'AMZN', 'F', 'KO']
canvas = []

def load_data(symbols, itype, timeframe):
    assets = []
    missing = []
    path = get_history_path(itype, timeframe)
    for s in symbols:
        a = Asset()
        try:
            a.load_av_data(path, s)
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
                a.load_av_data(path, m)
            except FileNotFoundError:
                print('DATA LOADING ERROR')
            else:
                assets.append(a)
    return (assets)

print(load_data(symbols, 'ASTOCKS', 'DAILY'))
