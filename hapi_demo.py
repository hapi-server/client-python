import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from hapi import hapi

Servers = hapi();

hapi(list=True)

SERVER   = 'http://mag.gmu.edu/TestData/hapi';
#SERVER = 'http://localhost:8999/hapi'
DATASET = 'TestData'
PARAMETERS = 'scalar'
START = '1970-01-01'
STOP = '1970-01-01T00:20:00'

meta = hapi(SERVER, DATASET)

data,meta = hapi(SERVER, DATASET, PARAMETERS, START, STOP)

fig = plt.figure(0)
fig.clf()
ax = fig.add_subplot(111)
ax.plot(data[:,0],data[:,1])

x_major = matplotlib.dates.AutoDateLocator(minticks=2,maxticks=10, interval_multiples=True)
x_fmt = matplotlib.dates.AutoDateFormatter(x_major)
x_fmt.scaled[1/(24.*60.)] = '%M:%S'
ax.xaxis.set_major_locator(x_major)
ax.xaxis.set_major_formatter(x_fmt)

x_minor = matplotlib.dates.HourLocator(byhour = range(0,25,1))
ax.xaxis.set_minor_locator(x_minor)
ax.set_xlabel("Time on " + START)

ax.grid()
plt.show()