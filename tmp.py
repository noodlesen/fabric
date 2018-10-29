from fabric import Fabric
from datetime import datetime

f = Fabric()
f.load_data(['USDJPY'],'FX','DAILY')
f.draw('USDJPY', datetime(2018,1,1), datetime(2018,10,29))
