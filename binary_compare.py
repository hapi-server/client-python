import time
import os
import numpy as np
import urllib
from datetime import datetime
import matplotlib.pyplot as plt 

file = 'scalar'
base = 'http://mag.gmu.edu/TestData/hapi';
urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',file + '.fbin')
urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + 'int' + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',file + 'int' + '.fbin')
urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=binary',file + '.bin')

###############################################################################
# Using mixed double and int data in fbinary
tic = time.time()
f = open(file+'int'+'.fbin', 'rb')
t = f.read(21)
n = int(t[0])
dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
zerotime = dt.toordinal()
f.seek(21, os.SEEK_SET)
dt = [('time', '<d'),('data',np.int32)]
dtype = np.dtype(dt)
data2  = np.fromfile(f, dtype)
#print data2
f.close
data2 = data2.astype( [('time', '<d'),('data','<d')]).view('<d')
size = 2
data2 = np.reshape(data2, [len(data2) / size, size])
toc = time.time()
tf0 = toc-tic;
print 'fbin w/ints total: %.4fs' % (toc-tic)
plt.figure(0)
plt.clf()
plt.plot(data2[:,0],data2[:,1]/1000)
plt.show()
plt.xlabel('Seconds since ' + START)

# Using double only data in fbinary
tic = time.time()
f = open(file+'.fbin', 'rb')
t = f.read(21)
n = int(t[0])
dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
zerotime = dt.toordinal()
f.seek(21, os.SEEK_SET)
data = np.fromfile(f, dtype=np.dtype('<d'))
#print data
f.close
size = 2
data = np.reshape(data, [len(data) / size, size])
toc = time.time()
tf = toc-tic;
print 'fbin total:        %.4fs' % (toc-tic)
plt.figure(0)
#plt.clf()
plt.plot(data[:,0],data[:,1],color='red')
plt.show()
plt.xlabel('Seconds since ' + START)
###############################################################################

###############################################################################
# Using HAPI binary
xt = [0,0,0];
dt = np.dtype([('year','S4'),('dash1','S1'),('month','S2'),('dash2','S1'),('day','S2'),('T','S1'),('hour','S2'),('colon1','S1'),('minute','S2'),('colon2','S1'),('second','S6'),('null','S1'),('data','double')])
tic = time.time()
fpo = np.memmap(file+'.bin', dt, mode='r', shape=86400,offset=0)
toc = time.time()
xt[0] = toc-tic
print 'bin memmap:        %.4fs' % (toc-tic)

tic = time.time()
yr = fpo['year'].astype(np.int)
mo = fpo['month'].astype(np.int)
dy = fpo['day'].astype(np.int)
hr = fpo['hour'].astype(np.int)
mn = fpo['minute'].astype(np.int)
sc = fpo['second'].astype(np.float)

t = []
if False:
    # Would need loop like this, which increased total time by factor of 10
    for i in range(len(yr)):
        fs = (hr[i]*60.*60. + mn[i]*60. + sc[i])/86400.
        t.append(fs + datetime(yr[i], mo[i], dy[i]).toordinal() )
else:
    # For now do this and assume no change in date.
    t = hr*60.*60. + mn*60. + sc
toc = time.time()
xt[1] = toc-tic
print 'bin extract time:  %.4fs' % (toc-tic)
tic = time.time()
d = fpo['data']
toc = time.time()
xt[2] = toc-tic
print 'bin extract data:  %.4fs' % (toc-tic)


plt.figure(0)
#plt.clf()
plt.plot(t,d,color='green')
plt.show()
plt.xlabel('Seconds since ' + START)
###############################################################################


print 'bin total:         %.4fs' % (xt[0] + xt[1] + xt[2])

print ''
print 'bin/fbin         : %.4f' % ((xt[0] + xt[1] + xt[2])/tf)
print 'bin/(fbin w/ints): %.4f' % ((xt[0] + xt[1] + xt[2])/tf0)
