import time
import os
import re
import numpy as np
import urllib
from datetime import datetime
import matplotlib.pyplot as plt 
import pandas
import csv

file = 'scalar'
base = 'http://mag.gmu.edu/TestData/hapi';
START = '1970-01-01'
size = 1;

if False:
    if not os.path.isfile(file+'.csv'):
        urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=csv',file + '.csv')
    if not os.path.isfile(file+'.fcsv'):
        urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fcsv',file + '.fcsv')
    if not os.path.isfile(file+'.bin'):
        urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=binary',file + '.bin')
    if not os.path.isfile(file+'.fbin'):
        urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',file + '.fbin')
    if not os.path.isfile(file+'.fbin2'):
        urllib.urlretrieve(base + '/data/?id=TestData&parameters=' + file + 'int' + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',file + '.fbin2')

plt.figure(0);plt.clf()

###############################################################################
# Read and plot HAPI CSV (jeremy)
tic= time.time()
currentStr="1970-01-01"
t1970= datetime.strptime(currentStr, "%Y-%m-%d").toordinal()-719163
currentDay= t1970 * 86400
for line in open(file + '.csv'):
     if ( line[0:10]==currentStr ):
          r= currentDay + int(line[11:13])*3600 + int(line[14:16])*60 + float(line[17:23])
     else:
         currentStr=line[0:10]
         t1970= datetime.strptime(currentStr, "%Y-%m-%d").toordinal()-719163
         currentDay= t1970 * 86400
toc = time.time()
tcsvj = toc-tic;
print 'csv (faden) tot.:  %.4f\t# HAPI CSV' % tcsvj
###############################################################################

###############################################################################
# Read and plot HAPI CSV (pandas)
tic = time.time()
#dt = [datetime, float]
df = pandas.read_csv(file + '.csv',names=['Time', 'scalar'],date_parser=[0], sep=',')
z = pandas.to_datetime(df['Time'],infer_datetime_format=True)
t  =  z.values.view('<i8')
scalar = df['scalar'].values.view()
toc = time.time()
tcsvp = toc-tic;
print 'csv (pandas) tot.: %.4fs\t# HAPI CSV' % tcsvp
plt.figure(0)
plt.plot(24*t/8.64e13,scalar,color='red')
plt.show()
plt.xlabel('Hours since ' + START)
###############################################################################

###############################################################################
# Read and plot HAPI CSV
# See also https://softwarerecs.stackexchange.com/questions/7463/fastest-python-library-to-read-a-csv-file
tic = time.time()
datacsv =[]
with open(file + '.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    datalist = list(csvreader)

datacsv = np.empty([86400,(size+1)])
# This is the limiter:
for i in range(len(datacsv)):
#for i in range(10):
    dt = datetime.strptime(datalist[i][0], '%Y-%m-%dT%H:%M:%S.%f')
    datacsv[i,0] = dt.toordinal()
    tt = dt.timetuple()
    hr = tt.tm_hour
    mn = tt.tm_min
    sc = tt.tm_sec
    #ms = tt.time_ms Does not exist?!
    fs = re.sub(r'.*\.','','.' + datalist[i][0])
    if (len(fs) > 1):
        fs = float(fs);
    else: fs = 0.
    sod = 3600*hr + 60*mn + sc + fs; # fractional second of day
    datacsv[i,0] = datacsv[i,0] + float(sod)/86400.
    datacsv[i,1] = float(datalist[i][1])

toc = time.time()
tcsv = toc-tic;
print 'csv total:         %.4fs\t# HAPI CSV' % tcsv

plt.figure(0)
plt.plot(24*(datacsv[:,0]-datacsv[0,0]),datacsv[:,1],color='red')
plt.show()
plt.xlabel('Hours since ' + START)
###############################################################################

###############################################################################
# Read and plot fast CSV
# See also https://softwarerecs.stackexchange.com/questions/7463/fastest-python-library-to-read-a-csv-file
tic = time.time()
# Too slow.
#datafcsv = np.loadtxt(file + '.fcsv', delimiter=',')
df = pandas.read_csv(file + '.fcsv', sep=',')
datafcsv = df.values
# Would get correct zero epoch and increment from /info
dt = datetime.strptime('1970-01-01', '%Y-%m-%d')
zerotime = dt.toordinal()
datafcsv[:,0] = zerotime + datafcsv[:,0]/86400.
toc = time.time()
tfcsv = toc-tic;
print 'fcsv total:        %.4fs\t# Proposed fast CSV' % tfcsv

plt.figure(0)
plt.plot(24*(datafcsv[:,0]-datafcsv[0,0]),datafcsv[:,1],color='green')
plt.show()
plt.xlabel('Hours since ' + START)
###############################################################################

###############################################################################
# Using double only data in fast binary
tic = time.time()
f = open(file+'.fbin', 'rb')
t = f.read(21)
n = int(t[0])
dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
zerotime = dt.toordinal()
f.seek(21, os.SEEK_SET)
datafbin = np.fromfile(f, dtype=np.dtype('<d'))
#print data
f.close

datafbin = np.reshape(datafbin, [len(datafbin)/(size+1), (size+1)])
toc = time.time()
tfbin = toc-tic;
print 'fbin total:        %.4fs\t# Proposed binary (all doubles)' % tfbin

plt.figure(0)
plt.plot(datafbin[:,0],datafbin[:,1],color='blue')
plt.show()
plt.xlabel('Seconds since ' + START)
###############################################################################

###############################################################################
# Using mixed double and int data in fast binary 
tic = time.time()
f = open(file+'.fbin2', 'rb')
t = f.read(21)
n = int(t[0])
dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
zerotime = dt.toordinal()
f.seek(21, os.SEEK_SET)
dt = [('time', '<d'),('data',np.int32)]
dtype = np.dtype(dt)
datafbin2  = np.fromfile(f, dtype)
f.close
datafbin2 = datafbin2.astype([('time', '<d'),('data','<d')]).view('<d')
datafbin2 = np.reshape(datafbin2, [len(datafbin2) / (size+1), size+1])
toc = time.time()
tfbin2 = toc-tic;
print 'fbin w/ints total: %.4fs\t# Proposed binary (time dbl, param int)' % tfbin2

plt.figure(0)
plt.plot(datafbin2[:,0],datafbin2[:,1]/1000,color='yellow')
plt.show()
plt.xlabel('Seconds since ' + START)
###############################################################################

###############################################################################
# Using HAPI binary
tbin = [0,0,0];

databin = np.fromfile(f, dtype=np.dtype('<d'))

dt = np.dtype([('year','S4'),('dash1','S1'),('month','S2'),
               ('dash2','S1'),('day','S2'),('T','S1'),('hour','S2'),
                ('colon1','S1'),('minute','S2'),('colon2','S1'),
                ('second','S6'),('null','S1'),('data','double')])
tic = time.time()
# Would need to get shape from reading response size.
fpo = np.memmap(file+'.bin', dt, mode='r', shape=86400,offset=0)
# Could also do this:
#databin = np.fromfile(file + '.bin', dtype=dt)

toc = time.time()
tbin[0] = toc-tic

tic = time.time()
yr = fpo['year'].astype(np.int)
mo = fpo['month'].astype(np.int)
dy = fpo['day'].astype(np.int)
hr = fpo['hour'].astype(np.int)
mn = fpo['minute'].astype(np.int)
sc = fpo['second'].astype(np.float)

t = []
if False:
    # Would need loop like this, which increases total time by factor of 10
    for i in range(len(yr)):
        fs = (hr[i]*60.*60. + mn[i]*60. + sc[i])/86400.
        t.append(fs + datetime(yr[i], mo[i], dy[i]).toordinal() )
else:
    # For now do this and assume no change in date.
    timebin = hr*60.*60. + mn*60. + sc
toc = time.time()
tbin[1] = toc-tic

tic = time.time()
databin = fpo['data']
toc = time.time()
tbin[2] = toc-tic

plt.figure(0)
plt.plot(timebin,databin,color='magenta')
plt.show()
plt.xlabel('Seconds since ' + START)
###############################################################################

print 'bin total:         %.4fs\t# HAPI binary' % np.sum(tbin)
print '  (bin memmap:        %.4fs)' % tbin[0]
print '  (bin extract time:  %.4fs)' % tbin[1]
print '  (bin extract data:  %.4fs)' % tbin[2]

print '\nTime Ratios'
#print 'csv/fcsv        : %.4f' % (tcsv/tfcsv)
print '(best csv)/fcsv  : %.4f' % (tcsvp/tfcsv)
print '(best csv)/bin   : %.4f' % (tcsvp/np.sum(tbin))
print 'bin/fbin         : %.4f' % (np.sum(tbin)/tfbin)
print 'bin/(fbin w/ints): %.4f' % (np.sum(tbin)/tfbin2)
