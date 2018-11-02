from fabric import Fabric
from multitester import multitest
from reader import load_settings_from_report


#symbols = ['FE', 'SCI', 'GTN', 'MSGN', 'USM', 'DISCA', 'OGE', 'AROW', 'EXPO', 'TLP', 'MMT', 'LION', 'ATI', 'MYGN']
#symbols =['DIS', 'WFC', 'VZ', 'T', 'KO', 'BA', 'ADBE', 'CAT', 'INTC', 'AAPL', 'AXP', 'C', 'CSCO', 'DIS','EBAY', 'F', 'FB', 'GS', 'HD', 'HOG', 'HPQ', 'IBM', 'ITX', 'JNJ',  'FE', 'SCI', 'GTN', 'MSGN', 'USM', 'DISCA', 'OGE', 'AROW', 'EXPO', 'TLP', 'MMT', 'LION', 'ATI', 'MYGN']
symbols = ['BA', 'ADBE', 'CAT', 'INTC', 'AAPL']
f = Fabric()
f.load_data(symbols, 'ASTOCKS', 'DAILY')
f.trim()
if f.check():

    f.set_range_from_last(500)
    params = load_settings_from_report('results/ALL3R88.txt')
    r = multitest(f, params, draw=True, verbose=True)
    print(r)



