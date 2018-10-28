# DRAWS CANDLESTICKS

from PIL import Image, ImageDraw
from random import randint

BLACK = (0, 0, 0, 0)
WHITE = (255, 255, 255, 0)
RED = (255, 0, 0, 0)
GREEN = (0, 255, 0, 0)


def get_coord(n, context):
    return (context['price_high'] - n)/(context['price_high']-context['price_low'])*context['height']


def candle(o, h, l, c, p, context, draw, **kwargs):

    w = context['width']/context['number']
    left = w*p-w*0.8
    right = w*p-w*0.2
    mid = w*p-w*0.5

    FILL_UP = WHITE
    FILL_DOWN = BLACK
    STROKE = BLACK

    if o < c:
        draw.rectangle([left, get_coord(o, context), right, get_coord(c, context)], FILL_UP, STROKE)
        draw.rectangle([mid-1, get_coord(h, context), mid, get_coord(c, context)], STROKE, STROKE)
        draw.rectangle([mid-1, get_coord(o, context), mid, get_coord(l, context)], STROKE, STROKE)
    else:
        draw.rectangle([left, get_coord(c, context), right, get_coord(o, context)], FILL_DOWN, STROKE)
        draw.rectangle([mid-1, get_coord(h, context), mid, get_coord(o, context)], STROKE, STROKE)
        draw.rectangle([mid-1, get_coord(c, context), mid, get_coord(l, context)], STROKE, STROKE)

    sl = kwargs.get('sl', None)
    if sl:
        draw.rectangle([mid-2, get_coord(sl, context)-2, mid+2, get_coord(sl, context)+2], 'red', 'red')

    tp = kwargs.get('tp', None)
    if tp:
        draw.rectangle([mid-2, get_coord(tp, context)-2, mid+2, get_coord(tp, context)+2], 'blue', 'blue')

    if p in context['marked_positions']:
        for m in context['marks']:
            if m[0] == p:
                draw.ellipse([mid-5, get_coord(m[1], context)-5, mid+5, get_coord(m[1], context)+5], 'green', 'green')


def draw_candles(data, name, context):

    context['marked_positions'] = [m[0] for m in context.get('marks', [])]

    img = Image.new('RGB', (context['width'], context['height'],), (255, 255, 255, 0))

    draw = ImageDraw.Draw(img)

    lowest = 10000000
    highest = 0

    if context['offset'] == 0:
        data_slice = data[-context['number']:]
    else:
        data_slice = data[-context['number']+context['offset']: context['offset']]

    for d in data_slice:
        #print (d)
        if d['high'] > highest:
            highest = d['high']
        if d['low'] < lowest:
            lowest = d['low']

    l = len(data)
    context['price_high'] = highest#*(1.0+l/1000)
    context['price_low'] = lowest#*(1.0-l/1000)

    for i, d in enumerate(data_slice):
        candle(d['open'], d['high'], d['low'], d['close'], i+1, context, draw, sl=d.get('stoploss', None), tp=d.get('takeprofit', None))

    img.save(name+'.jpg', "JPEG")


def draw_plot(data_list, name, **kwargs):

    if kwargs.get('parallel', False):
        new_data_list = []
        width = len(data_list[0])
        for i in range(0, width):
            new_data_list.append([])

        for w in range(0,width):
            for i, d in enumerate(data_list):
                new_data_list[w].append(d[w])

        data_list = new_data_list
        print('PARALLEL')

    maximum = max([max(d) for d in data_list])
    minimum = min([min(d) for d in data_list])
    band = maximum-minimum
    length = len(data_list[0])
    plots = len(data_list)
    print(maximum, minimum, band, length, plots)

    img_width = 1920    
    img_height = 800

    img = Image.new('RGB', (img_width, img_height,), (255, 255, 255, 0))

    draw = ImageDraw.Draw(img)

    for p in range(0,plots):
        color = [BLACK, RED, GREEN][p%3]
        for i,d in enumerate(data_list[p]):
            if i>0:
                startX = (i-1)/length*img_width
                endX = i/length*img_width
                startY = (maximum-data_list[p][i-1])/band*img_height
                endY = (maximum-d)/band*img_height
                draw.line((startX,startY,endX, endY), fill=color, width=1)

    img.save(name+'.jpg', "JPEG")


