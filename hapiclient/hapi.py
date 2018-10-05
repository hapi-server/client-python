import os
import re
import json
from datetime import datetime
import warnings
import sys
import time
import pickle

import numpy as np
import pandas

sys.tracebacklimit = 1000  # Turn tracebacklimit back to default

def error(msg):
    # TODO: Return more specific exception. Will need to update test_hapi.py
    # because it keys on exception value for certain tests.
    print('\n')
    #sys.tracebacklimit = 0  # Suppress traceback
    # TODO: The problem with this is that it changes the traceback
    # limit globally.
    raise Exception(msg)

# Start compatability code
if sys.version_info[0] > 2:
    # Tested with sys.version = 3.6.5 |Anaconda, Inc.| (default, Apr 26 2018, 08:42:37) \n[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
    import urllib.request, urllib.parse, urllib.error
else:
    # Tested with sys.version = 2.7.15 |Anaconda, Inc.| (default, May  1 2018, 18:37:05) \n[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
    import urllib
    import urllib2

def urlerror(e, url):

    def unknown():
        body = e.read().decode('utf8')
        if len(body) > 0:
            error('\n"HTTP %d - %s" returned by %s. Response body:\n%s' % (e.code, e.reason, url, body))
        else:
            error('\n"HTTP %d - %s" returned by %s.' % (e.code, e.reason, url))

    try:
        jres = json.load(e)
    except:
        unknown()

    if jres['status'] and jres['status']['message']:
        error('\n%s\n  %s\n' % (url, jres['status']['message']))
        if jres['status'] and jres['status']['message']:
            error('\n%s\n  %s\n' % (url, jres['status']['message']))
        else:
            unknown()
    else:
        unknown()

def urlopen(url):
    if sys.version_info[0] > 2:
        try:
            res = urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            urlerror(e, url)
    else:
        try:
            res = urllib2.urlopen(url)
        except urllib2.URLError as e:
            urlerror(e, url)

    return res

def urlretrieve(url, fname):
    if sys.version_info[0] > 2:
        try:
            urllib.request.urlretrieve(url, fname)
        except urllib.error.URLError as e:
            urlerror(e, url)
    else:
        try:
            urllib.urlretrieve(url, fname)
        except urllib2.URLError as e:
            urlerror(e, url)
# End compatability code

def jsonparse(res):
    try:
        return json.load(res)
    except:
        error('Could not parse JSON from %s' % res.geturl())

def printf(format, *args): sys.stdout.write(format % args)

def hapi(*args, **kwargs):
    """Request data from a HAPI server.

    For additional documentation and demonstration, see
    https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb

    Version: 0.0.6

    Parameters
    ----------
    server : str
        A string with the url to the HAPI compliant server. A HAPI URL
        always ends with "/hapi".
    dataset : str
        A string specifying a dataset from a server
    parameters: str
        Comma-separated list of parameters in dataset
    start_time: str
        The start time of the requested data
    end_time: str
        The end time of the requested data; end times are exclusive - the
        last data record returned by a HAPI server should be before the
        given end_time.
    options : dict
        The following options are available.
            logging (False) - Log to console
            cache (True) - Save responses and processed responses in cache_dir
            cache_dir (./hapi-data)
            use_cache (True) - Use files in cache_dir if found
            serverlist (https://github.com/hapi-server/servers/raw/master/all.txt)

    Returns
    -------
    result : various
        Results depend on the input parameters.

        Servers = hapi() or hapi() returns a list of data server URLs from
        https://github.com/hapi-server/data-specification/blob/master/servers.txt

        Dataset = hapi(Server) returns a dict of datasets available from a
        URL given by the string Server.  The dictionary structure follows the
        HAPI JSON structure.

        Parameters = hapi(Server, Dataset) returns a dictionary of parameters
        in the string Dataset.  The dictionary structure follows the HAPI JSON
        structure.

        Metadata = hapi(Server, Dataset, Parameters) or HAPI(...) returns metadata
        associated each parameter in the comma-separated string Parameters.

        Data = hapi(Server, Dataset, Parameters, Start, Stop) returns a dictionary
        with elements corresponding to Parameters, e.g., if
        Parameters='scalar,vector' and the number of records returned is N, then

        Data['Time'] is a NumPy array of datetimes with shape (N)
        Data['scalar'] is a NumPy array of shape (N)
        Data['vector'] is a NumPy array of shape (N,3)

    References
    ----------
        * `HAPI Server Definition <https://github.com/hapi-server/client-python>`

    Examples
    ----------
       See https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb
    """

    __version__ = '0.0.6' # This is modified by misc/setversion.py. See Makefile.

    nin = len(args)

    if nin > 0:
        SERVER = args[0]
    if nin > 1:
        DATASET = args[1]
    if nin > 2:
        PARAMETERS = args[2]
    if nin > 3:
        START = args[3]
    if nin > 4:
        STOP = args[4]

    # Default options
    DOPTS = {}
    DOPTS.update({'logging': False})
    DOPTS.update({'cache': True})
    DOPTS.update({'cache_dir': os.getcwd() + os.path.sep + 'hapi-data'})
    DOPTS.update({'use_cache': False})
    DOPTS.update({'server_list': 'https://github.com/hapi-server/servers/raw/master/all.txt'})

    # For testing force transport format. (CSV used binary not available.)
    DOPTS.update({'format': 'binary'}) # Change to 'csv' to always use CSV.
    # For testing csv read methods. See hapi_test.py for usage.
    DOPTS.update({'method': 'pandas'})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            warnings.warn('Warning: Keyword option "%s" is not valid.', key)

    if DOPTS['logging']: printf('Running hapi.py version %s\n',__version__)

    if nin == 0:  # hapi()
        if DOPTS['logging']:
            printf('Reading %s ... ', DOPTS['server_list'])
        # Last .encode('utf8') needed to make Python 2 and 3 types match
        data = urlopen(DOPTS['server_list']).read().decode('utf8').split('\n')
        if DOPTS['logging']:
            printf('Done.\n')
        data = [x for x in data if x]  # Remove empty items (if blank lines)
        # Display server URLs to console.
        if DOPTS['logging']:
            printf('List of HAPI servers in %s:\n', DOPTS['server_list'])
            for url in data:
                printf("   %s\n", url)
        return data

    if nin == 1:  # hapi(SERVER)
        # TODO: Cache
        url = SERVER + '/catalog'
        if DOPTS['logging']:
            printf('Downloading %s ... ', url)
        res = urlopen(url)
        meta = jsonparse(res)
        if DOPTS['logging']:
            printf('Done.\n')
        data = meta
        return meta

    if nin == 2:  # hapi(SERVER,DATASET)
        # TODO: Cache
        url = SERVER + '/info?id=' + DATASET
        if DOPTS['logging']:
            printf('Downloading %s ... ', url)
        res = urlopen(url)
        meta = jsonparse(res)
        if DOPTS['logging']:
            printf('Done.\n')
        data = meta
        return meta

    if nin == 3 or nin == 5:
        # hapi(SERVER,DATASET,PARAMETERS) or
        # hapi(SERVER,DATASET,PARAMETERS,START,STOP)

        # urld = url directory (cache directory root path)
        urld = re.sub(r"https*://", "", SERVER)
        urld = re.sub(r'/', '_', urld)
        urld = DOPTS["cache_dir"] + os.path.sep + urld

        urljson = SERVER + '/info?id=' + DATASET + '&parameters=' + PARAMETERS
        # Metadata files do not need START/STOP
        fname = '%s_%s' % (DATASET,re.sub(',', '-', PARAMETERS))
        fnamejson = urld + os.path.sep + fname + '.json'
        fnamepkl  = urld + os.path.sep + fname + '.pkl'

        if nin == 5: # Data requested
            fname = '%s_%s_%s_%s' % (DATASET,re.sub(',', '-', PARAMETERS),
                                     re.sub(r'-|:|\.|Z', '', START),
                                     re.sub(r'-|:|\.|Z', '', STOP))
            fnamecsv = urld + os.path.sep + fname + '.csv'
            fnamebin = urld + os.path.sep + fname + '.bin'
            urlcsv = SERVER + '/data?id=' + DATASET + '&parameters=' + \
                     PARAMETERS + '&time.min=' + START + '&time.max=' + STOP
            urlbin = urlcsv + '&format=binary'
            fnamenpy = urld + os.path.sep + fname + '.npy'

        metaloaded = False
        if DOPTS["use_cache"]:
            if os.path.isfile(fnamepkl):
                if DOPTS['logging']: printf('Reading %s ... ', fnamepkl)
                f = open(fnamepkl, 'rb')
                meta = pickle.load(f)
                f.close()
                if DOPTS['logging']: printf('Done.\n')
                metaloaded = True
                if nin == 3: return meta
            if metaloaded and os.path.isfile(fnamenpy):
                if DOPTS['logging']: printf('Reading %s ... ', fnamenpy)
                f = open(fnamenpy, 'rb')
                data = np.load(f)
                f.close()
                if DOPTS['logging']: printf('Done.\n')
                return data, meta

        if (DOPTS["cache"]):
            # Create cache directory
            if not os.path.exists(DOPTS["cache_dir"]):
                os.makedirs(DOPTS["cache_dir"])
            if not os.path.exists(urld):
                os.makedirs(urld)

        if not metaloaded:
            if DOPTS['logging']: printf('Downloading %s ... ', urljson)
            res = urlopen(urljson)
            meta = jsonparse(res)
            if DOPTS['logging']: printf('Done.\n')

        meta.update({"x_server": SERVER})
        meta.update({"x_dataset": DATASET})
        meta.update({"x_parameters": PARAMETERS})
        meta.update({"x_metaFile": fnamejson})
        meta.update({"x_requestDate": datetime.now().isoformat()[0:19]})
        meta.update({"x_cacheDir": urld})

        if nin == 5:
            meta.update({"x_time.min": START})
            meta.update({"x_time.max": STOP})
            if DOPTS['format'] == 'binary':
                meta.update({"x_dataFile": fnamebin})
            else:
                meta.update({"x_dataFile": fnamecsv})

        if DOPTS["cache"]:
            if DOPTS['logging']: printf('Writing %s ... ', fnamejson)
            f = open(fnamejson, 'w')
            json.dump(meta, f, indent=4)
            f.close()
            if DOPTS["logging"]: printf('Done.\n')

        if nin == 3:
            return meta

        cformats = ['csv', 'binary']  # client formats
        if not DOPTS['format'] in cformats:
            raise ValueError('This client does not handle transport '
                             'format "%s".  Available options: %s'
                             % (DOPTS['format'], ', '.join(cformats)))

        # See if server supports binary
        if DOPTS['format'] != 'csv':
            res = urlopen(SERVER + '/capabilities')
            caps = jsonparse(res)
            sformats = caps["outputFormats"]  # Server formats
            if not DOPTS['format'] in sformats:
                warnings.warn('Requested transport format "%s" not avaiable '
                              'from %s. Will use "csv". Available options: %s'
                              % (DOPTS['format'], SERVER, ', '.join(sformats)))
                DOPTS['format'] = 'csv'

        pnames, psizes, dt = [], [], []
        # Each element of cols is an array with start/end column number of
        # parameter.
        cols = np.zeros([len(meta["parameters"]), 2], dtype=np.int32)
        ss = 0  # running sum of prod(size)

        # String or ISOTime parameter with no length attribute in metadata
        # (length attribute is required only for primary time column)
        missing_length = False

        for i in range(0, len(meta["parameters"])):
            ptype = str(meta["parameters"][i]["type"])
            pnames.append(str(meta["parameters"][i]["name"]))
            if 'size' in meta["parameters"][i]:
                psizes.append(meta["parameters"][i]['size'])
            else:
                psizes.append(1)

            # For size = [N] case, readers want
            # dtype = ('name', type, N) not dtype = ('name', type, [N])
            if type(psizes[i]) is list and len(psizes[i]) == 1:
                psizes[i] = psizes[i][0]

            cols[i][0] = ss  # First column of parameter
            cols[i][1] = ss + np.prod(psizes[i]) - 1  # Last column of parameter
            ss = cols[i][1] + 1

            if ptype == 'double':
                dtype = (pnames[i], '<d', psizes[i])
            if ptype == 'integer':
                dtype = (pnames[i], np.int32, psizes[i])

            if DOPTS['format'] == 'binary':
                # TODO: If 'length' not available, warn and fall back to CSV.
                # length attribute required for all parameters if
                # format=binary.
                if ptype == 'string' or ptype == 'isotime':
                    dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])
            else:
                # length attribute may not be given (but must be given for
                # first parameter technically)
                if ptype == 'string' or ptype == 'isotime':
                    if 'length' in meta["parameters"][i]:
                        # length is specified for parameter in metadata. Use it.
                        if ptype == 'string' or 'isotime':
                            dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])
                    else:
                        # A string or isotime parameter did not have a length.
                        # Will need to use slower CSV read method.
                        missing_length = True
                        if ptype == 'string' or ptype == 'isotime':
                            dtype = (pnames[i], object, psizes[i])

            # For testing reader. Force use of slow reader.
            if DOPTS['format'] == 'csv':
                if DOPTS['method'] == 'numpynolength' or DOPTS['method'] == 'pandasnolength':
                    missing_length = True
                    if ptype == 'string' or 'isotime':
                        dtype = (pnames[i], object, psizes[i])

            dt.append(dtype)

        # length attribute required for all parameters when serving binary but
        # is only required for time parameter when serving CSV. This catches
        # case where server provides binary but is missing a length attribute
        # in one or more string parameters that were requested.
        if DOPTS['format'] == 'binary' and missing_length:
            warnings.warn('Requesting CSV instead of binary because of problem with server metadata.')
            DOPTS['format'] == 'csv'

        # Read the data.
        if DOPTS['format'] == 'binary':
            # HAPI Binary
            if DOPTS["cache"]:
                if DOPTS['logging']: printf('Saving %s ... ', urlbin)
                tic0 = time.time()
                urlretrieve(urlbin, fnamebin)
                toc0 = time.time()-tic0
                if DOPTS['logging']: printf('Done.\n')
                if DOPTS['logging']: printf('Reading %s ... ', fnamebin)
                tic = time.time()
                data = np.fromfile(fnamebin, dtype=dt)
            else:
                from io import BytesIO
                if DOPTS['logging']: printf('Getting %s ... ', urlbin)
                tic0 = time.time()
                fnamebin = BytesIO(urlopen(urlbin).read())
                toc0 = time.time()-tic0
                if DOPTS['logging']: printf('Done.\n')
                if DOPTS['logging']: printf('Reading %s ... ', fnamebin)
                tic = time.time()
                data = np.frombuffer(fnamebin.read(), dtype=dt)
            if DOPTS['logging']: printf('Done.\n')
            toc = time.time() - tic
        else:
            # HAPI CSV
            if DOPTS["cache"]:
                if DOPTS['logging']: printf('Saving %s ... ', urlcsv)
                tic0 = time.time()
                urlretrieve(urlcsv, fnamecsv)
                toc0 = time.time() - tic0
            else:
                from io import StringIO
                if DOPTS['logging']: printf('Getting %s ... ', urlcsv)
                tic0 = time.time()
                fnamecsv = StringIO(urlopen(urlcsv).read().decode())
                toc0 = time.time() - tic0
            if DOPTS['logging']: printf('Done.\n')
            if DOPTS['logging']: printf('Reading %s ... ', fnamecsv)

            if not missing_length:
                # All string and isotime parameters have a length in metadata
                tic = time.time()
                if DOPTS['method'] == 'numpy':
                    data = np.genfromtxt(fnamecsv, dtype=dt, delimiter=',')
                    toc = time.time() - tic
                if DOPTS['method'] == 'pandas':
                    # Read file into Pandas DataFrame
                    df = pandas.read_csv(fnamecsv, sep=',', header=None)

                    # Allocate output N-D array (It is not possible to pass dtype=dt
                    # as computed to pandas.read_csv; pandas dtype is different
                    # from numpy's dtype.)
                    data = np.ndarray(shape=(len(df)), dtype=dt)

                    # Insert data from dataframe 'df' columns into N-D array 'data'
                    for i in range(0, len(pnames)):
                        shape = np.append(len(data), psizes[i])
                        # In numpy 1.8.2 and Python 2.7, this throws an error
                        # for no apparent reason. Works as expected in numpy 1.10.4
                        data[pnames[i]] = np.squeeze(np.reshape(df.values[:, np.arange(cols[i][0], cols[i][1]+1)], shape))

                    toc = time.time() - tic
            else:
                # At least one requested string or isotime parameter does not
                #  have a length in metadata
                if DOPTS['method'] == 'numpynolength':
                    tic = time.time()
                    # With dtype='None', the data type is determined automatically
                    table = np.genfromtxt(fnamecsv, dtype=None, delimiter=',',
                                          encoding='utf-8')
                    # table is a 1-D array. Each element is a row in the file.
                    # - If the data types are not the same for each column,
                    # the elements are tuples with length equal to the number
                    # of columns.
                    # - If the data types are the same for each column, which
                    # will happen if only Time is requested or Time and
                    # a string or isotime parameter is requested, then table
                    # has rows that are 1-D numpy arrays.

                    # Contents of 'table' will be placed into N-D array 'data'.
                    data = np.ndarray(shape=(len(table)), dtype=dt)

                    # Insert data from 'table' into N-D array 'data'
                    if (table.dtype.names == None):
                        if len(pnames) == 1:
                            # Only time parameter requested.
                            # import pdb; pdb.set_trace()
                            data[pnames[0]] = table[:]
                        else:
                            # All columns in 'table' have the same data type
                            # so table is a 2-D numpy matrix
                            #import pdb; pdb.set_trace()
                            for i in range(0, len(pnames)):
                                shape = np.append(len(data), psizes[i])
                                data[pnames[i]] = np.squeeze(np.reshape(table[:, np.arange(cols[i][0], cols[i][1]+1)], shape))
                    else:
                        # Table is not a 2-D numpy matrix.
                        # Extract each column (don't know how to do this with slicing
                        # notation, e.g., data['varname'] = table[:][1:3]. Instead,
                        # loop over each parameter (pn) and aggregate columns.
                        # Then insert aggregated columns into N-D array 'data'.
                        #import pdb; pdb.set_trace()
                        for pn in range(0, len(cols)):
                            shape = np.append(len(data), psizes[pn])
                            for c in range(cols[pn][0], cols[pn][1]+1):
                                if c == cols[pn][0]:  # New parameter
                                    tmp = table[table.dtype.names[c]]
                                else: # Aggregate
                                    tmp = np.vstack((tmp, table[table.dtype.names[c]]))
                            tmp = np.squeeze( np.reshape(np.transpose(tmp), shape))
                            data[pnames[pn]] = tmp

                if DOPTS['method'] == 'pandasnolength':
                    tic = time.time()

                    # Read file into Pandas DataFrame
                    df = pandas.read_csv(fnamecsv, sep=',', header=None)

                    # Allocate output N-D array (It is not possible to pass dtype=dt
                    # as computed to pandas.read_csv, so need to create new ND array.)
                    # print(dt)
                    # import pdb; pdb.set_trace()
                    data = np.ndarray(shape=(len(df)), dtype=dt)

                    # Insert data from dataframe into N-D array
                    for i in range(0, len(pnames)):
                        shape = np.append(len(data), psizes[i])
                        # In numpy 1.8.2 and Python 2.7, this throws an error for no apparent reason.
                        # Works as expected in numpy 1.10.4
                        data[pnames[i]] = np.squeeze(np.reshape(df.values[:, np.arange(cols[i][0], cols[i][1]+1)], shape))

                # If any of the parameters are strings that do not have an associated
                # length in the metadata, they will have dtype='O' (object).
                # These parameters must be converted to have a dtype='SN', where
                # N is the maximum string length. N is determined automatically
                # when using astype('<S') (astype uses largest N needed).
                dt2 = []
                for i in range(0, len(pnames)):
                    if data[pnames[i]].dtype == 'O':
                        dtype = (pnames[i], str(data[pnames[i]].astype('<S').dtype), psizes[i])
                    else:
                        dtype = dt[i]
                    dt2.append(dtype)

                # Create new N-D array
                data2 = np.ndarray(data.shape, dt2)

                for i in range(0, len(pnames)):
                    if data[pnames[i]].dtype == 'O':
                        data2[pnames[i]] = data[pnames[i]].astype(dt2[i][1])
                    else:
                        data2[pnames[i]] = data[pnames[i]]
                        # Save memory by not copying (does this help?)
                        #data2[pnames[i]] = np.array(data[pnames[i]],copy=False)

                toc = time.time() - tic

            if DOPTS['logging']: printf('Done.\n')

        meta.update({"x_downloadTime": toc0})
        meta.update({"x_readTime": toc})

        if DOPTS["cache"]:
            if DOPTS['logging']: printf('Writing %s ... ', fnamenpy)
            if missing_length:
                np.save(fnamenpy, data2)
            else:
                np.save(fnamenpy, data)

            if DOPTS['logging']: printf('Done.\n')

            if DOPTS['logging']: printf('Writing %s ... ', fnamepkl)
            f = open(fnamepkl, 'wb')
            pickle.dump(meta, f, protocol=2)
            f.close()
            if DOPTS['logging']:
                printf('Done.\n')

        if missing_length:
            return data2, meta
        else:
            return data, meta

def hapitime2datetime(Time, **kwargs):
    """Convert HAPI timestamps to Python datetimes.

    A HAPI-compliant server represents time as an ISO 8601 string
    (with several constraints - see the HAPI specification).
    hapi() reads these into a NumPy array of Python byte literals.

    This function converts the byte literals to Python datetime objects.

    Typical usage:
        data = hapi(...) # Get data
        DateTimes = hapitime2datetime(data['Time']) # Convert

    Parameter
    ----------
    Time:
        - A numpy array of HAPI timestamp byte literals
        - A numpy array of HAPI timestamp strings
        - A list of HAPI timestamp byte literals
        - A list of HAPI timestamp strings
        - A HAPI timestamp byte literal
        - A HAPI timestamp strings

    Returns
    ----------
    A NumPy array Python datetime objects with length = len(Time)

    Examples
    ----------
    All of the following return
      array([datetime.datetime(1970, 1, 1, 0, 0)], dtype=object)

    from hapiclient.hapi import hapitime2datetime
    import numpy as np

    hapitime2datetime(np.array([b'1970-01-01T00:00:00.000Z']))
	hapitime2datetime(np.array(['1970-01-01T00:00:00.000Z']))

    hapitime2datetime([b'1970-01-01T00:00:00.000Z'])
    hapitime2datetime(['1970-01-01T00:00:00.000Z'])

    hapitime2datetime([b'1970-01-01T00:00:00.000Z'])
    hapitime2datetime('1970-01-01T00:00:00.000Z')

    """

    import re
    import time
    from datetime import datetime

    DOPTS = {}
    DOPTS.update({'logging': False})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            warnings.warn('Keyword option "%s" is not valid.' % key)

    if type(Time) == list:
        Time = np.asarray(Time)
    if type(Time) == str or type(Time) == bytes:
        Time = np.asarray([Time])

    if type(Time) != np.ndarray:
        print("error")
    if type(Time[0]) == np.bytes_:
        Time = Time.astype('U')

    tic = time.time()

    try:
        # Will fail if no pandas, if YYY-DOY format and other valid ISO 8601
        # dates such as 2001-01-01T00:00:03.Z
        import pandas
        # When infer_datetime_format is used, TimeStamp object returned.
        # When format=... is used, datetime object is used.
        Time = pandas.to_datetime(Time, infer_datetime_format=True).to_pydatetime()
        toc = time.time() - tic
        if DOPTS['logging']: printf("Pandas processing time = %.4fs, Input = %s\n", toc, Time[0])
        return Time
    except:
        pass

    # Convert from Python byte literals to unicode strings
    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html
    # https://www.b-list.org/weblog/2017/sep/05/how-python-does-unicode/
    # Note the new Time variable requires 4x more memory. 
    Time = Time.astype('U')
    # Could save memory at cost of speed by decoding at each iteration below, e.g.
    # Time[i] -> Time[i].decode('utf-8')

    d = 0
    # Catch case where no trailing Z
    # Technically HAPI ISO 8601 must have trailing Z:
    # https://github.com/hapi-server/data-specification/blob/master/hapi-dev/HAPI-data-access-spec-dev.md#representation-of-time
    if not re.match(r".*Z$", Time[0]):
        d = 1

    pythonDateTime = np.empty(len(Time), dtype=object)

    # Parse date part
    # If h=True then hour given.
    # If hm=True, then hour and minute given.
    # If hms=True, them hour, minute, and second given.
    (h,hm,hms) = (False, False, False)

    if len(Time[0]) == 4 or (len(Time[0]) == 5 and Time[0][-1] == "Z"):
        fmt = '%Y'
        to = 5
    elif re.match(r"[0-9]{4}-[0-9]{3}", Time[0]):
        # YYYY-DOY format
        fmt = "%Y-%j"
        to = 9
        if len(Time[0]) >= 12-d:
            h = True
        if len(Time[0]) >= 15-d:
            hm = True
        if len(Time[0]) >= 18-d:
            hms = True
    elif re.match(r"[0-9]{4}-[0-9]{2}", Time[0]):
        # YYYY-MM-DD format
        fmt = "%Y-%m"
        to = 8
        if len(Time[0]) > 8:
            fmt = fmt + "-%d"
            to = 11
        if len(Time[0]) >= 14-d:
            h = True
        if len(Time[0]) >= 17-d:
            hm = True
        if len(Time[0]) >= 20-d:
            hms = True
    else:
        # TODO: Also check for invalid time string lengths.
        # Should use JSON schema regular expressions for allowed versions of ISO 8601.
        raise ValueError('First time value %s is not a valid HAPI Time' % Time[0])

    fmto = fmt
    if h:
        fmt = fmt + "T%H"
    if hm:
        fmt = fmt + ":%M"
    if hms:
        fmt = fmt + ":%S"

    if re.match(r".*\.[0-9].*$", Time[0]):
        fmt = fmt + ".%f"
    if re.match(r".*\.$", Time[0]) or re.match(r".*\.Z$", Time[0]):
        fmt = fmt + "."

    if re.match(r".*Z$", Time[0]):
        fmt = fmt + "Z"

    for i in range(0, len(Time)):
        pythonDateTime[i] = datetime.strptime(Time[i],fmt)

    toc = time.time() - tic
    if DOPTS['logging']: printf("Manual processing time = %.4fs, Input = %s, fmto = %s, fmt = %s\n", toc, Time[0], fmto, fmt)

    return pythonDateTime
