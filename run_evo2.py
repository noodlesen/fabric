# LAUNCHER FOR EVO ALGORITHM

from evo2 import generate
from reader import load_settings_from_report
from config import TS
from fabric import Fabric


initial_params = load_settings_from_report('results/P50T3Y.txt')
#initial_params = TS.get_random_ts_params()

CHANNEL = ['DIS', 'WFC', 'VZ', 'T', 'KO']
TRENDY = ['BA', 'ADBE', 'CAT', 'INTC', 'AAPL']
OTHER1 = ['AXP', 'C', 'CSCO', 'DIS']
OTHER2 = ['EBAY', 'F', 'FB', 'GS', 'HD', 'HOG', 'HPQ', 'IBM', 'ITX', 'JNJ']
NEW = ['FE', 'SCI', 'GTN', 'MSGN', 'USM', 'DISCA', 'OGE', 'AROW', 'EXPO', 'TLP', 'MMT', 'LION', 'ATI', 'MYGN']

symbols = []
symbols.extend(TRENDY)
symbols.extend(CHANNEL)
symbols.extend(OTHER1)
symbols.extend(OTHER2)
symbols.extend(NEW)

GENERATIONS_COUNT = 50
MUTATIONS = 70
OUTSIDERS = 5
DEPTH = 10
#STRATEGY = 'FX'
STRATEGY = 'PROFIT_INVEST_LIMIT'
TIME_LIMIT =570 #5  # MINUTES

f = Fabric()
#f.load_data(['GBPUSD', 'USDJPY', 'EURUSD', 'USDCHF'], 'FX', '60MIN')
f.load_data(symbols, 'ASTOCKS', 'DAILY')
f.trim()
f.set_range_from_last(750)
if f.check():
    generate(f, GENERATIONS_COUNT, MUTATIONS, OUTSIDERS, DEPTH, STRATEGY, initial_params=initial_params, report=True, time_limit=TIME_LIMIT)
