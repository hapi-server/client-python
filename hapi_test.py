from hapi import hapi
import numpy as np
import json

# Checks that all four read methods give same result.
# Does not check that an individual read is correct. Do this manually.

server     = 'http://hapi-server.org/servers/TestData/hapi'
#server     = 'http://localhost:8999/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01'
stop       = '1970-01-01T00:00:03'
#stop       = '1970-01-02T00:00:00'

# Note that cache = False will prevent output from server from
# being written to file before being read. Need to test all permutations
# of cache/use_cache
opts       = {'logging': False, 'cache': True, 'use_cache': True}

'''
Typical results:
    
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

def test(parameters,opts):

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
    print('Data types: {0}').format(data.dtype)
#############################################################################

if False:
    #############################################################################
    #%% Metadata request examples
    
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
    #############################################################################

if True:
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

    