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

from matplotlib import rc_context
# Ubuntu - type1cm package needed. Otherwise text.usetex fails
rcParams = {'text.usetex': False}
with rc_context(rc=rcParams):
    if rcParams['text.usetex']:
        try:
            fig = timeseries(t, y)
        except RuntimeError as e:
            print('------')
    else:
        fig = timeseries(t, y)        
    #fig.show()
    fig.set_facecolor('gray')
    fig.axes[0].set_facecolor('yellow')
fig.axes[0].set_ylabel('y label')

# If any parts of the image are changed from the command line (i.e.,
# after it has been rendered), you must enter "fig" on the command line
# to re-render the image.
