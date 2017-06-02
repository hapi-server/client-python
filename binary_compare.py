import time
import os
import numpy as np
import urllib
from datetime import datetime

file = 'scalar'
base = 'http://mag.gmu.edu/TestData/hapi';
urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',file + '.fbin')
urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + 'int' + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',file + 'int' + '.fbin')
urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=binary',file + '.bin')

# Using mixed double and int data in fbinary
tic = time.time()
f = open(file+'int'+'.fbin', 'rb')
t = f.read(21)
n = int(t[0])
dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
zerotime = dt.toordinal()
f.seek(21, os.SEEK_SET)
dt = [('time', '<d'),('data','<i4')]
dtype = np.dtype(dt)
data2  = np.fromfile(f, dtype)
f.close
data2 = data2.astype( [('time', '<f8'),('data','<f8')]).view('<f8')
size = 2
data2 = np.reshape(data2, [len(data2) / size, size])
toc = time.time()
tf = toc-tic;
print 'fbin2 total:      %.4f' % (toc-tic)

# Using double only data in fbinary
tic = time.time()
f = open(file+'.fbin', 'rb')
t = f.read(21)
n = int(t[0])
dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
zerotime = dt.toordinal()
f.seek(21, os.SEEK_SET)
data = np.fromfile(f, dtype=np.dtype('<d'))
f.close
size = 2
data = np.reshape(data, [len(data) / size, size])
toc = time.time()
tf = toc-tic;
print 'fbin total:       %.4f' % (toc-tic)

xt = [0,0,0];
dt = np.dtype([('year','S4'),('dash1','S1'),('month','S2'),('dash2','S1'),('day','S2'),('T','S1'),('hour','S2'),('colon1','S1'),('minute','S2'),('colon2','S1'),('second','S6'),('null','S1'),('data','double')])
tic = time.time()
fpo = np.memmap(file+'.bin', dt, mode='r', shape=86400,offset=0)
toc = time.time()
xt[0] = toc-tic
print 'bin memmap:       %.4f' % (toc-tic)

tic = time.time()
zt = []
yr = fpo['year'].astype(np.int)
mo = fpo['month'].astype(np.int)
dy = fpo['day'].astype(np.int)
hr = fpo['hour'].astype(np.int)
mn = fpo['minute'].astype(np.int)
sc = fpo['second'].astype(np.float)
# datetime is not vectorized as datenum is in MATALB
# Would need a vectorized version of calculation similar to  this
# zt = 365*fpo['year'].astype(np.float) + 30*fpo['month'].astype(np.float) + fpo['day'].astype(np.float)
# But loop below does not seem as slow as expected ...
for i in range(len(yr)):
    zt.append(datetime(yr[i], mo[i], dy[i]).toordinal())
    #zt[i] = ... add fraction of day using hr, mn, sec.
toc = time.time()
xt[1] = toc-tic
print 'bin extract time: %.4f' % (toc-tic)

tic = time.time()
d = fpo['data']
toc = time.time()
xt[2] = toc-tic
print 'bin extract data: %.4f' % (toc-tic)

print 'bin/fbin speed:   %.4f' % ((xt[0] + xt[1] + xt[2])/tf)