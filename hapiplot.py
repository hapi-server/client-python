import matplotlib.pyplot as plt 
from datetime import datetime
import pandas
import time
from hapi import iso2format
import matplotlib

# TODO: Figure out equivalent of MATLAB's datetick() function.

def hapiplot(meta,data,titlestr):
    fignums = plt.get_fignums()
    if len(fignums) == 0:
        fignums = [0]
    lastfn = fignums[-1]

    #tic = time.time()
    #Time1 = iso2format(data['Time'],'Unix')
    #toc = time.time()
    #tiso2format = toc-tic
    #print 'iso2format tot: %.4fs' % tiso2format
    
    #tic = time.time()
    Time = pandas.to_datetime(data['Time'],infer_datetime_format=True)
    #toc = time.time()
    #tpandas = toc-tic
    #print 'pandas to_dt:   %.4f s' % tpandas
    
    for i in xrange(1,len(meta["parameters"])):
        plt.figure(lastfn + i)
        plt.clf()
        name = meta["parameters"][i]["name"]       
        plt.plot(Time,data[name])
        ax = plt.gca()
        ax.xaxis.set_major_formatter(
            matplotlib.dates.DateFormatter('%H:%M')
        )
        #to = Time[0].toordinal()
        #tf = Time[-1].toordinal()
        # TODO: Figure out automated way to do this equivalent to
        # dateticks() in MATLAB.
        plt.xlabel('Start date:' + data['Time'][0][0:10])
        yl = meta["parameters"][i]["name"] + " [" + meta["parameters"][i]["units"] + "]"
        plt.ylabel(yl)
        plt.title(titlestr + ": Parameter from dataset w/id = " + meta["x_dataset"] + " from " + meta["x_server"], fontsize=10)
        plt.grid()
        plt.show()