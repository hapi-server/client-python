from hapi import hapi
from hapiplot import hapitime2datetime
import numpy as np
import json

# Test various parts of hapi.py and hapiplot.py.

server     = 'http://hapi-server.org/servers/TestData/hapi'
#server     = 'http://localhost:8999/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01'
stop       = '1970-01-01T00:00:03'  # Returns 3 time values
#stop       = '1970-01-02T00:00:00' # Returns 86400 time values

#%%
def test(parameters,opts):

    # Checks that all four read methods give same result.
    # Does not check that an individual read is correct. Do this manually.
    
    opts['format'] = 'csv'
    
    print('Parameter(s) = %s' % parameters)
    opts['method'] = 'numpynolength'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('numpy no length   %.4fs/%.4fs' % (meta['x_readTime'],meta['x_downloadTime']))
    datalast = data 
    
    opts['method'] = 'pandasnolength'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas no length  %.4fs/%.4fs' % (meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts['method'] = 'numpy'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('numpy             %.4fs/%.4fs' % (meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts['method'] = 'pandas'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas            %.4fs/%.4fs' % (meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    datalast = data
    
    opts['format'] = 'binary'
    opts['method'] = '' # Ignored
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('binary            %.4fs/%.4fs' % (meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
    
    print('Number of time values = %s' % len(data))
    print('Data types:')
    print(data.dtype)


###############################################################################
# Read tests

opts = {'logging': False, 'cache': True, 'use_cache': True}
# Note that cache = False will prevent output from server from
# being written to file before being read. Need to test all permutations
# of cache/use_cache

#%% Read one parameter
if True:
    test('scalar',opts)

'''
Typical results for test('scalar',use_cache=False):
    
cache = True # Save data to disk then read.
Parameter(s) = scalar
numpy no length   0.7053s
pandas no length  0.1095s
numpy             0.4706s
pandas            0.0913s
binary            0.0030s
Number of time values = 86400
Data types: [('Time', 'S24'), ('scalar', '<f8')]

cache = False # Read data directly into memory.
Parameter(s) = scalar
numpy no length   0.7064s
pandas no length  0.1195s
numpy             0.4301s
pandas            0.1011s
binary            0.0004s
Number of time values = 86400
Data types: [('Time', 'S24'), ('scalar', '<f8')]
'''

#%% Read all parameters
if False:
    test('',opts)
    
#%% Read pairs of parameters
if False:
    ds = hapi(server,dataset)
    for i in range(0,len(ds['parameters'])-1):
        parameters = ds['parameters'][i]['name'] + ',' + ds['parameters'][i+1]['name']
        test(parameters,opts)
    
#%% Read each parameter individually
if False:
    ds = hapi(server,dataset)
    for p in ds['parameters']:
        test(p['name'],opts)
###############################################################################

#%% Metadata request examples
if False:
    
    # List servers to console
    hapi(logging=True)
    
    # Get server list
    Servers = hapi()
    print("Server list")
    print(json.dumps(Servers, sort_keys=True, indent=4))
    
    # Get structure of datasets from server
    print("Datasets from " + server)
    metad = hapi(server)
    print(json.dumps(metad, sort_keys=True, indent=4))
    
    # Get dictionary of all parameters in dataset dn
    print("Parameters in first datataset " + metad['catalog'][0]['id'] + " from server " + server)
    metap = hapi(server, metad['catalog'][0]['id'])
    print(json.dumps(metap, sort_keys=True, indent=4))
    
    # Get structure of first parameter in first dataset
    metap1 = hapi(server, metad['catalog'][0]['id'], metap["parameters"][1]["name"])
    
    print("Parameter " +  metap["parameters"][1]["name"] + " in datataset " + metad['catalog'][0]['id'] + " from server " + server)
    print(json.dumps(metap1, sort_keys=True, indent=4))

if False:
    # Bad server URL
    hapi('http://hapi-server.org/servers/TestData/xhapi')

    # Bad dataset name
    dataset    = 'dataset1x'    
    stop       = '1970-01-01T00:00:03'   
    meta  = hapi(server, dataset)
    
   # Bad parameter name
    dataset    = 'dataset1'
    parameters = 'scalarx'
    meta  = hapi(server, dataset, parameters)
    
    data,meta  = hapi(server, dataset, parameters, start, stop)

if False:
    # Test manual time parsing code used in hapiplot.py.
    print(hapitime2datetime(['2000-01-02']))
    print(hapitime2datetime(['2000-01-02Z']))
    print(hapitime2datetime(['2000-002']))
    print(hapitime2datetime(['2000-002Z']))
    print('')
    print(hapitime2datetime(['2000-01-02T03']))
    print(hapitime2datetime(['2000-01-02T03Z']))
    print(hapitime2datetime(['2000-002T03']))
    print(hapitime2datetime(['2000-002T03Z']))
    print('')
    print(hapitime2datetime(['2000-01-02T03:04']))
    print(hapitime2datetime(['2000-01-02T03:04Z']))
    print(hapitime2datetime(['2000-002T03:04']))
    print(hapitime2datetime(['2000-002T03:04Z']))
    print('')
    print(hapitime2datetime(['2000-01-02T03:04:05']))
    print(hapitime2datetime(['2000-01-02T03:04:05Z']))
    print(hapitime2datetime(['2000-002T03:04:05']))
    print(hapitime2datetime(['2000-002T03:04:05Z']))
    print('')
    print(hapitime2datetime(['2000-01-02T03:04:05.']))
    print(hapitime2datetime(['2000-01-02T03:04:05.Z']))
    print(hapitime2datetime(['2000-002T03:04:05.']))
    print(hapitime2datetime(['2000-002T03:04:05.Z']))
    print('')
    print(hapitime2datetime(['2000-01-02T03:04:05.6']))
    print(hapitime2datetime(['2000-01-02T03:04:05.6Z']))
    print(hapitime2datetime(['2000-002T03:04:05.6']))
    print(hapitime2datetime(['2000-002T03:04:05.6Z']))