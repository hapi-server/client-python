import numpy as np
import pandas
import matplotlib.pyplot as plt 
import warnings
import re
import sys
import os

###############################################################################
#%% Python 2/3 Compatability
def urlretrieve(url,fname):
    import sys
    if sys.version_info[0] > 2: import urllib.request
    else: import urllib
    try:
        if sys.version_info[0] > 2: urllib.request.urlretrieve(url, fname)
        else: urllib.urlretrieve(url, fname)
    except: raise Exception('Could not open %s' % url)        
###############################################################################

def printf(format, *args): sys.stdout.write(format % args)

def hapitime2datetime(Time):

    import re
    import time
    import matplotlib.dates as mpl
    from datetime import datetime

    end = len(Time[0])-1
    d = 0
    # Catch case where no trailing Z
    if not re.match(r".*Z$",Time[0]):
        end = len(Time[0])
        d = 1

    tic= time.time()
    dateTime = np.zeros(len(Time),dtype='d')
    (h,hm,hms) = (False,False,False)
    if re.match(r"[0-9]{4}-[0-9]{3}", Time[0]):
        fmt = "%Y-%j"
        to = 9
        if (len(Time[0]) == 12-d):
            h = True
        if (len(Time[0]) == 15-d):
            hm = True
        if (len(Time[0]) >= 18-d):
            hms = True        
    elif re.match(r"[0-9]{4}-[0-9]{2}", Time[0]):
        fmt = "%Y-%m-%d"
        to = 11
        if (len(Time[0]) == 14-d):
            h = True
        if (len(Time[0]) == 17-d):
            hm = True
        if (len(Time[0]) >= 20-d):
            hms = True
    else:
        raise
            
    DS = Time[0][0:to-1]
    DN = float(datetime.strptime(DS, fmt).toordinal())
    for i in range(0,len(Time)):
        if (Time[i][0:to-1] != DS):
            DS = Time[0:to-1]
            DN = float(datetime.strptime(DS, fmt).toordinal()) 
        # TODO: Do different loop for each case for speed
        if hms:
            dateTime[i] = DN + float(Time[i][to:to+2])/24. + float(Time[i][to+3:to+5])/(24.*60.) + float(Time[i][to+6:end])/(24.*3600.)
        elif hm:
            dateTime[i] = DN + float(Time[i][to:to+2])/24. + float(Time[i][to+3:to+5])/(24.*60.)
        elif h:
            dateTime[i] = DN + float(Time[i][to:to+2])/24.
        else:
            dateTime[i] = DN        
        i = i+1
    toc = time.time()-tic
    #print('%.4fs' % toc)
    
    tic= time.time()
    dateTimeString = mpl.num2date(dateTime)
    toc = time.time()-tic
    #print('%.4fs' % toc)
    return dateTimeString

def hapiplot(data,meta,**kwargs):

    #%% Download and import datetick.py 
    # TODO: Incorporate datetick.py into hapiplot.py
    url = 'https://github.com/hapi-server/client-python/raw/master/misc/datetick.py'
    print(url)
    if os.path.isfile('datetick.py') == False and os.path.isfile('misc/datetick.py') == False:
        urlretrieve(url,'datetick.py')
    if os.path.isfile('misc/datetick.py') == True:
        sys.path.insert(0, './misc')

    from datetick import datetick
    
    # Default options
    DOPTS = {}
    DOPTS.update({'logging': False})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            print('Warning: Keyword option "%s" is not valid.' % key)

    fignums = plt.get_fignums()
    if len(fignums) == 0:
        fignums = [0]
    lastfn = fignums[-1]
    
    try:
        Time = pandas.to_datetime(data['Time'].astype('U'),infer_datetime_format=True)
    except:
        Time = hapitime2datetime(data['Time'].astype('U'))
        
    # In the following, the x parameter is a datetime object.
    # If the x parameter is a number, would need to use plt.plot_date()
    # and much of the code for datetick.py would need to be modified.
    for i in range(1,len(meta["parameters"])):
        if meta["parameters"][i]["type"] != "double" and meta["parameters"][i]["type"] != "integer":
            warnings.warn("Plots for types double and integer only implemented.")
            continue

        name = meta["parameters"][i]["name"]
        y = np.asarray(data[name])
    
        if meta["parameters"][i]["fill"]:
            if meta["parameters"][i]["fill"] == 'nan':
                yfill = np.nan
            else:
                yfill = float(meta["parameters"][i]["fill"])  
                #if isnan(yfill),yfill = 'null';,end
        else:
            yfill = 'null'

        if yfill != 'null':
            # Replace fills with NaN for plotting
            # (so gaps shown in lines for time series)
            y[y == yfill] = np.nan;    
        
        plt.figure(lastfn + i)
        plt.clf()
        plt.plot(Time,y)
        plt.gcf().canvas.set_window_title(meta["x_server"] + " | " + meta["x_dataset"] + " | " + name)

        yl = meta["parameters"][i]["name"] + " [" + meta["parameters"][i]["units"] + "]"
        plt.ylabel(yl)
        plt.title(meta["x_server"] + "/info?id=" + meta["x_dataset"] + "&parameters=" + name + "\n", fontsize=10)
        plt.grid()
        datetick('x')
        #import pdb; pdb.set_trace()
        
        fnamepng = re.sub('\.csv|\.bin','.png',meta['x_dataFile'])
        if DOPTS['logging']: printf('Writing %s ... ', fnamepng)
        plt.figure(lastfn + i).savefig(fnamepng,dpi=300) 
        if DOPTS['logging']: printf('Done.\n')

        # Important: This must go after savefig or else the png is blank.
        plt.show()
