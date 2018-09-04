#%% Note
# In IPython, enter %matplotlib qt on command line to open plots in 
# new window. Enter %matplotlib inline to revert.

#%% Python 2/3 Compatability
def urlretrieve(url,fname):
    import sys
    if sys.version_info[0] > 2: import urllib.request
    else: import urllib
    try:
        if sys.version_info[0] > 2: urllib.request.urlretrieve(url, fname)
        else: urllib.urlretrieve(url, fname)
    except: raise Exception('Could not open %s' % url)        

#%% Download hapi.py and hapiplot.py if not found
import os
url = 'https://github.com/hapi-server/client-python/hapi_demo.py'        
if os.path.isfile('hapi.py') == False:
    urlretrieve(url,'hapi.py')
if os.path.isfile('hapiplot.py') == False:
    urlretrieve(url,'hapiplot.py')

#%% Imports
from hapi import hapi
from hapiplot import hapiplot

#%% CDAWeb data
server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
dataset    = 'AC_H0_MFI'
start      = '2001-01-01T05:00:00'
stop       = '2001-01-01T06:00:00'
parameters = 'Magnitude,BGSEc'
opts       = {'logging': False, 'use_cache': False}
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data,meta)
###############################################################################

#%% CDAWeb metadata for AC_H0_MFI
server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
dataset    = 'AC_H0_MFI'
meta = hapi(server,dataset, **opts)
print('Parameters in %s' % dataset)
for i in range(0,len(meta['parameters'])):
    print('  %s' % meta['parameters'][i]['name'])
print('')

#%% CDAWeb metadata for all datasets
server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
meta = hapi(server, **opts)
print('%d CDAWeb datasets' % len(meta['catalog']))
for i in range(0,3):
    print('  %d. %s' % (i,meta['catalog'][i]['id']))
print('  ...')    
print('  %d. %s' % (len(meta['catalog']),meta['catalog'][-1]['id']))
print('')

#%% List all servers
servers = hapi(logging=True)
print('')