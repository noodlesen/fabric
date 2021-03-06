# EVOLUTION ALGORITHM FOR TESTING

from random import randint
from copy import deepcopy
import json
from multitester import multitest
#from assets import Asset
from config import TS
from datetime import datetime, timedelta


def mutate(p, nm):
    new_params = TS.get_random_ts_params()
    numbers = []
    l = len(p.items())

    n = randint(1, round(nm/100*l))
    while len(numbers) < n:
        nn = randint(1, l)
        if nn not in numbers:
            numbers.append(nn)
    np = deepcopy(p)
    x = 1
    for k, v in new_params.items():
        if x in numbers:
            np[k] = new_params[k]
        x += 1
    return np


def generate(f, generations_count, mutations, outsiders, depth, strategy, **kwargs):

    time_limit = kwargs.get('time_limit', None)

    now = datetime.now()
    stamp = TS.ts_name()+"-%d-%d-%d-%d.txt" % (now.day, now.month, now.hour, now.minute)

    cut = kwargs.get('cut', False)

    default_ir = {
        "DAYS_MAX": 0,
        "LOSES": 0,
        "MAX_LOSES_IN_A_ROW": 0,
        "MAX_LOSS_PER_TRADE": 0,
        "MAX_PROFIT_PER_TRADE": 0,
        "MAX_WINS_IN_A_ROW": 0,
        "PROFIT": 0,
        "ROI": 0,
        "TRADES": 1,
        "WINRATE": 0,
        "WINS": 0,
        "WINS_TO_LOSES": 0,
        "MAX_DRAWDOWN": 0
    }

    initial = kwargs.get('initial_params', None)

    initial_result = multitest(f, initial, **kwargs)

    if initial_result is None:
        initial_result = default_ir
    survivor = {'input': initial, 'output': initial_result}
    print(json.dumps(survivor['input'], sort_keys=True, indent=4))

    elapsed_times = []

    for n in range(1, generations_count+1):
        print()
        print('GEN', n)
        start_time = datetime.now()
        offs = []
        for d in range(0, depth):
            m = mutate(survivor['input'], mutations)
            ta = multitest(f, m, **kwargs)
            if ta:
                offs.append({'input': m, 'output': ta})

        for x in range(0, outsiders):
            m = TS.get_random_ts_params()
            ta = multitest(f, m, **kwargs)
            if ta:
                offs.append({'input': m, 'output': ta})

        for off in offs:

            if off['output']['TRADES'] > 0:
                off_wr = (off['output']['WINS'])/off['output']['TRADES']
                survivor_wr = (survivor['output']['WINS'])/survivor['output']['TRADES']

                if strategy == 'ROI_AND_WINRATE':
                    cond = off['output']['ROI']*off_wr/(off['output']['MAX_DRAWDOWN']+0.0001) > survivor['output']['ROI']*survivor_wr/(survivor['output']['MAX_DRAWDOWN']+0.0001) and off['output']['VERS']>0.4

                if strategy == 'PROFIT_INVEST_LIMIT':
                    cond = off['output']['PROFIT'] > survivor['output']['PROFIT'] and  off['output']['TOTAL_INV'] <=50000

                if strategy == 'FX':
                    off_dd = off['output']['MAX_DRAWDOWN']
                    sur_dd = survivor['output']['MAX_DRAWDOWN']
                    cond = off['output']['ROI']*off_wr/(off_dd+0.0001) > survivor['output']['ROI']*survivor_wr/(sur_dd+0.0001) and off['output']['VERS']==1

                if cond:
                    survivor = deepcopy(off)

        print(json.dumps(survivor['input'], sort_keys=True, indent=4))
        print(json.dumps(survivor['output'], sort_keys=True, indent=4))
        print('\n>>>>')
        print('\nWINRATE','%.2f' % survivor_wr)
        print('PROFIT', '%.2f' % survivor['output']['PROFIT'])
        print('ROI', '%.2f' % survivor['output']['ROI'])
        now = datetime.now()
        elapsed = (now-start_time).total_seconds()
        elapsed_times.append(elapsed)
        average = sum(elapsed_times)/len(elapsed_times)
        print('elapsed:', int(elapsed), 'average:', int(average))
        gens_to_go = generations_count - n 
        if time_limit:
            if ((now-start_time)+timedelta(seconds=average)).seconds//60 > time_limit:
                print('STOP TIME '+ datetime.strftime(now, '%H:%M'))
                break
            else:
                togo = (start_time + timedelta(minutes=time_limit) - now)
                est_gens = togo.seconds // average
                est_gens = gens_to_go if est_gens>gens_to_go else est_gens
                print('est. gens: ', est_gens)
        else:
            est_time = now+timedelta(seconds=average*gens_to_go)
            print('est. finish: ', datetime.strftime(est_time, '%H:%M'))
            
        
        print()

    if kwargs.get('report', False):
        
        names = [stamp, 'recent.txt']
        for n in names:
            with open('results/'+n, 'w') as report:
                report.write(json.dumps(survivor, sort_keys=True, indent=4))

        kwargs['draw'] = True
        kwargs['verbose'] = True
        multitest(f, survivor['input'], **kwargs)

        print(json.dumps(survivor['output'], sort_keys=True, indent=4))

    return(survivor)
