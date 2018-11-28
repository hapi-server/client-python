from hapiclient.plot.timeseries import timeseries
from datetime import datetime, timedelta
import numpy as np

# Time axes
start = datetime(1970, 1, 1)
tb0 = [start,start+timedelta(seconds=2.5)]
tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]

T = 20
t = np.array([start + timedelta(seconds=i) for i in range(T)])        
y = np.arange(0, T)
y = np.vstack((y, y)).T
opts = {'style': 'seaborn-dark', 'rc': {'figure.facecolor': 'green'}}
timeseries(t, y, **opts)
timeseries(t, y)
 