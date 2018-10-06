import shutil
import numpy as np
from hapiclient.hapi import hapi

def readcompare(server, dataset, parameters, run, opts):

    dataset = 'dataset1'
    start = '1970-01-01'

    allpass = True
    
    if run == 'short':
        stop = '1970-01-01T00:00:03' # Returns 3 time values

    if run == 'long':
        stop= '1970-01-02T00:00:00' # Returns 86400 time values

    # Checks that all four read methods give same result.
    # Does not check that an individual read is correct. 
    # Do this manually.
    
    opts['format'] = 'csv'
    
    print('\nParameter(s) = %s; run = %s. use_cache = %s' % (parameters, run, opts['use_cache']))
    print('_______________________________________')
    print('Method          read time/download time')
    print('_______________________________________')
    opts['method'] = 'numpynolength'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('numpy no length   %.1f ms/%.4f s' % (1000.*meta['x_readTime'],meta['x_downloadTime']))
    dtypelast = data.dtype
    datalast = data 
    
    opts['method'] = 'pandasnolength'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas no length  %.1f ms/%.1f s' % (1000.*meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False': 
        print('Outputs differ.')
        allpass = True
    if dtypelast != data.dtype: 
        print('Data types differ.')
        allpass = True
    dtypelast = data.dtype
    datalast = data
    
    opts['method'] = 'numpy'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('numpy             %.1f ms/%.2f s' % (1000.*meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
        allpass = True
    if dtypelast != data.dtype:
        print('Data types differ.')
        allpass = True
    dtypelast = data.dtype
    datalast = data
    
    opts['method'] = 'pandas'
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('pandas            %.1f ms/%.2f s' % (1000.*meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
        allpass = True
    if dtypelast != data.dtype:
        print('Data types differ.')
        allpass = True

    dtypelast = data.dtype
    datalast = data
    
    opts['format'] = 'binary'
    opts['method'] = '' # Ignored
    data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
    print('binary            %.1f ms/%.2f s' % (1000.*meta['x_readTime'],meta['x_downloadTime']))
    if np.array_equal(data,datalast) == 'False':
        print('Outputs differ.')
        allpass = True
    if dtypelast != data.dtype:
        print('Data types differ.')
        allpass = True
        
    return allpass

def clearcache(opts):
    shutil.rmtree(opts['cache_dir'], ignore_errors=True)
