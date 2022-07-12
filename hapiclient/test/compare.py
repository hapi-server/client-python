import os
import numpy as np
import shutil

from hapiclient import hapi

debug = False

def comparisonOK(a, b, nolength=False, a_name="First", b_name="Second"):

    if a.dtype != b.dtype:
        if debug:
            print('---- dts differ.')
        unicode_length_mismatch = False
        for i in range(len(a.dtype)):
            if a.dtype[i].str != b.dtype[i].str:
                if debug:
                    print("---  {}".format(a_name))
                    print("---  {}".format(a.dtype[i].str))
                    print("---  {}".format(b_name))
                    print("---  {}".format(b.dtype[i].str))
                # When length is given, the HAPI spec states that it should be
                # the number of bytes required to store any value of the parameter.
                # Greek characters require two bytes when encoded as UTF-8, so
                # length=2 if the parameter values are all single Greek character.
                # However, when NumPy is used to determine the data type of a
                # single UTF-8 encoded character because length is not given,
                # it uses "U1" (see hapi.py/parse_missing_length() and search
                # for ".astype('<S').dtype")
                if a.dtype[i].str.startswith("<U") and b.dtype[i].str.startswith("<U"):
                    unicode_length_mismatch = True
                if a.dtype[i].str.startswith("|V") and b.dtype[i].str.startswith("|V"):
                    # Array of strings
                    unicode_length_mismatch = True

        if nolength is True and unicode_length_mismatch is True:
            return True
        else:
            if debug:
                print(a.dtype)
                print(b.dtype)
            return False

    if equal(a, b):
        return True
    else:
        if closeFloats(a, b) and equalNonFloats(a, b):
            return True
        else:
            if debug:
                print(a)
                print(b)
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
                if debug: print("'" + name + "' values differ.")
                #print(a[name])
                #print(b[name])
                #if debug: import pdb; pdb.set_trace()

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
logfile = os.path.splitext(__file__)[0] + ".log"
with open(logfile, "w") as f: pass


def xprint(msg):
    print(msg)
    f = open(logfile, "a")
    f.write(msg + "\n")
    f.close()


def cache(server, dataset, parameter, opts):

    import sys

    start      = '1970-01-01T00:00:00.000Z';
    stop       = '1970-01-01T00:00:04.000Z';

    shutil.rmtree(opts['cachedir'], ignore_errors=True)

    opts['format']   = 'binary';
    opts['cache']    = False;
    opts['usecache'] = False;

    data0, meta = hapi(server, dataset, parameter, start, stop, **opts)

    opts['format']   = 'binary';
    opts['cache']    = False;
    opts['usecache'] = True;
    data, meta = hapi(server, dataset, parameter, start, stop, **opts)

    allpass = True

    if sys.version_info[0] < 3:
        ok = np.array_equal(data0[str(parameter)], data[str(parameter)])
    else:
        ok = np.array_equal(data0[parameter], data[parameter])
    allpass = allpass and ok

    opts['format'] = 'csv';
    opts['usecache'] = False;
    data, meta = hapi(server, dataset, parameter, start, stop, **opts)

    if sys.version_info[0] < 3:
        ok = np.array_equal(data0[str(parameter)], data[str(parameter)])
    else:
        ok = np.array_equal(data0[parameter], data[parameter])
    allpass = allpass and ok

    opts['format'] = 'csv';
    opts['usecache'] = True;
    data, meta = hapi(server, dataset, parameter, start, stop, **opts)

    if sys.version_info[0] < 3:
        ok = np.array_equal(data0[str(parameter)], data[str(parameter)])
    else:
        ok = np.array_equal(data0[parameter], data[parameter])
    allpass = allpass and ok

    return allpass


def read(server, dataset, parameters, run, opts):

    # Note that for this dataset, there are differences in
    # the numeric values that seem not to be due to issues
    # with the reader. This needs investigation.

    start = '1970-01-01'

    allpass = True

    if run == 'short':
        stop = '1970-01-01T00:00:03' # Returns 3 time values

    if run == 'long':
        stop= '1970-01-02T00:00:00' # Returns 86400 time values

    # Checks that all four read methods give same result.
    # Does not check that an individual read is correct.
    # Do this manually.
    
    xprint('\nDataset = {}; Parameter(s) = {}; run = {}. cache = {}; usecache = {}' \
            .format(dataset, parameters, run, opts['cache'], opts['usecache']))
    if opts['cache']:
        xprint('_____________________________________________________________')
        xprint('Method                total      d/l->file  read & parse file')
        xprint('_____________________________________________________________')
    else:
        xprint('___________________________________________________________')
        xprint('Method                total      d/l->buff  parse buff')
        xprint('___________________________________________________________')


    opts['format'] = 'binary'
    opts['method'] = ''

    data0, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    xprint('binary               %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    opts['format'] = 'csv'

    opts['method'] = 'pandas' # Default CSV read method.
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    xprint('csv; pandas          %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    allpass = allpass and comparisonOK(data0, data, a_name='binary', b_name='pandas')

    opts['method'] = 'pandasnolength'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    xprint('csv; pandas; no len. %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    allpass = allpass and comparisonOK(data0, data, nolength=True, a_name='binary', b_name='csv; pandas; no len.')


    opts['method'] = 'numpy'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    xprint('csv; numpy           %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))

    allpass = allpass and comparisonOK(data0, data, a_name='binary', b_name='csv; numpy')

    opts['method'] = 'numpynolength'
    data, meta  = hapi(server, dataset, parameters, start, stop, **opts)
    xprint('csv; numpy; no len.  %8.4f   %8.4f   %8.4f' % \
            (meta['x_totalTime'], meta['x_downloadTime'], meta['x_readTime']))


    allpass = allpass and comparisonOK(data0, data, nolength=True, a_name='binary', b_name='csv; numpy; no len.')

    return allpass
