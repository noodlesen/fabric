# LAUNCHER FOR EVO ALGORITHM

from evo import generate
from reader import load_settings_from_report
from config import TS
from fabric import Fabric 


#initial_params = load_settings_from_report('results/TRENDY109.txt')
initial_params = TS.get_random_ts_params()

CHANNEL = ['DIS', 'WFC', 'VZ', 'T', 'KO']
TRENDY = ['BA', 'ADBE', 'CAT', 'INTC', 'AAPL']
OTHER1 = ['AXP', 'C', 'CSCO', 'DIS']
OTHER2 = ['EBAY', 'F', 'FB', 'GS', 'HD', 'HOG', 'HPQ', 'IBM', 'ITX', 'JNJ']
NEW = ['FE', 'SCI', 'GTN', 'MSGN', 'USM', 'DISCA', 'OGE', 'AROW', 'EXPO', 'TLP', 'MMT', 'LION', 'ATI', 'MYGN']

symbols = []
symbols.extend(TRENDY)
#symbols.extend(CHANNEL)
# symbols.extend(OTHER1)
# symbols.extend(OTHER2)
# symbols.extend(NEW)

GENERATIONS_COUNT = 5
MUTATIONS = 70
OUTSIDERS = 5
DEPTH = 10
STRATEGY = 'MAX_ROI_MAX_DIV'

f = Fabric()
f.load_data(['USDJPY','EURUSD','GBPUSD'], 'FX', 'DAILY')
f.trim()
f.set_range_from_last(250)
if f.check():
    generate(f, GENERATIONS_COUNT, MUTATIONS, OUTSIDERS, DEPTH, STRATEGY, initial_params=initial_params, report=True)