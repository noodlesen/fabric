from fabric import Fabric

f = Fabric()
f.load_data(['KO','F','T', 'INTC'], 'ASTOCKS', 'DAILY')

f.trim()
if f.check():
    f.set_range_from_last(1000)

    for i in range(1000):

        #print(' '.join(['%s %.2f' % (k, f.get(k).close_price) for k in f.canvas.keys()]))
        fg = f.last('INTC',5, figure=True)
        if fg.is_harami():
            print(f.get('INTC').datetime, 'HARAMI')
        f.next()
