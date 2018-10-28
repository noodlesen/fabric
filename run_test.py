from config import TS
from tester import test
#from reader import load_settings_from_report
from assets import Asset
from datetime import datetime

RANDOM = True

if RANDOM:
    params = TS.get_random_ts_params()
# else:
#     params = load_settings_from_report('evo.txt')

# chart = Asset()
# chart.load_av_history('AVHD', 'AAPL')
# chart.range_from_last(750)

from fabric import Fabric
f = Fabric()
#f.load_data(['AAPL','KO','F','T', 'INTC', 'AA'], 'ASTOCKS', 'DAILY')
f.load_data(['USDJPY'], 'FX', 'DAILY')
f.trim()
f.cut_last(500)
if f.check():
    res = test(f, 'USDJPY', params, verbose=True, draw=True)


    for k,v in res.items():
        print(k, v)
    print()
    print ('%r(%d)' % (res['PROFIT'],res['TRADES']))

