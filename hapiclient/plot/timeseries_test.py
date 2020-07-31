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

tn = 1

if tn == 1:
    title = 'test #' + str(tn) + ' All NaN values'
    timeseries(t, np.nan*y, title=title)

if tn == 2:
    from matplotlib import rc_context
    # Ubuntu - type1cm package needed. Otherwise text.usetex fails
    rcParams = {'text.usetex': True}
    with rc_context(rc=rcParams):
        try:
            title = 'test #' + str(tn) + ' text.usetex=True w/o RuntimeError'
            fig = timeseries(t, y, title=title)
        except RuntimeError:
            failed = True
            pass

    rcParams = {'text.usetex': False}
    if failed:
        with rc_context(rc=rcParams):
            title = 'test #' + str(tn) + ' text.usetex=True gave RuntimeError'
            fig = timeseries(t, y, title=title)

#y = np.vstack((y, y)).T
