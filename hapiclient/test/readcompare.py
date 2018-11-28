import shutil
import numpy as np
import pickle

from hapiclient.hapi import hapi
from hapiclient.hapi import request2path

debug = False

def requestinfo(server, dataset, parameters, start, stop, cachedir):
    infopkl = request2path(server, dataset, parameters, start, stop, cachedir)
    infopkl = infopkl + ".pkl"
    f = open(infopkl, 'rb')
    info = pickle.load(f)
    f.close()
    return info

def comparisonOK(a, b):
    
    if a.dtype != b.dtype: 
        if debug: print('Data types differ.')
        if debug: print(a.dtype, b.dtype)
        if debug: import pdb; pdb.set_trace()
        return False

    if equal(a, b):
        return True
    else:
        if closeFloats(a, b) and equalNonFloats(a, b):
            return True
        else:
            return False
    
def equal(a, b):
    allequal = True
    for name in a.dtype.names:
        if not np.array_equal(a[name], b[name]):
            allequal = False
            if debug: print(name + ' values differ.')

    return allequal

def equalNonFloats(a, b):
    allequal = True
    for name in a.dtype.names:
        if np.issubdtype(a[name].dtype, np.integer) or np.issubdtype(a[name].dtype, np.flexible):
            # https://docs.scipy.org/doc/numpy-1.10.1/reference/arrays.scalars.html
            # Parameter type is string or integer
            if not np.array_equal(a[name], b[name]):
                allequal = False
                if debug: print(name + ' values differ.')
                if debug: import pdb; pdb.set_trace()

    return allequal

def closeFloats(a, b):
    allclose = True
    for name in a.dtype.names:
        if np.issubdtype(a[name].dtype, np.inexact):
            # https://docs.scipy.org/doc/numpy-1.10.1/reference/arrays.scalars.html
            # Parameter is floating point number
            if np.allclose(a[name], b[name], rtol=1e-15, atol=0.0, equal_nan=True):
                if not np.array_equal(a[name], b[name]):
                    if debug: print(name + ' values equal within rtol=1e-15.')
            else:
                allclose = False
                if debug: print(name + ' values not equal within rtol=1e-15.')
                if debug: import pdb; pdb.set_trace()


    return allclose

def readcompare(server, dataset, parameters, run, opts):

    # Note that for this dataset, there are differences in
    # the numeric values that seem not to be due to issues
    # with the reader. This needs investigation.
    
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
    
    print('\nParameter(s) = %s; run = %s. cache = %s; usecache = %s' % (parameters, run, opts['cache'], opts['usecache']))
    if opts['cache']:
        print('__________________________________________')
        print('Method           read/parse  download ')
        print('__________________________________________')
    else:
        print('__________________________________________')
        print('Method         create buff   download/parse')
        print('__________________________________________')
        
    opts['method'] = 'numpynolength'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    info = requestinfo(server, dataset, parameters, start, stop, opts['cachedir'])
    print('numpy no length   %5.2f ms %8.4f s' % (1000.*info['x_readTime'], info['x_downloadTime']))
    datalast = data 
    
    opts['method'] = 'pandasnolength'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    info = requestinfo(server, dataset, parameters, start, stop, opts['cachedir'])
    if np.array_equal(data, datalast):
        print('pandas no length  %5.2f ms %8.4f s' % (1000.*info['x_readTime'], info['x_downloadTime']))
    else:
        print('pandas no length  %5.2f ms %8.4f s (diffs in float values <= 1e-15)' % (1000.*info['x_readTime'], info['x_downloadTime']))
    allpass = comparisonOK(data, datalast)
    datalast = data
    
    opts['method'] = 'numpy'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    info = requestinfo(server, dataset, parameters, start, stop, opts['cachedir'])
    if np.array_equal(data, datalast):
        print('numpy             %5.2f ms %8.4f s' % (1000.*info['x_readTime'], info['x_downloadTime']))
    else:
        print('numpy             %5.2f ms %8.4f s (diffs in float values <= 1e-15)' % (1000.*info['x_readTime'], info['x_downloadTime']))
    allpass = comparisonOK(data, datalast)
    datalast = data
    
    opts['method'] = 'pandas'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    info = requestinfo(server, dataset, parameters, start, stop, opts['cachedir'])
    if np.array_equal(data, datalast):
        print('pandas            %5.2f ms %8.4f s' % (1000.*info['x_readTime'], info['x_downloadTime']))
    else:
        print('pandas            %5.2f ms %8.4f s (diffs in float values <= 1e-15)' % (1000.*info['x_readTime'], info['x_downloadTime']))

    allpass = comparisonOK(data, datalast)
    datalast = data
    
    opts['format'] = 'binary'
    opts['method'] = '' # Ignored
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    info = requestinfo(server, dataset, parameters, start, stop, opts['cachedir'])
    if np.array_equal(data, datalast):
        print('binary            %5.2f ms %8.4f s' % (1000.*info['x_readTime'], info['x_downloadTime']))
    else:
        print('binary            %5.2f ms %8.4f s (diffs in float values <= 1e-15)' % (1000.*info['x_readTime'], info['x_downloadTime']))

    allpass = comparisonOK(data, datalast)

    return allpass

def clearcache(opts):
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
