# DATA READING LIBRARY

import json
from keys import AV_API_KEY
import requests
from time import sleep
import datetime
import os


def get_history_path(itype, timeframe):
    path =  'HD/%s/%s/' % (itype,timeframe)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def read_av_json(symbol, itype, timeframe):
    
    path = get_history_path(itype, timeframe)+symbol+'.json'

    if itype == 'ASTOCKS':
        if timeframe == 'DAILY':
            k = "Time Series (Daily)"
    elif itype == 'FX':
        if timeframe == 'DAILY':
            k = "Time Series FX (Daily)"

    with open(path, 'r') as f:
        data = json.loads(f.read())[k]

    datalist = [{k: data[k]} for k in sorted(data.keys())]


    data =[]
    for d in datalist:
        k = list(d.keys())[0]

        bar = {
            "open": float(d[k]['1. open']),
            "high": float(d[k]['2. high']),
            "low": float(d[k]['3. low']),
        }

        if timeframe in ['DAILY', 'WEEKLY', 'MONTHLY']:
            bar["datetime"] = datetime.datetime.strptime(k, '%Y-%m-%d')
        else:
            bar["datetime"] = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')

        if itype == 'ASTOCKS':
            bar["close"] = float(d[k]['5. adjusted close'])
            bar["volume"] = int(d[k]['6. volume'])

        elif itype == 'FX':
            bar["close"] = float(d[k]['4. close'])
            bar["volume"] = 0

    return data



def ask_av_history(symbols, itype, timeframe):
    path = get_history_path(itype, timeframe)
    if itype=='ASTOCKS':
        if timeframe == 'DAILY':
            url_temp = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&outputsize=full&apikey='
    elif itype == 'FX':
        if timeframe == 'DAILY':
            url_temp = 'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=%s&to_symbol=%s&outputsize=full&apikey='
    SLEEP = 10
    for symbol in symbols:
        print ('requesting '+symbol)
        if itype == 'ASTOCKS':
            url = url_temp % symbol
        elif itype == 'FX':
            url = url_temp % (symbol[:3],symbol[-3:])

        response = requests.request('GET',url+AV_API_KEY)
        print(response.status_code)
        if response.status_code == requests.codes.ok:
            print ('OK')
            with open(path+symbol+'.json', 'w') as f:
                f.write(response.text)
            for n in range(SLEEP):
                sleep(1)
                print('.')
            print()


def ask_av_indi(s,i):
    url="https://www.alphavantage.co/query?function=%s&symbol=%s&interval=daily&time_period=10&apikey=" % (i,s)
    response = requests.request('GET',url+AV_API_KEY)
    print(response.status_code)
    if response.status_code == requests.codes.ok:
        print ('OK')
        with open('INDI/'+s+i+'.json', 'w') as f:
            f.write(response.text)






