import os
import re
import json
import time
import pickle

import numpy as np
import pandas

from datetime import datetime

from hapiclient.util import setopts, log, warning
from hapiclient.util import urlopen, urlretrieve, jsonparse


def subset(meta, params):
    """Extract subset of parameters from meta object returned by hapi()
    
    metar = subset(meta, parameters) modifies meta.parameters array so
    it only contains elements for the time variable and the parameters in
    the comma-separated list `parameters`.
    """

    if params == '':
        return meta

    p = params.split(',')
    pm = []  # Parameter names in metadata
    for i in range(0, len(meta['parameters'])):
        pm.append(meta['parameters'][i]['name'])
    for i in range(0, len(p)):
        if p[i] not in pm:
            raise Exception('Parameter %s is not in dataset' % p[i])
    
    pa = [meta['parameters'][0]]  # First parameter is always the time parameter
    for i in range(1, len(pm)):
        if pm[i] in p:
            pa.append(meta['parameters'][i])
    meta['parameters'] = pa
    return meta


def server2dirname(server):
    """Convert a server URL to a directory name."""
    
    urld = re.sub(r"https*://", "", server)
    urld = re.sub(r'/', '_', urld)
    return urld


def cachedir(*args):
    """HAPI cache directory.
    
    cachedir() returns the default directory hapi-data subdirectory of
    system tempdir.

    cachdir(basedir, server)
    """
    import tempfile
    
    if len(args) == 2:
        # cachedir(base_dir, server)
        return args[0] + os.path.sep + server2dirname(args[1])
    else:
        return tempfile.gettempdir() + os.path.sep + 'hapi-data'


def request2path(*args):
    # request2path(server, dataset, parameters, start, stop)
    # request2path(server, dataset, parameters, start, stop, cachedir)

    if len(args) == 5:
        # Use default if cachedir not given.
        cachedirectory = cachedir()
    else:
        cachedirectory = args[5]

    # url subdirectory
    urldirectory = server2dirname(args[0])
    fname = '%s_%s_%s_%s' % (args[1], re.sub(',', '-', args[2]),
                             re.sub(r'-|:|\.|Z', '', args[3]),
                             re.sub(r'-|:|\.|Z', '', args[4]))

    return os.path.join(cachedirectory, urldirectory, fname)


def hapiopts():
    """Return allowed options for hapi().
    
       Used by hapiplot() and hapi().
    """
    # Default options
    opts = {
                'logging': False,
                'cache': True,
                'cachedir': cachedir(),
                'usecache': False,
                'server_list': 'https://github.com/hapi-server/servers/raw/master/all.txt',
                'format': 'binary',
                'method': 'pandas'
            }

    # format = 'binary' is used by default and CSV used if binary is not available from server.
    # This should option should be excluded from the help string.
 
    # method = 'pandas' is used by default. Other methods 
    # (numpy, pandasnolength, numpynolength)can be used for testing
    # CSV read methods. See test_hapi.py for comparsion.
    # This should option should be excluded from the help string.
    
    return opts


def hapi(*args, **kwargs):
    """Request data from a HAPI server.

    For additional documentation and demonstration, see
    <https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb>

    Version: 0.1.0

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
            cache (True) - Save responses and processed responses in cachedir
            cachedir (./hapi-data)
            usecache (True) - Use files in cachedir if found
            serverlist (https://github.com/hapi-server/servers/raw/master/all.txt)

    Returns
    -------
    result : various
        Results depend on the input parameters.

        Servers = hapi() returns a list of available HAPI server URLs from
        <https://github.com/hapi-server/data-specification/blob/master/all.txt>

        Dataset = hapi(Server) returns a dict of datasets available from a
        URL given by the string Server.  The dictionary structure follows the
        HAPI JSON structure.

        Parameters = hapi(Server, Dataset) returns a dictionary of parameters
        in the string Dataset.  The dictionary structure follows the HAPI JSON
        structure.

        Metadata = hapi(Server, Dataset, Parameters) returns metadata
        associated each parameter in the comma-separated string Parameters. The
        dictionary structure follows the HAPI JSON structure.

        Data = hapi(Server, Dataset, Parameters, Start, Stop) returns a 
        dictionary with elements corresponding to Parameters, e.g., if
        Parameters = 'scalar,vector' and the number of records in the time
        range Start <= t < Stop returned is N, then

          Data['scalar'] is a NumPy array of shape (N)
          Data['vector'] is a NumPy array of shape (N,3)
          Data['Time'] is a NumPy array of byte literals with shape (N).
          
          Byte literal times can be converted to Python datetimes using 
          
          dtarray = hapitime2datetime(Data['Time'])
        
        Data, Meta = hapi(Server, Dataset, Parameters, Start, Stop) returns
        the metadata for parameters in Meta.

    References
    ----------
        * `HAPI Server Definition <https://github.com/hapi-server/data-specification>`

    Examples
    ----------
       See <https://github.com/hapi-server/client-python-notebooks>
    """

    __version__ = '0.1.0'  # This is modified by misc/setversion.py. See Makefile.

    nin = len(args)

    if nin > 0:
        SERVER = args[0]
    if nin > 1:
        DATASET = args[1]
    if nin > 2:
        PARAMETERS = args[2]
        if re.search(r', ', PARAMETERS):
            warning("hapi", "Removing spaces after commas in given parameter list of '" + PARAMETERS + "'")
            PARAMETERS = re.sub(r',\s+', ',', PARAMETERS)
    if nin > 3:
        START = args[3]
    if nin > 4:
        STOP = args[4]

    # Override defaults
    opts = setopts(hapiopts(), kwargs)
    
    log('Running hapi.py version %s' % __version__, opts)

    if nin == 0:  # hapi()
        log('Reading %s' % opts['server_list'], opts)
        # decode('utf8') in following needed to make Python 2 and 3 types match.
        data = urlopen(opts['server_list']).read().decode('utf8').split('\n')
        data = [x for x in data if x]  # Remove empty items (if blank lines)
        # Display server URLs to console.
        log('List of HAPI servers in %s:\n' % opts['server_list'], opts)
        for url in data:
            log("   %s" % url, opts)
        return data

    if nin == 1:  # hapi(SERVER)
        # TODO: Cache
        url = SERVER + '/catalog'
        log('Reading %s' % url, opts)
        res = urlopen(url)
        meta = jsonparse(res)
        return meta

    if nin == 2:  # hapi(SERVER, DATASET)
        # TODO: Cache
        url = SERVER + '/info?id=' + DATASET
        log('Reading %s' % url, opts)
        res = urlopen(url)
        meta = jsonparse(res)
        return meta
    
    if nin == 4:
        raise ValueError('A stop time is required if a start time is given.')

    if nin == 3 or nin == 5:
        # hapi(SERVER, DATASET, PARAMETERS) or
        # hapi(SERVER, DATASET, PARAMETERS, START, STOP)
                
        # urld = url subdirectory of cachedir to store files from SERVER
        urld = cachedir(opts["cachedir"], SERVER)

        if opts["cachedir"]: log('hapi(): file directory = %s' % urld, opts)

        urljson = SERVER + '/info?id=' + DATASET

        # Output from urljson will be saved in a .json file. Parsed json
        # will be stored in a .pkl file. Metadata for all parameters is
        # requested and response is subsetted so only metadata for PARAMETERS
        # is returned.
        fnamejson = urld + os.path.sep + DATASET + '.json'
        fnamepkl  = urld + os.path.sep + DATASET + '.pkl'

        if nin == 5:  # Data requested
            # URL to get CSV (will be used if binary response is not available)
            urlcsv = SERVER + '/data?id=' + DATASET + '&parameters=' + \
                     PARAMETERS + '&time.min=' + START + '&time.max=' + STOP
            # URL for binary request
            urlbin = urlcsv + '&format=binary'

            # Raw CSV and HAPI Binary (no header) will be stored in .csv and 
            # .bin files. Parsed response of either CSV or HAPI Binary will
            # be stored in a .npy file.
            fname = '%s_%s_%s_%s' % (DATASET, re.sub(',', '-', PARAMETERS),
                                     re.sub(r'-|:|\.|Z', '', START),
                                     re.sub(r'-|:|\.|Z', '', STOP))
            fnamecsv = urld + os.path.sep + fname + '.csv'
            fnamebin = urld + os.path.sep + fname + '.bin'
            fnamenpy = urld + os.path.sep + fname + '.npy'
            
            # fnamepklx will contain additional metadata about the request
            # including d/l time, parsing time, and the location of files.
            fnamepklx = request2path(SERVER, DATASET, PARAMETERS, START, STOP, opts['cachedir'])
            fnamepklx = fnamepklx + ".pkl"

        metaFromCache = False
        if opts["usecache"]:
            if nin == 3 and os.path.isfile(fnamepkl):
                # Read cached metadata from .pkl file.
                # This returns subsetted metadata with no additional "x_"
                # information (which is stored in fnamepklx).
                log('Reading %s' % fnamepkl.replace(urld + '/', ''), opts)
                f = open(fnamepkl, 'rb')
                meta = pickle.load(f)
                f.close()
                metaFromCache = True
                # Remove parameters not requested.
                meta = subset(meta, PARAMETERS)
                return meta
            if os.path.isfile(fnamepklx):
                # Read subsetted meta file with x_ information
                log('Reading %s' % fnamepklx.replace(urld + '/', ''), opts)
                f = open(fnamepklx, 'rb')
                meta = pickle.load(f)
                metaFromCache = True
                f.close()
        
        if not metaFromCache:
            # No cached metadata loaded so request it from server.
            log('Reading %s' % urljson.replace(urld + '/', ''), opts)
            res = urlopen(urljson)
            meta = jsonparse(res)

        # Add information to metdata so we can figure out request needed
        # to generated it. Will also be used for labeling plots by hapiplot().
        meta.update({"x_server": SERVER})
        meta.update({"x_dataset": DATASET})

        if opts["cache"]:
            if not os.path.exists(urld): os.makedirs(urld)

        if opts["cache"] and not metaFromCache:
            # Cache metadata for all parameters if it was not already loaded
            # from cache. Note that fnamepklx is written after data downloaded
            # and parsed.
            log('Writing %s ' % fnamejson.replace(urld + '/', ''), opts)
            f = open(fnamejson, 'w')
            json.dump(meta, f, indent=4)
            f.close()
            
            log('Writing %s ' % fnamepkl.replace(urld + '/', ''), opts)
            f = open(fnamepkl, 'wb')
            # protocol=2 used for Python 2.7 compatability.
            pickle.dump(meta, f, protocol=2)
            f.close()

        # Remove unrequested parameters if they have not have already been
        # removed (b/c loaded from cache).
        if not metaFromCache:
            meta = subset(meta, PARAMETERS)

        if nin == 3:
            return meta

        if opts["usecache"] and os.path.isfile(fnamenpy):
            # Read cached data file.
            log('Reading %s ' % fnamenpy.replace(urld + '/', ''), opts)
            f = open(fnamenpy, 'rb')
            data = np.load(f)                    
            f.close()
            # There is a possibility that the fnamenpy file existed but
            # fnamepklx was not found (b/c removed). In this case, the meta 
            # returned will not have all of the "x_" information inserted below.
            # Code that uses this information needs to account for this.
            return data, meta

        cformats = ['csv', 'binary']  # client formats
        if not opts['format'] in cformats:
            # Check if requested format is implemented by this client.
            raise ValueError('This client does not handle transport '
                             'format "%s".  Available options: %s'
                             % (opts['format'], ', '.join(cformats)))

        # See if server supports binary
        if opts['format'] != 'csv':
            log('Reading %s' % (SERVER + '/capabilities'), opts)
            res = urlopen(SERVER + '/capabilities')
            caps = jsonparse(res)
            sformats = caps["outputFormats"]  # Server formats
            if not opts['format'] in sformats:
                warning("hapi", 'Requested transport format "%s" not avaiable '
                                'from %s. Will use "csv". Available options: %s'
                              % (opts['format'], SERVER, ', '.join(sformats)))
                opts['format'] = 'csv'

        ##################################################################
        # Compute data type varialbe dt used to read HAPI response into
        # a data structure.
        pnames, psizes, dt = [], [], []
        # Each element of cols is an array with start/end column number of
        # parameter.
        cols = np.zeros([len(meta["parameters"]), 2], dtype=np.int32)
        ss = 0  # running sum of prod(size)

        # missing_length = True will be set if HAPI String or ISOTime
        # parameter has no length attribute in metadata (length attribute is
        # required for both in binary but only for primary time column in CSV).
        # When missing_length=True the CSV read gets more complicated.
        missing_length = False

        # Extract sizes and types of parameters.
        for i in range(0, len(meta["parameters"])):
            ptype = str(meta["parameters"][i]["type"])
            pnames.append(str(meta["parameters"][i]["name"]))
            if 'size' in meta["parameters"][i]:
                psizes.append(meta["parameters"][i]['size'])
            else:
                psizes.append(1)

            # For size = [N] case, readers want
            # dtype = ('name', type, N)
            # not 
            # dtype = ('name', type, [N])
            if type(psizes[i]) is list and len(psizes[i]) == 1:
                psizes[i] = psizes[i][0]

            if type(psizes[i]) is list and len(psizes[i]) > 1:
                psizes[i] = list(reversed(psizes[i]))
                
            # First column of ith parameter.
            cols[i][0] = ss
            # Last column of ith parameter.
            cols[i][1] = ss + np.prod(psizes[i]) - 1
            # Running sum of columns.
            ss = cols[i][1] + 1

            # HAPI numerical formats are 64-bit LE floating point and  32-bit LE
            # signed integers.
            if ptype == 'double':
                dtype = (pnames[i], '<d', psizes[i])
            if ptype == 'integer':
                dtype = (pnames[i], np.dtype('<i4'), psizes[i])

            if opts['format'] == 'binary':
                # TODO: If 'length' not available, warn and fall back to CSV.
                # Technically, server response is invalid b/c length attribute
                # required for all parameters if format=binary.
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
            if opts['format'] == 'csv':
                if opts['method'] == 'numpynolength' or opts['method'] == 'pandasnolength':
                    missing_length = True
                    if ptype == 'string' or ptype == 'isotime':
                        dtype = (pnames[i], object, psizes[i])

            dt.append(dtype)
        ##################################################################

        # length attribute required for all parameters when serving binary but
        # is only required for time parameter when serving CSV. This catches
        # case where server provides binary but is missing a length attribute
        # in one or more string parameters that were requested. Note that
        # this is will never be true. Need to update code above.
        # if opts['format'] == 'binary' and missing_length:
        #    warnings.warn('Requesting CSV instead of binary because of problem with server metadata.')
        #    opts['format'] == 'csv'

        # Read the data. toc0 is time to download (or build buffer); 
        # toc is time to parse (includes download time if buffered IO is used.)
        if opts['format'] == 'binary':
            # HAPI Binary
            if opts["cache"]:
                log('Writing %s to %s' % (urlbin, fnamebin.replace(urld + '/', '')), opts)
                tic0 = time.time()
                urlretrieve(urlbin, fnamebin)
                toc0 = time.time()-tic0
                log('Reading %s' % fnamebin.replace(urld + '/', ''), opts)
                tic = time.time()
                data = np.fromfile(fnamebin, dtype=dt)
                toc = time.time() - tic
            else:
                from io import BytesIO
                log('Creating buffer: %s' % urlbin, opts)
                tic0 = time.time()
                buff = BytesIO(urlopen(urlbin).read())
                toc0 = time.time()-tic0
                log('Parsing buffer.', opts)
                tic = time.time()
                data = np.frombuffer(buff.read(), dtype=dt)
                toc = time.time() - tic
        else:
            # HAPI CSV
            if opts["cache"]:
                log('Saving %s' % urlcsv.replace(urld + '/', ''), opts)
                tic0 = time.time()
                urlretrieve(urlcsv, fnamecsv)
                toc0 = time.time() - tic0
                log('Parsing %s' % fnamecsv.replace(urld + '/', ''), opts)
            else:
                from io import StringIO
                log('Creating buffer: %s' % urlcsv.replace(urld + '/', ''), opts)
                tic0 = time.time()
                fnamecsv = StringIO(urlopen(urlcsv).read().decode())
                toc0 = time.time() - tic0
                log('Parsing buffer.', opts)

            if not missing_length:
                # All string and isotime parameters have a length in metadata.
                tic = time.time()
                if opts['method'] == 'numpy':
                    data = np.genfromtxt(fnamecsv, dtype=dt, delimiter=',')
                    toc = time.time() - tic
                if opts['method'] == 'pandas':
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
                # have a length in metadata. More work to do to read. 
                tic = time.time()
                if opts['method'] == 'numpy' or opts['method'] == 'numpynolength':
                    # If requested method was numpy, use numpynolength method.

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
                    if table.dtype.names is None:
                        if len(pnames) == 1:
                            # Only time parameter requested.
                            data[pnames[0]] = table[:]
                        else:
                            # All columns in 'table' have the same data type
                            # so table is a 2-D numpy matrix
                            for i in range(0, len(pnames)):
                                shape = np.append(len(data), psizes[i])
                                data[pnames[i]] = np.squeeze(np.reshape(table[:, np.arange(cols[i][0], cols[i][1]+1)], shape))
                    else:
                        # Table is not a 2-D numpy matrix.
                        # Extract each column (don't know how to do this with slicing
                        # notation, e.g., data['varname'] = table[:][1:3]. Instead,
                        # loop over each parameter (pn) and aggregate columns.
                        # Then insert aggregated columns into N-D array 'data'.
                        for pn in range(0, len(cols)):
                            shape = np.append(len(data), psizes[pn])
                            for c in range(cols[pn][0], cols[pn][1]+1):
                                if c == cols[pn][0]:  # New parameter
                                    tmp = table[table.dtype.names[c]]
                                else:  # Aggregate
                                    tmp = np.vstack((tmp, table[table.dtype.names[c]]))
                            tmp = np.squeeze(np.reshape(np.transpose(tmp), shape))
                            data[pnames[pn]] = tmp

                if opts['method'] == 'pandas' or opts['method'] == 'pandasnolength':
                    # If requested method was pandas, use pandasnolength method.

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

                # Any of the string parameters that do not have an associated
                # length in the metadata will have dtype='O' (object).
                # These parameters must be converted to have a dtype='SN', where
                # N is the maximum string length. N is determined automatically
                # when using astype('<S') (astype uses largest N needed).
                dt2 = []  # Will have dtypes with strings lengths calculated.
                for i in range(0, len(pnames)):
                    if data[pnames[i]].dtype == 'O':
                        dtype = (pnames[i], str(data[pnames[i]].astype('<S').dtype), psizes[i])
                    else:
                        dtype = dt[i]
                    dt2.append(dtype)

                # Create new N-D array which won't have any parameters with
                # type = 'O'.
                data2 = np.ndarray(data.shape, dt2)

                for i in range(0, len(pnames)):
                    if data[pnames[i]].dtype == 'O':
                        data2[pnames[i]] = data[pnames[i]].astype(dt2[i][1])
                    else:
                        data2[pnames[i]] = data[pnames[i]]
                        # Save memory by not copying (does this help?)
                        #data2[pnames[i]] = np.array(data[pnames[i]],copy=False)

            toc = time.time() - tic

        # Extra metadata associated with request will be saved in
        # a pkl file with same base name as npy data file.
        meta.update({"x_server": SERVER})
        meta.update({"x_dataset": DATASET})
        meta.update({"x_parameters": PARAMETERS})
        meta.update({"x_time.min": START})
        meta.update({"x_time.max": STOP})
        meta.update({"x_requestDate": datetime.now().isoformat()[0:19]})
        meta.update({"x_cacheDir": urld})
        meta.update({"x_downloadTime": toc0})
        meta.update({"x_readTime": toc})
        meta.update({"x_metaFileParsed": fnamepkl})
        meta.update({"x_dataFileParsed": fnamenpy})
        meta.update({"x_metaFile": fnamejson})
        if opts['format'] == 'binary':
            meta.update({"x_dataFile": fnamebin})
        else:
            meta.update({"x_dataFile": fnamecsv})

        # Note that this should only technically be
        # written if cache=True. Will do this when output is
        # h = hapi(...)
        # h.data
        # h.meta
        # h.info
        # Create cache directory
        if not os.path.exists(opts["cachedir"]):
            os.makedirs(opts["cachedir"])
        if not os.path.exists(urld):
            os.makedirs(urld)
        log('Writing %s' % fnamepklx, opts)
        f = open(fnamepklx, 'wb')
        pickle.dump(meta, f, protocol=2)
        f.close()

        if opts["cache"]:
            log('Writing %s' % fnamenpy, opts)
            if missing_length:
                np.save(fnamenpy, data2)
            else:
                np.save(fnamenpy, data)

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

    opts = {'logging': False}

    opts = setopts(opts, kwargs)
    
    if type(Time) == list:
        Time = np.asarray(Time)
    if type(Time) == str or type(Time) == bytes:
        Time = np.asarray([Time])

    if type(Time) != np.ndarray:
        print("error")
    
    reshape = False
    if Time.shape[0] != Time.size:
        reshape = True
        shape = Time.shape
        Time = Time.flatten()

    if type(Time[0]) == np.bytes_:
        Time = Time.astype('U')

    tic = time.time()

    try:
        # Will fail if no pandas, if YYY-DOY format and other valid ISO 8601
        # dates such as 2001-01-01T00:00:03.Z
        # When infer_datetime_format is used, TimeStamp object returned.
        # When format=... is used, datetime object is used.
        Time = pandas.to_datetime(Time, infer_datetime_format=True).to_pydatetime()
        if reshape:
            Time = np.reshape(Time, shape)
        toc = time.time() - tic
        log("Pandas processing time = %.4fs, Input = %s\n" % (toc, Time[0]), opts)
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
    (h, hm, hms) = (False, False, False)

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
    
    # TODO: Why not use pandas.to_datetime here with fmt
    for i in range(0, len(Time)):
        pythonDateTime[i] = datetime.strptime(Time[i], fmt)

    toc = time.time() - tic
    log("Manual processing time = %.4fs, Input = %s, fmto = %s, fmt = %s\n" % (toc, Time[0], fmto, fmt), opts)

    if reshape:
        pythonDateTime = np.reshape(pythonDateTime, shape)

    return pythonDateTime



