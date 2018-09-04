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

def hapiplot(data,meta,**kwargs):

    #%% Download and import datetick.py 
    # TODO: Incorporate datetick.py into hapiplot.py
    url = 'https://github.com/hapi-server/client-python/misc/datetick.py'
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
    
    Time = pandas.to_datetime(data['Time'].astype('U'),infer_datetime_format=True)
    
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
        plt.title(meta["x_server"] + "/info?id=" + meta["x_dataset"] + "&parameters=" + name, fontsize=10)

        plt.grid()
        datetick('x')
        
        fnamepng = re.sub('\.csv|\.bin','.png',meta['x_dataFile'])
        if DOPTS['logging']: printf('Writing %s ... ', fnamepng)
        plt.figure(lastfn + i).savefig(fnamepng,dpi=300) 
        if DOPTS['logging']: printf('Done.\n')

        # Important: This must go after savefig or else the png is blank.
        plt.show()
