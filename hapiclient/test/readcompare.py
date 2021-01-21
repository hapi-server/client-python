import os
import numpy as np

from hapiclient import hapi

debug = False


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
            # Parameter type is string or integer
            # https://docs.scipy.org/doc/numpy-1.10.1/reference/arrays.scalars.html
            if not np.array_equal(a[name], b[name]):
                allequal = False
                if debug: print(name + ' values differ.')
                if debug: import pdb; pdb.set_trace()

    return allequal


def closeFloats(a, b):
    allclose = True
    for name in a.dtype.names:
        if np.issubdtype(a[name].dtype, np.inexact):
            # Parameter is floating point number
            # See https://docs.scipy.org/doc/numpy-1.10.1/reference/arrays.scalars.html
            atol = np.finfo(a[name].dtype.str).eps
            if np.allclose(a[name], b[name], rtol=0.0, atol=atol, equal_nan=True):
                if debug and not np.array_equal(a[name], b[name]):
                    mdiff = np.max(np.abs(a[name] - b[name]))
                    print('All values in parameter ' + name \
                          + ' equal within absolute tolerance ' \
                          + 'of %.2e; max |diff| = %.2e' % (atol, mdiff))
            else:
                allclose = False
                print('All values in parameter ' + name \
                      + ' not equal within absolute tolerance of %.2e.' % atol)

    return allclose


# Create empty file
logfile = os.path.realpath(__file__)[0:-2] + "log"
with open(logfile, "w") as f: pass


def xprint(msg):
    print(msg)
    f = open(logfile, "a")
    f.write(msg + "\n")
    f.close()


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

    if run == 'verylong':
        stop= '1970-01-02T00:00:00' # Returns 86400 time values

    # Checks that all four read methods give same result.
    # Does not check that an individual read is correct.
    # Do this manually.
    
    opts['format'] = 'csv'
    
    xprint('\nParameter(s) = %s; run = %s. cache = %s; usecache = %s' \
            % (parameters, run, opts['cache'], opts['usecache']))
    if opts['cache']:
        xprint('_____________________________________________________________')
        xprint('Method                total      d/l->file  read & parse file')
        xprint('_____________________________________________________________')
    else:
        xprint('___________________________________________________________')
        xprint('Method                total      d/l->buff  parse buff')
        xprint('___________________________________________________________')


    opts['method'] = 'numpynolength'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    xprint('csv; numpy; no len.  %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))
    datalast = data 


    opts['method'] = 'pandasnolength'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)

    xprint('csv; pandas; no len. %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    allpass = comparisonOK(data, datalast)
    datalast = data


    opts['method'] = 'numpy'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)

    xprint('csv; numpy           %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    allpass = comparisonOK(data, datalast)
    datalast = data


    opts['method'] = 'pandas'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)

    xprint('csv; pandas          %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    allpass = comparisonOK(data, datalast)
    datalast = data


    opts['format'] = 'binary'
    opts['method'] = '' # Ignored
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)

    xprint('binary               %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    allpass = comparisonOK(data, datalast)

    return allpass
