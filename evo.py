# EVOLUTION ALGORITHM FOR TESTING

from random import randint
from copy import deepcopy
import json
from tester import test
from assets import Asset
from config import TS
from datetime import datetime


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


def test_all(f, params, **kwargs):
    results = []
    inst_used = 0
    for an, a in f.canvas.items():
            test_res = test(f, an, params, **kwargs)
            if test_res:
                results.append(test_res)
                if test_res['TRADES']:
                    inst_used +=1

    if results:
        wins = sum([r['WINS'] for r in results])
        loses = sum([r['LOSES'] for r in results])
        trades = sum([r['TRADES'] for r in results])
        total_inv = sum([r['TOTAL_INV'] for r in results])
        winrate = wins/trades if trades > 0 else None
        wins_to_loses = wins/loses if loses > 0 else None
        profit = sum([r['PROFIT'] for r in results])
        roi = profit/total_inv*100
        output = {
            'PROFIT': profit,
            'ROI': roi,
            'TRADES': trades,
            'WINS': wins,
            'LOSES': loses,
            'WINS_TO_LOSES': wins_to_loses,
            'WINRATE': winrate,
            'MAX_PROFIT_PER_TRADE': max([r['MAX_PROFIT_PER_TRADE'] for r in results]),
            'MAX_LOSS_PER_TRADE': min([r['MAX_LOSS_PER_TRADE'] for r in results]),
            'MAX_WINS_IN_A_ROW': max([r['MAX_WINS_IN_A_ROW'] for r in results]),
            'MAX_LOSES_IN_A_ROW': max([r['MAX_LOSES_IN_A_ROW'] for r in results]),
            'DAYS_MAX': max([r['DAYS_MAX'] for r in results]),
            'INST_USED': inst_used/len(f.canvas)
        }
        return {
            'ALL': output,
            'PASSES': results
        }
    else:
        return None


def generate(f, generations_count, mutations, outsiders, depth, strategy, **kwargs):

    now = datetime.now()
    stamp = TS.ts_name()+"-%d-%d-%d-%d.txt" % (now.day, now.month, now.hour, now.minute)

    cut = kwargs.get('cut', False)
    # assets = {}
    # for s in symbols:
    #     a = Asset()
    #     a.load_av_history('AVHD', s)
    #     if cut:
    #         a.range_from_last(cut)

    #     assets[s] = a


    default_ir = {

        "ALL": {
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
            "WINS_TO_LOSES": 0
        }

    }

    initial = kwargs.get('initial_params', TS.get_random_ts_params())
    initial_result = test_all(f, initial, **kwargs)
    if initial_result is None:
        initial_result = default_ir
    survivor = {'input': initial, 'output': initial_result}
    print(json.dumps(survivor['input'], sort_keys=True, indent=4))



    for n in range(0, generations_count):
        print('GEN', n)

        offs = []
        for d in range(0, depth):
            m = mutate(survivor['input'], mutations)
            ta = test_all(f, m, **kwargs)
            if ta:
                offs.append({'input': m, 'output': ta})

        for x in range(0, outsiders):
            m = TS.get_random_ts_params()
            ta = test_all(f, m, **kwargs)
            if ta:
                offs.append({'input': m, 'output': ta})

        for off in offs:

            if off['output']['ALL']['TRADES'] > 0:
                off_wr = (off['output']['ALL']['WINS'])/off['output']['ALL']['TRADES']
                survivor_wr = (survivor['output']['ALL']['WINS'])/survivor['output']['ALL']['TRADES']

                if strategy == 'PROFIT_AND_WINRATE':
                    cond = off['output']['ALL']['PROFIT']*off_wr > survivor['output']['ALL']['PROFIT']*survivor_wr and off_wr > 0.5

                elif strategy == 'MAX_PROFIT':
                    cond = off['output']['ALL']['PROFIT'] > survivor['output']['ALL']['PROFIT'] and off_wr > 0.5

                elif strategy == 'MIN_TRADES_MAX_PROFIT':
                    cond = off['output']['ALL']['PROFIT']/off['output']['ALL']['TRADES'] > survivor['output']['ALL']['PROFIT']/survivor['output']['ALL']['TRADES']

                elif strategy == 'MAX_ROI':
                    cond = off['output']['ALL']['ROI'] >= survivor['output']['ALL']['ROI']

                elif strategy == 'MAX_ROI_MAX_DIV':
                    cond = off['output']['ALL']['ROI']*off['output']['ALL']['INST_USED'] >= survivor['output']['ALL']['ROI']*survivor['output']['ALL']['INST_USED']

                elif strategy == 'MAX_ROI_MIN_LOSS':
                    cond = off['output']['ALL']['ROI']/(off['output']['ALL']['MAX_LOSS_PER_TRADE']*-1+1) >= survivor['output']['ALL']['ROI']/(survivor['output']['ALL']['MAX_LOSS_PER_TRADE']*-1+1)

                elif strategy == 'MAX_ROI_FAST_RETURN':
                    d = 120
                    cond = off['output']['ALL']['ROI']/(abs(d-off['output']['ALL']['DAYS_MAX'])+1) >= survivor['output']['ALL']['ROI']/(abs(d-survivor['output']['ALL']['DAYS_MAX'])+1)

                elif strategy == 'EVERYTHING':
                    off_max_loses = off['output']['ALL']['MAX_LOSES_IN_A_ROW']
                    off_max_loses = 0.01 if off_max_loses == 0 else off_max_loses
                    sur_max_loses = survivor['output']['ALL']['MAX_LOSES_IN_A_ROW']
                    sur_max_loses = 0.01 if sur_max_loses == 0 else sur_max_loses
                    off_max_wins = off['output']['ALL']['MAX_WINS_IN_A_ROW']
                    sur_max_wins = survivor['output']['ALL']['MAX_WINS_IN_A_ROW']
                    cond = off['output']['ALL']['PROFIT']/off_max_loses*off_wr*off_max_wins > survivor['output']['ALL']['PROFIT']/sur_max_loses*survivor_wr*sur_max_wins

                if cond:
                    survivor = deepcopy(off)

        print(json.dumps(survivor['input'], sort_keys=True, indent=4))
        print('>>>>')
        print(survivor['output']['ALL']['WINS']/survivor['output']['ALL']['TRADES'])
        print(survivor['output']['ALL']['PROFIT'])
        print(survivor['output']['ALL']['ROI'])
        print()

    if kwargs.get('report', False):
        
        with open('results/'+stamp, 'w') as f:
            f.write(json.dumps(survivor, sort_keys=True, indent=4))

        kwargs['draw'] = True
        kwargs['verbose'] = True
        test_all(assets, survivor['input'], **kwargs)

        print(json.dumps(survivor['output']['ALL'], sort_keys=True, indent=4))

    return(survivor)
