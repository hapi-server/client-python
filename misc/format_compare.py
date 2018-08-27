import time
import os
import re
import numpy as np
import urllib
from datetime import datetime
import matplotlib.dates as mdates
import pandas
import csv
from datetick import *

file = 'vector'
base = 'http://mag.gmu.edu/TestData/hapi';
#base = 'http://localhost:8999/hapi'
START = '1970-01-01'
size = 1;

filecsv   = './tmp/' + file + '.csv'
filefcsv  = './tmp/' + file + '.fcsv'
filebin   = './tmp/' + file + '.bin'
filefbin  = './tmp/' + file + '.fbin'
filefbin2 = './tmp/' + file + '.fbin2'

if not os.path.exists('./tmp/'):
    os.makedirs('./tmp')
if not os.path.isfile(filecsv):
    urllib.urlretrieve(base + '/data/?id=dataset1&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=csv',filecsv)
if not os.path.isfile(filefcsv):
    urllib.urlretrieve(base + '/data/?id=dataset1&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fcsv',filefcsv)
if not os.path.isfile(filebin):
    urllib.urlretrieve(base + '/data/?id=datset1&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=binary',filebin)
if not os.path.isfile(filefbin):
    urllib.urlretrieve(base + '/data/?id=datset1&parameters=' + file + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',filefbin)
if not os.path.isfile(filefbin2):
    urllib.urlretrieve(base + '/data/?id=dataset1&parameters=' + file + 'int' + '&time.min=1970-01-01&time.max=1970-01-02T00:00:00&format=fbinary',filefbin2)

plt.figure(0);plt.clf()

###############################################################################
# Read Fast CSV
# See also https://softwarerecs.stackexchange.com/questions/7463/fastest-python-library-to-read-a-csv-file
tic = time.time()
dtype = [('Time','<d',1),('scalar','<d',1)]
datafcsv1 = pandas.read_csv(filefcsv,dtype=dtype,names=['Time','scalar'],sep=',')
zero = datetime.strptime('1970-01-01', "%Y-%m-%d").toordinal()
Time = zero + datafcsv1['Time']/86400.
tfcsv = [time.time()-tic];
print 'fcsv (pandas.read_csv)                 %.4fs # Fast CSV' % tfcsv[0]
#Time = mdates.num2date(zero + datafcsv1['Time']/86400., tz=None)

plt.figure(0)
plt.plot(Time, datafcsv1['scalar'], '-')
datetick()
plt.show()
###############################################################################

###############################################################################
# Read Fast CSV
tic = time.time()
datafcsv2 = np.loadtxt(filefcsv, delimiter=',')
toc = time.time()
zero = datetime.strptime('1970-01-01', "%Y-%m-%d").toordinal()
Time = zero + datafcsv2[:,0]/86400.
tfcsv = [time.time()-tic] + tfcsv
print 'fcsv (np.loadtxt)                      %.4fs # Fast CSV' % tfcsv[0]

plt.figure(0)
plt.plot(Time, datafcsv2[:,1], '-')
datetick()
plt.show()
###############################################################################

###############################################################################
# Read CSV
tic= time.time()
Time = np.zeros(86400,dtype='d')
data = np.zeros(86400,dtype='d')
DS = "1970-01-01"
DN = float(datetime.strptime(DS, "%Y-%m-%d").toordinal())
i = 0
f = open(filecsv)
for line in f:
     data[i] = line.split(',')[1]
     if (line[0:10] != DS):
         DS = line[0:10]
         DN = float(datetime.strptime(DS, "%Y-%m-%d").toordinal()) 
     Time[i] = DN + float(line[11:13])/24. + float(line[14:16])/(24.*60.) + float(line[17:23])/(24.*3600.)
     i = i+1
tcsv = [time.time()-tic]
print 'csv (line by line + faden/datenum)     %.4fs # HAPI CSV' % tcsv[0]
f.close()

plt.figure(0)
plt.plot(Time, data, '-')
datetick()
plt.show()
###############################################################################

###############################################################################
# Read HAPI CSV
tic = time.time()
dt = [('Time','|S24',1),('scalar','<d',1)]
df = pandas.read_csv(filecsv,dtype=dt,names=['Time','scalar'],sep=',')
v = df['Time'].values
data = df['scalar'].values
i = 0
for line in v:
     if (line[0:10] != DS):
         DS = line[0:10]
         DN = float(datetime.strptime(DS, "%Y-%m-%d").toordinal()) 
     Time[i] = DN + float(line[11:13])/24. + float(line[14:16])/(24.*60.) + float(line[17:23])/(24.*3600.)
     i = i+1
tcsv = tcsv + [time.time()-tic]
print 'csv (pandas.read_csv + faden/datenum)  %.4fs # HAPI CSV' % tcsv[1]
plt.figure(0)
plt.plot(Time,data,color='red')
datetick()
plt.show()
###############################################################################

###############################################################################
# Read HAPI CSV
tic = time.time()
df = pandas.read_csv(filecsv,names=['Time', 'scalar'],date_parser=[0], sep=',')
z  = pandas.to_datetime(df['Time'],infer_datetime_format=True,utc=True)
Time = z.values.astype('d')
Time = Time/86400.0e9 + float(datetime.strptime("1970-01-01", "%Y-%m-%d").toordinal())

data  = df['scalar'].values.view()
tcsv = tcsv + [time.time()-tic];
print 'csv (pandas.read_csv)                  %.4fs # HAPI CSV' % tcsv[2]

plt.figure(0)
plt.plot(Time, data, '-')
datetick()
plt.show()
###############################################################################

###############################################################################
# Read and plot HAPI CSV (genfromtxt)
tic = time.time()
dt = [('Time','|S24',1),('scalar','<d',1)]
df = np.genfromtxt(filecsv,dtype=dt, delimiter=',')
i = 0
v = df['Time']
for line in v:
     if (line[0:10] != DS):
         DS = line[0:10]
         DN = float(datetime.strptime(DS, "%Y-%m-%d").toordinal()) 
     Time[i] = DN + float(line[11:13])/24. + float(line[14:16])/(24.*60.) + float(line[17:23])/(24.*3600.)
     i = i+1
tcsv = tcsv + [time.time()-tic]
print 'csv (genfromtext + faden/datenum)      %.4fs # HAPI CSV' % tcsv[3]

###############################################################################

stop
if False: # Far too slow.
    ###############################################################################
    # Read and plot HAPI CSV
    # See also https://softwarerecs.stackexchange.com/questions/7463/fastest-python-library-to-read-a-csv-file
    tic = time.time()
    datacsv =[]
    with open(filecsv, 'rb') as csvfile:
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
    plt.draw()
    plt.show(block=False)
    plt.xlabel('Hours since ' + START)
    ###############################################################################

###############################################################################
# Using double only data in fast binary
tic = time.time()
f = open(filefbin, 'rb')
t = f.read(21)
n = int(t[0])
dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
f.seek(21, os.SEEK_SET)
datafbin = np.fromfile(f, dtype=np.dtype('<d'))
f.close
datafbin = np.reshape(datafbin, [len(datafbin)/(size+1), (size+1)])
toc = time.time()
tfbin = toc-tic;
print 'fbin (fromfile)    %.4fs\t# Fast binary (all doubles)' % tfbin

plt.figure(0)
plt.plot(datafbin[:,0],datafbin[:,1],color='blue')
plt.draw()
plt.show(block=False)
plt.xlabel('Seconds since ' + START)
###############################################################################

if False: # Faster than above, but use above as worst-case
    ###############################################################################
    # Using mixed double and int data in fast binary 
    tic = time.time()
    f = open(filefbin2, 'rb')
    t = f.read(21)
    n = int(t[0])
    dt = datetime.strptime(t[1:20], '%Y-%m-%dT%H:%M:%S')
    zerotime = dt.toordinal()
    f.seek(21, os.SEEK_SET)
    dt = [('time', '<d'),('scalar',np.int32)]
    datafbin2 = np.fromfile(f, dtype=dt)
    f.close
    toc = time.time()
    tfbin2 = toc-tic;
    print 'fbin (fromfile)   %.4fs\t# Fast binary (time dbl, param int)' % tfbin2
    
    plt.figure(0)
    plt.plot(datafbin2['time'],datafbin2['scalar']/1000.,color='yellow')
    plt.draw()
    plt.show(block=False)
    plt.xlabel('Seconds since ' + START)
    ###############################################################################

###############################################################################
# Using HAPI binary
tic = time.time()
dt   = []
dt.append(('Time', 'S24', 1))
dt.append(('scalar','d',1))
df = np.fromfile(filebin, dtype=dt)
# Much slower: data['Time'] = iso2format(df['Time'],'Unix')
Time = pandas.to_datetime(df['Time'],infer_datetime_format=True,utc=True).view('m8')
toc = time.time()
tbin = toc-tic;
print 'bin (fromfile)     %.4fs\t# HAPI binary' % tbin

plt.figure(0)
plt.plot(Time/1e9,df['scalar'],color='black')
plt.draw()
plt.show(block=False)
plt.xlabel('Seconds since ' + START)

###############################################################################

if False:
    ###############################################################################
    # Using HAPI binary
    tbin = [0,0,0];
    
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

    print 'bin total:         %.4fs\t# HAPI binary' % np.sum(tbin)

    #plt.figure(0)
    #plt.plot(timebin,databin,color='magenta')
    #plt.show()
    #plt.xlabel('Seconds since ' + START)
###############################################################################

#print '  (bin memmap:        %.4fs)' % tbin[0]
#print '  (bin extract time:  %.4fs)' % tbin[1]
#print '  (bin extract data:  %.4fs)' % tbin[2]

print '\nTime Ratios (Best HAPI over best "Fast")'
#print 'csv/fcsv        : %.4f' % (tcsv/tfcsv)
print 'csv/fcsv   %.4f' % (tcsvp2/tfcsv)
print 'bin/fbin   %.4f' % (tbin/tfbin)
print ''
print 'csv/bin    %.4f' % (tcsvp/tbin)
print 'fcsv/fbin  %.4f' % (tfcsv/tbin)
#print 'bin/(fbin w/ints): %.4f' % (np.sum(tbin)/tfbin2)