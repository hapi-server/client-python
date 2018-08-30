from hapi import hapi
import numpy as np

# Checks that all four read methods give same result.
# Does not check that an individual read is correct. This was done manually.

server     = 'http://hapi-server.org/servers/TestData/hapi'
#server     = 'http://localhost:8999/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01'
stop       = '1970-01-01T00:00:03'
#stop       = '1970-01-02T00:00:00'
logging    = False
use_cache  = False

def test(parameters):
    print('Parameter(s) = %s' % parameters)
    opts       = {'format': 'csv', 'method': 'numpynolength', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('numpy no length   %.4fs' % meta['x_readTime'])
    datalast = data 
    
    opts       = {'format': 'csv', 'method': 'pandasnolength', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas no length  %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts       = {'format': 'csv', 'method': 'numpy', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('nunpy             %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts       = {'format': 'csv', 'method': 'pandas', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas            %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts       = {'format': 'binary', 'logging': logging, 'use_cache': use_cache}
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('binary            %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    
    print('Number of time values = %s' % len(data))
    print('Data types: {0}').format(data.dtype)
#############################################################################

#%% Read all parameters
test('')

#%% Read pairs of parameters
ds = hapi(server,dataset)
for i in range(0,len(ds['parameters'])-1):
    parameters = ds['parameters'][i]['name'] + ',' + ds['parameters'][i+1]['name']
    test(parameters)

#%% Read each parameter individually
ds = hapi(server,dataset)
for p in ds['parameters']:
    test(p['name'])

    