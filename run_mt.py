from fabric import Fabric
from multitester import multitest
from reader import load_settings_from_report


#symbols = ['FE', 'SCI', 'GTN', 'MSGN', 'USM', 'DISCA', 'OGE', 'AROW', 'EXPO', 'TLP', 'MMT', 'LION', 'ATI', 'MYGN']
symbols = ['DIS', 'WFC', 'VZ', 'T', 'KO']
f = Fabric()
f.load_data(['ADBE'], 'ASTOCKS', 'DAILY')
f.trim()
if f.check():

    f.set_range_from_last(500)
    params = load_settings_from_report('results/TR110.txt')
    r = multitest(f, params, draw=True, verbose=True)
    print(r)



