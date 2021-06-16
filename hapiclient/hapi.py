import os
import re
import sys
import json
import time
import pickle
import warnings
from datetime import datetime, timedelta

import pandas
import isodate
import numpy as np
from joblib import Parallel, delayed

from hapiclient.hapitime import hapitime2datetime, hapitime_reformat
from hapiclient.util import setopts, log, warning, error
from hapiclient.util import urlopen, urlretrieve, jsonparse


def subset(meta, params):
    """Extract subset of parameters from meta object returned by hapi().

    ``metar = subset(meta, parameters)`` modifies ``meta["parameters"]`` array
    so that it only contains elements for the time variable and the parameters
    in the comma-separated string ``parameters``.
    """

    if params == '':
        return meta

    p = params.split(',')
    pm = []  # Parameter names in metadata
    for i in range(0, len(meta['parameters'])):
        pm.append(meta['parameters'][i]['name'])

    # Check for parameters requested that are not in metadata
    for i in range(0, len(p)):
        if p[i] not in pm:
            error('Parameter %s is not in meta' % p[i] + '\n')
            return

    pa = [meta['parameters'][0]]  # First parameter is always the time parameter

    params_reordered = []  # Re-ordered params
    # If time parameter explicity requested, put it first in params_reordered.
    if meta['parameters'][0]['name'] in p:
        params_reordered = [meta['parameters'][0]['name']]

    # Create subset of parameter metadata
    for i in range(1, len(pm)):
        if pm[i] in p:
            pa.append(meta['parameters'][i])
            params_reordered.append(pm[i])
    meta['parameters'] = pa

    params_reordered_str = ','.join(params_reordered)

    if not params == params_reordered_str:
        msg = "\n  " + "Order requested: " + params
        msg = msg + "\n  " + "Order required: " + params_reordered_str
        error('Order of requested parameters does not match order of ' \
              'parameters in server info metadata.' + msg + '\n')

    return meta


def cachedir(*args):
    """HAPI cache directory.

    cachedir() returns tempfile.gettempdir() + os.path.sep + 'hapi-data'

    cachdir(basedir, server) returns basedir + os.path.sep + server2dirname(server)
    """
    import tempfile

    if len(args) == 2:
        # cachedir(base_dir, server)
        return args[0] + os.path.sep + server2dirname(args[1])
    else:
        # cachedir()
        return tempfile.gettempdir() + os.path.sep + 'hapi-data'


def server2dirname(server):
    """Convert a server URL to a directory name."""

    urld = re.sub(r"https*://", "", server)
    urld = re.sub(r'/', '_', urld)
    return urld


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
    fname = '%s_%s_%s_%s' % (re.sub('/', '_', args[1]),
                             re.sub(',', '-', args[2]),
                             re.sub(r'-|:|\.|Z', '', args[3]),
                             re.sub(r'-|:|\.|Z', '', args[4]))

    return os.path.join(cachedirectory, urldirectory, fname)


def hapiopts():
    """Return dict of default options for hapi()

    Used by hapiplot() and hapi().

    format = 'binary' is used by default and CSV used if binary is not
    available from server. This should option should be excluded from the help
    string.

    method = 'pandas' is used by default. Other methods
    (numpy, pandasnolength, numpynolength) can be used for testing
    CSV read methods. See test/test_hapi.py for comparison.
    """

    # Default options
    opts = {
        'logging': False,
        'cache': True,
        'cachedir': cachedir(),
        'usecache': False,
        'server_list': 'https://github.com/hapi-server/servers/raw/master/all.txt',
        'format': 'binary',
        'method': 'pandas',
        'parallel': False,
        'n_parallel': 5,
        'n_chunks': None,
        'dt_chunk': None,
    }

    return opts


def hapi(*args, **kwargs):
    """Request data from a HAPI server.

    Version: 0.2.1


    Examples
    ----------
    `Jupyter Notebook <https://colab.research.google.com/drive/11Zy99koiE90JKJ4u_KPTaEBMQFzbfU3P?usp=sharing>_`

    Parameters
    ----------
    server : str
        A string with the URL to a HAPI compliant server. (A HAPI URL
        always ends with "/hapi").
    dataset : str
        A string specifying a dataset from a `server`
    parameters: str
        A Comma-separated list of parameters in `dataset`
    start: str
        The start time of the requested data
    stop: str
        The end time of the requested data; end times are exclusive - the
        last data record returned by a HAPI server should have a timestamp
        before `start`.
    options : dict

            `logging` (False) - Log to console

            `cache` (True) - Save responses and processed responses in cachedir

            `cachedir` (./hapi-data)

            `usecache` (True) - Use files in `cachedir` if found

            `serverlist` (https://github.com/hapi-server/servers/raw/master/all.txt)

            `parallel` (False) If true, make up to `n_parallel` requests to
                server in parallel (uses threads)

            `n_parallel` (5) Maximum number of parallel requests to server.
                Max allowed is 5.

            `n_chunks` (None) Get data by making `n_chunks` requests by splitting
                requested time range. `dt_chunk` is ignored if `n_chunks` is
                not `None`. Allowed values are integers > 1.

            `dt_chunk` ('infer') For requests that span a time range larger
                than the default chunk size for a given dataset cadence, the
                client will split request into chunks if `dt_chunk` is not
                `None`.

                Allowed values of `dt_chunk` are 'infer', `None`, and an ISO 8601
                duration that is unambiguous (durations that include Y and M are not
                allowed). The default chunk size is determined based on the cadence
                of the dataset requested according to

                    cadence < PT1S              dt_chunk='PT1H'
                    PT1S <= cadence <= PT1H     dt_chunk='P1D'
                    cadence > PT1H              dt_chunk='P30D'
                    cadence >= P1D              dt_chunk='P365D'

                If the dataset does not have a cadence listed in its metadata, an
                attempt is made to infer the cadence by requesting a small time range
                of data and doubling the time range until 10 records are in the response.
                The cadence used to determine the chunk size is then the average time
                difference between records.

                If requested time range is < 1/2 of chunk size, only one request is
                made. Otherwise, start and/or stop are modified to be at hour, day,
                month or year boundaries and requests are made for a time span of a
                full chunk, and trimming is performed. For example,

                    Cadence = PT1M and request for
                        start/stop=1999-11-12T00:10:00/stop=1999-11-12T12:09:00
                        Chunk size is P1D and requested time range < 1/2 of this
                        =>  Default behavior
                    Cadence = PT1M and request for
                        start/stop=1999-11-12T00:10:00/1999-11-12T12:10:00
                        Chunk size is P1D and requested time range >= 1/2 of this
                        =>  One request with start/stop=1999-11-12/1999-11-13
                            and trim performed
                    Cadence = PT1M and request for
                        start/stop=1999-11-12T00:10:00/1999-11-13T12:09:00
                        Chunk size is P1D and requested time range > than this
                        =>  Two requests:
                            (1) start/stop=1999-11-12/start=1999-11-13
                            (2) start/stop=1999-11-13/start=1999-11-14
                            and trim performed


    Returns
    -------
    result : various
        `result` depends on the input parameters.

        servers = hapi() returns a list of available HAPI server URLs from
        https://github.com/hapi-server/data-specification/blob/master/all.txt

        dataset = hapi(server) returns a dict of datasets available from a
        URL given by the string `server`.  The dictionary structure follows the
        HAPI JSON structure.

        parameters = hapi(server, dataset) returns a dictionary of parameters
        in the string `dataset`. The dictionary structure follows the HAPI JSON
        structure.

        metadata = hapi(server, dataset, parameters) returns metadata
        associated each parameter in the comma-separated string `parameters`. The
        dictionary structure follows the HAPI JSON structure.

        data = hapi(server, dataset, parameters, start, stop) returns a
        dictionary with elements corresponding to `parameters`, e.g., if
        `parameters` = 'scalar,vector' and the number of records in the time
        range `start` <= t < `stop` returned is N, then

          data['scalar'] is a NumPy array of shape (N)
          data['vector'] is a NumPy array of shape (N,3)
          data['Time'] is a NumPy array of byte literals with shape (N).

          Byte literal times can be converted to Python datetimes using

          dtarray = hapitime2datetime(data['Time'])

        data, meta = hapi(server, dataset, parameters, start, stop) returns
        the metadata for parameters in `meta`.


    References
    ----------
        * `HAPI Server Definition <https://github.com/hapi-server/data-specification>`_

    """

    nin = len(args)

    if nin > 0:
        SERVER = args[0]
    if nin > 1:
        DATASET = args[1]
    if nin > 2:
        PARAMETERS = args[2]
    if nin > 3:
        START = args[3]
        if START[-1] != 'Z':
            # TODO: Consider warning.
            START = START + 'Z'
    if nin > 4:
        STOP = args[4]
        if STOP[-1] != 'Z':
            # TODO: Consider warning.
            STOP = STOP + 'Z'

    # Override defaults
    opts = setopts(hapiopts(), kwargs)

    assert (opts['logging'] in [True, False])
    assert (opts['cache'] in [True, False])
    assert (opts['usecache'] in [True, False])
    assert (opts['format'] in ['binary', 'csv'])
    assert (opts['method'] in ['', 'pandas', 'numpy', 'pandasnolength', 'numpynolength'])
    assert (opts['parallel'] in [True, False])
    assert (isinstance(opts['n_parallel'], int) and opts['n_parallel'] > 1)
    assert (opts['n_chunks'] is None or isinstance(opts['n_chunks'], int) and opts['n_chunks'] > 0)
    assert (opts['dt_chunk'] in [None, 'infer', 'PT1H', 'P1D', 'P1M', 'P1Y'])

    from hapiclient import __version__
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
        meta = jsonparse(res, url)
        return meta

    if nin == 2:  # hapi(SERVER, DATASET)
        # TODO: Cache
        url = SERVER + '/info?id=' + DATASET
        log('Reading %s' % url, opts)
        res = urlopen(url)
        meta = jsonparse(res, url)
        return meta

    if nin == 4:
        error('A stop time is required if a start time is given.')

    if nin == 3 or nin == 5:
        # hapi(SERVER, DATASET, PARAMETERS) or
        # hapi(SERVER, DATASET, PARAMETERS, START, STOP)

        # Extract all parameters.
        if re.search(r', ', PARAMETERS):
            warning("Removing spaces after commas in given parameter list of '" \
                    + PARAMETERS + "'")
            PARAMETERS = re.sub(r',\s+', ',', PARAMETERS)

        # urld = url subdirectory of cachedir to store files from SERVER
        urld = cachedir(opts["cachedir"], SERVER)

        if opts["cachedir"]: log('file directory = %s' % urld, opts)

        urljson = SERVER + '/info?id=' + DATASET

        # Output from urljson will be saved in a .json file. Parsed json
        # will be stored in a .pkl file. Metadata for all parameters is
        # requested and response is subsetted so only metadata for PARAMETERS
        # is returned.
        fname_root = request2path(SERVER, DATASET, '', '', '', opts['cachedir'])
        fnamejson = fname_root + '.json'
        fnamepkl = fname_root + '.pkl'

        if nin == 5:  # Data requested

            tic_totalTime = time.time()

            # URL to get CSV (will be used if binary response is not available)
            urlcsv = SERVER + '/data?id=' + DATASET + '&parameters=' + \
                     PARAMETERS + '&time.min=' + START + '&time.max=' + STOP
            # URL for binary request
            urlbin = urlcsv + '&format=binary'

            # Raw CSV and HAPI Binary (no header) will be stored in .csv and
            # .bin files. Parsed response of either CSV or HAPI Binary will
            # be stored in a .npy file.
            # fnamepklx will contain additional metadata about the request
            # including d/l time, parsing time, and the location of files.
            fname_root = request2path(SERVER, DATASET, PARAMETERS, START, STOP, opts['cachedir'])
            fnamecsv = fname_root + '.csv'
            fnamebin = fname_root + '.bin'
            fnamenpy = fname_root + '.npy'
            fnamepklx = fname_root + ".pkl"

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
            meta = jsonparse(res, urljson)

        # Add information to metadata so we can figure out request needed
        # to generated it. Will also be used for labeling plots by hapiplot().
        meta.update({"x_server": SERVER})
        meta.update({"x_dataset": DATASET})

        if opts["cache"]:
            if not os.path.exists(urld): os.makedirs(urld)

        if opts['dt_chunk'] == 'infer':
            cadence = meta.get('cadence', None)

            # If cadence not given, use 1-day chunks.
            if cadence is None:
                cadence = 'PT1M'
            else:
                cadence = isodate.parse_duration(cadence)
                if isinstance(cadence, isodate.Duration):
                    # When a duration does not correspond to an unambiguous
                    # time duration (e.g., P1M), parse_duration returns an
                    # isodate.duration.Duration object. Otherwise, it returns
                    # a datetime.timedelta object.
                    cadence = cadence.totimedelta(start=datetime.now())

            pt1s = isodate.parse_duration('PT1S')
            pt1h = isodate.parse_duration('PT1H')
            p1d = isodate.parse_duration('P1D')

            if cadence < pt1s:
                opts['dt_chunk'] = 'PT1H'
            elif pt1s <= cadence <= pt1h:
                opts['dt_chunk'] = 'P1D'
            elif cadence > pt1h:
                opts['dt_chunk'] = 'P1M'
            elif cadence >= p1d:
                opts['dt_chunk'] = 'P1Y'

        if opts['n_chunks'] is not None or opts['dt_chunk'] is not None:

            padz = lambda x: x if 'Z' in x else x + 'Z'
            pSTART = hapitime2datetime(padz(START))[0]
            pSTOP  = hapitime2datetime(padz(STOP))[0]

            if opts['dt_chunk']:
                pDELTA = isodate.parse_duration(opts['dt_chunk'])

                if opts['dt_chunk'] == 'P1Y':
                    half = isodate.parse_duration('P365D') / 2
                elif opts['dt_chunk'] == 'P1M':
                    half = isodate.parse_duration('P30D') / 2
                else:
                    half = pDELTA / 2

                if (pSTOP - pSTART) < half:
                    opts['n_chunks'] = None
                    opts['dt_chunk'] = None
                    return hapi(SERVER, DATASET, PARAMETERS, START, STOP, **opts)

                if opts['dt_chunk'] == 'P1Y':
                    pSTART = datetime(pSTART.year, 1, 1)
                    pSTOP = datetime(pSTOP.year + 1, 1, 1)
                    opts['n_chunks'] = pSTOP.year - pSTART.year
                elif opts['dt_chunk'] == 'P1M':
                    pSTART = datetime(pSTART.year, pSTART.month, 1)
                    pSTOP = datetime(pSTOP.year, pSTOP.month + 1, 1)
                    opts['n_chunks'] = (pSTOP.year - pSTART.year) * 12 + (pSTOP.month - pSTART.month)
                elif opts['dt_chunk'] == 'P1D':
                    pSTART = datetime.combine(pSTART.date(), datetime.min.time())
                    pSTOP = datetime.combine(pSTOP.date(), datetime.min.time()) + timedelta(days=1)
                    opts['n_chunks'] = (pSTOP - pSTART).days
                elif opts['dt_chunk'] == 'PT1H':
                    pSTART = datetime.combine(pSTART.date(), datetime.min.time()) + timedelta(hours=pSTART.hour)
                    pSTOP = datetime.combine(pSTOP.date(), datetime.min.time()) + timedelta(hours=pSTOP.hour + 1)
                    opts['n_chunks'] = int(((pSTOP - pSTART).total_seconds() / 60) / 60)
            else:
                pDIFF = pSTOP - pSTART
                pDELTA = pDIFF / opts['n_chunks']

            n_chunks = opts['n_chunks']
            opts['n_chunks'] = None
            opts['dt_chunk'] = None

            backend = 'sequential'
            if opts['parallel']:
                backend = 'threading'
                # multiprocessing was not tested. It may work, but will
                # need a speed comparison with threading.
                # backend = 'multiprocessing'

            log('backend = {}'.format(backend), opts)

            verbose = 0
            if opts.get('logging'):
                verbose = 100

            def nhapi(SERVER, DATASET, PARAMETERS, pSTART, pDELTA, i, **opts):
                START = pSTART + (i * pDELTA)
                START = str(START.date())+'T'+str(START.time())

                STOP = pSTART + ((i + 1) * pDELTA)
                STOP = str(STOP.date()) + 'T' + str(STOP.time())

                data, meta = hapi(
                    SERVER,
                    DATASET,
                    PARAMETERS,
                    START,
                    STOP,
                    **opts
                )
                return data, meta

            resD, resM = zip(
                *Parallel(n_jobs=opts['n_parallel'], verbose=verbose, backend=backend)(
                    delayed(nhapi)(
                        SERVER,
                        DATASET,
                        PARAMETERS,
                        pSTART,
                        pDELTA,
                        i,
                        **opts
                    ) for i in range(n_chunks)
                )
            )

            resD = list(resD)

            tic_trimTime = time.time()
            if sys.version_info < (3, ):
                START = hapitime_reformat(str(resD[0]['Time'][0]), START)
                resD[0] = resD[0][resD[0]['Time'] >= START]

                STOP = hapitime_reformat(str(resD[-1]['Time'][0]), STOP)
                resD[-1] = resD[-1][resD[-1]['Time'] < STOP]
            else:
                START = hapitime_reformat(resD[0]['Time'][0].decode('UTF-8'), START)
                resD[0] = resD[0][resD[0]['Time'] >= bytes(START, 'UTF-8')]

                STOP = hapitime_reformat(resD[-1]['Time'][0].decode('UTF-8'), STOP)
                resD[-1] = resD[-1][resD[-1]['Time'] < bytes(STOP, 'UTF-8')]
            trimTime = time.time() - tic_trimTime

            tic_catTime = time.time()
            data = np.concatenate(resD)
            catTime = time.time() - tic_catTime

            meta = resM[0].copy()
            meta['x_time.max'] = resM[-1]['x_time.max']
            meta['x_dataFile'] = None
            meta['x_dataFiles'] = [resM[i]['x_dataFile'] for i in range(len(resM))]
            meta['x_downloadTime'] = sum([resM[i]['x_downloadTime'] for i in range(len(resM))])
            meta['x_downloadTimes'] = [resM[i]['x_downloadTime'] for i in range(len(resM))]
            meta['x_readTime'] = sum([resM[i]['x_readTime'] for i in range(len(resM))])
            meta['x_readTimes'] = [resM[i]['x_readTime'] for i in range(len(resM))]
            meta['x_trimTime'] = trimTime
            meta['x_catTime'] = catTime
            meta['x_totalTime'] = time.time() - tic_totalTime
            meta['x_dataFileParsed'] = None
            meta['x_dataFilesParsed'] = [resM[i]['x_dataFileParsed'] for i in range(len(resM))]

            return data, meta

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
            meta['x_totalTime'] = time.time() - tic_totalTime
            return data, meta

        cformats = ['csv', 'binary']  # client formats
        if not opts['format'] in cformats:
            # Check if requested format is implemented by this client.
            error('This client does not handle transport '
                  'format "%s".  Available options: %s'
                  % (opts['format'], ', '.join(cformats)))

        # See if server supports binary
        if opts['format'] != 'csv':
            log('Reading %s' % (SERVER + '/capabilities'), opts)
            res = urlopen(SERVER + '/capabilities')
            caps = jsonparse(res, SERVER + '/capabilities')
            sformats = caps["outputFormats"]  # Server formats
            if 'format' in kwargs and not kwargs['format'] in sformats:
                warning("hapi", 'Requested transport format "%s" not avaiable '
                                'from %s. Will use "csv". Available options: %s'
                        % (opts['format'], SERVER, ', '.join(sformats)))
                opts['format'] = 'csv'
            if not 'binary' in sformats:
                opts['format'] = 'csv'

        dt, cols, psizes, pnames, missing_length = compute_dt(meta, opts)

        # length attribute required for all parameters when serving binary but
        # is only required for time parameter when serving CSV. This catches
        # case where server provides binary but is missing a length attribute
        # in one or more string parameters that were requested. In this case,
        # there is not enough information to parse binary.
        if opts['format'] == 'binary' and missing_length:
             warnings.warn('Requesting CSV instead of binary because of problem with server metadata.')
             opts['format'] == 'csv'

        # Read the data. toc0 is time to download to file or into buffer;
        # toc is time to parse.
        if opts['format'] == 'binary':
            # HAPI Binary
            if opts["cache"]:
                log('Writing %s to %s' % (urlbin, fnamebin.replace(urld + '/', '')), opts)
                tic0 = time.time()
                urlretrieve(urlbin, fnamebin)
                toc0 = time.time() - tic0
                log('Reading and parsing %s' % fnamebin.replace(urld + '/', ''), opts)
                tic = time.time()
                data = np.fromfile(fnamebin, dtype=dt)
            else:
                from io import BytesIO
                log('Writing %s to buffer' % urlbin.replace(urld + '/', ''), opts)
                tic0 = time.time()
                buff = BytesIO(urlopen(urlbin).read())
                toc0 = time.time() - tic0
                log('Parsing BytesIO buffer.', opts)
                tic = time.time()
                data = np.frombuffer(buff.read(), dtype=dt)
        else:
            # HAPI CSV
            if opts["cache"]:
                log('Writing %s to %s' % (urlcsv, fnamecsv.replace(urld + '/', '')), opts)
                tic0 = time.time()
                urlretrieve(urlcsv, fnamecsv)
                toc0 = time.time() - tic0
                log('Reading and parsing %s' % fnamecsv.replace(urld + '/', ''), opts)
                tic = time.time()
            else:
                from io import StringIO
                log('Writing %s to buffer' % urlcsv.replace(urld + '/', ''), opts)
                tic0 = time.time()
                fnamecsv = StringIO(urlopen(urlcsv).read().decode())
                toc0 = time.time() - tic0
                log('Parsing StringIO buffer.', opts)
                tic = time.time()

            if not missing_length:
                # All string and isotime parameters have a length in metadata.
                if opts['method'] == 'numpy':
                    data = np.genfromtxt(fnamecsv, dtype=dt, delimiter=',')
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
                        data[pnames[i]] = np.squeeze(
                            np.reshape(df.values[:, np.arange(cols[i][0], cols[i][1] + 1)], shape))
            else:
                data = parse_missing_length(fnamecsv, dt, cols, psizes, pnames, opts)

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


        # Create cache directory
        # Note that this should only technically be
        # written if cache=True.
        if not os.path.exists(opts["cachedir"]):
            os.makedirs(opts["cachedir"])
        if not os.path.exists(urld):
            os.makedirs(urld)

        # Write metadata to cache
        # Note that this should only technically be
        # written if cache=True.
        log('Writing %s' % fnamepklx, opts)
        f = open(fnamepklx, 'wb')
        pickle.dump(meta, f, protocol=2)
        f.close()

        if opts["cache"]:
            log('Writing %s' % fnamenpy, opts)
            np.save(fnamenpy, data)

        meta['x_totalTime'] = time.time() - tic_totalTime

        return data, meta


def compute_dt(meta, opts):

    # Compute data type variable dt used to read HAPI response into
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
            # psizes[i] = list(reversed(psizes[i]))
            psizes[i] = list(psizes[i])

        # First column of ith parameter.
        cols[i][0] = ss
        # Last column of ith parameter.
        cols[i][1] = ss + np.prod(psizes[i]) - 1
        # Running sum of columns.
        ss = cols[i][1] + 1

        # HAPI numerical formats are 64-bit LE floating point and 32-bit LE
        # signed integers.
        if ptype == 'double':
            dtype = (pnames[i], '<d', psizes[i])
        if ptype == 'integer':
            dtype = (pnames[i], np.dtype('<i4'), psizes[i])

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

        # For testing reader. Force use of slow read method.
        if opts['format'] == 'csv':
            if opts['method'] == 'numpynolength' or opts['method'] == 'pandasnolength':
                missing_length = True
                if ptype == 'string' or ptype == 'isotime':
                    dtype = (pnames[i], object, psizes[i])

        # https://numpy.org/doc/stable/release/1.17.0-notes.html#shape-1-fields-in-dtypes-won-t-be-collapsed-to-scalars-in-a-future-version
        if dtype[2] == 1:
            dtype = dtype[0:2]

        dt.append(dtype)

    return dt, cols, psizes, pnames, missing_length


def parse_missing_length(fnamecsv, dt, cols, psizes, pnames, opts):

    # At least one requested string or isotime parameter does not
    # have a length in metadata. More work to do to read.
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
                    data[pnames[i]] = np.squeeze(
                        np.reshape(table[:, np.arange(cols[i][0], cols[i][1] + 1)], shape))
        else:
            # Table is not a 2-D numpy matrix.
            # Extract each column (don't know how to do this with slicing
            # notation, e.g., data['varname'] = table[:][1:3]). Instead,
            # loop over each parameter (pn) and aggregate columns.
            # Then insert aggregated columns into N-D array 'data'.
            for pn in range(0, len(cols)):
                shape = np.append(len(data), psizes[pn])
                for c in range(cols[pn][0], cols[pn][1] + 1):
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
        data = np.ndarray(shape=(len(df)), dtype=dt)

        # Insert data from dataframe into N-D array
        for i in range(0, len(pnames)):
            shape = np.append(len(data), psizes[i])
            # In numpy 1.8.2 and Python 2.7, this throws an error for no apparent reason.
            # Works as expected in numpy 1.10.4
            data[pnames[i]] = np.squeeze(
                np.reshape(df.values[:, np.arange(cols[i][0], cols[i][1] + 1)], shape))

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

        # https://numpy.org/doc/stable/release/1.17.0-notes.html#shape-1-fields-in-dtypes-won-t-be-collapsed-to-scalars-in-a-future-version
        if len(dtype) > 2 and dtype[2] == 1:
            dtype = dtype[0:2]
        dt2.append(dtype)

    # Create new N-D array that won't have any parameters with
    # type = 'O'.
    data2 = np.ndarray(data.shape, dt2)

    for i in range(0, len(pnames)):
        if data[pnames[i]].dtype == 'O':
            data2[pnames[i]] = data[pnames[i]].astype(dt2[i][1])
        else:
            data2[pnames[i]] = data[pnames[i]]
            # Save memory by not copying (does this help?)
            # data2[pnames[i]] = np.array(data[pnames[i]],copy=False)

    return data2