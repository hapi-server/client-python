from hapi import hapi
from hapiplot import hapiplot
import time
import numpy as np

server     = 'http://hapi-server.org/servers/TestData/hapi'
#server     = 'http://localhost:8999/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01'
stop       = '1970-01-01T00:00:03'
#stop       = '1970-01-02T00:00:00'
logging    = False
use_cache  = False

#############################################################################
#%% Read method test
ds = hapi(server,dataset)

#%% Read all parameters
parameters = ''
print('Parameter(s) = %s' % parameters)
opts       = {'format': 'csv', 'method': 'numpynolength', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
datalast = data

opts       = {'format': 'csv', 'method': 'pandasnolength', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
if np.array_equal(data,datalast) == 'False':
    print('Outputs differ.')
datalast = data

opts       = {'format': 'csv', 'method': 'numpy', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
if np.array_equal(data,datalast) == 'False':
    print('Outputs differ.')
datalast = data

opts       = {'format': 'csv', 'method': 'pandas', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
if np.array_equal(data,datalast) == 'False':
    print('Outputs differ.')
datalast = data

opts       = {'format': 'binary', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
if np.array_equal(data,datalast) == 'False':
    print('Outputs differ.')

print('Number of time values = %s' % len(data))
print('Data types: {0}').format(data.dtype)
#############################################################################

#%% Read each parameter individually
for p in ds['parameters']:
    parameters = p['name']
    print('Parameter(s) = %s' % parameters)
    opts       = {'format': 'csv', 'method': 'numpynolength', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    datalast = data
    
    opts       = {'format': 'csv', 'method': 'pandasnolength', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts       = {'format': 'csv', 'method': 'numpy', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts       = {'format': 'csv', 'method': 'pandas', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts       = {'format': 'binary', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    
    print('Number of time values = %s' % len(data))
    print('Data types: {0}').format(data.dtype)
#############################################################################
