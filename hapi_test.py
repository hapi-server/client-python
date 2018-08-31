from hapi import hapi
import numpy as np

# Checks that all four read methods give same result.
# Does not check that an individual read is correct. This was done manually.

server     = 'http://hapi-server.org/servers/TestData/hapi'
#server     = 'http://localhost:8999/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01'
stop       = '1970-01-01T00:00:03'
stop       = '1970-01-02T00:00:00'
logging    = False
use_cache  = False # If true, read cached output.
# cache_npbin = False will prevent output from server being written to file
# before being read.
opts       = {'logging': logging, 'cache_npbin': False, 'use_cache': use_cache}

'''
Typical results:
    
cache_npbin = True # Save data to disk then read.
Parameter(s) = scalar
numpy no length   1.5245s
pandas no length  0.2028s
numpy             0.4956s
pandas            0.1133s
binary            0.0015s
Number of time values = 86400
Data types: [('Time', 'S24'), ('scalar', '<f8')]

cache_npbin = False # Read data directly into memory.
Parameter(s) = scalar
numpy no length   0.7105s
pandas no length  0.1058s
numpy             0.4420s
pandas            0.0914s
binary            0.0018s
Number of time values = 86400
Data types: [('Time', 'S24'), ('scalar', '<f8')]
'''

def test(parameters,opts):

    opts['format'] = 'csv'
    
    print('Parameter(s) = %s' % parameters)
    opts['method'] = 'numpynolength'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('numpy no length   %.4fs' % meta['x_readTime'])
    datalast = data 
    
    opts['method'] = 'pandasnolength'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas no length  %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts['method'] = 'numpy'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('numpy             %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts['method'] = 'pandas'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas            %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts['format'] = 'binary'
    opts['method'] = '' # Ignored
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('binary            %.4fs' % meta['x_readTime'])
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    
    print('Number of time values = %s' % len(data))
    print('Data types: {0}').format(data.dtype)
#############################################################################

#%% Read one parameter
test('scalar',opts)

if False:
    #%% Read all parameters
    test('',opts)
    
    #%% Read pairs of parameters
    ds = hapi(server,dataset)
    for i in range(0,len(ds['parameters'])-1):
        parameters = ds['parameters'][i]['name'] + ',' + ds['parameters'][i+1]['name']
        test(parameters,opts)
    
    #%% Read each parameter individually
    ds = hapi(server,dataset)
    for p in ds['parameters']:
        test(p['name'],opts)

    