from hapiclient.log import log, configure_logging
from hapiclient.util import setopts, error
from hapiclient.cache import cachedir
from hapiclient.servers import servers
from hapiclient.catalog import catalog
from hapiclient.info import info
from hapiclient.data import data

# Backward compatibility: older code imports request2path from hapiclient.hapi
from hapiclient.cache import request2path # Do not remove.



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
        'format': 'binary',
        'method': '',
        'parallel': False,
        'n_parallel': 5,
        'n_chunks': None,
        'dt_chunk': None,
    }

    return opts


def hapi(*args, **kwargs):
    """Request data from a HAPI server.

    Version: 0.3.0


    Examples
    ----------
    `Jupyter Notebook <https://colab.research.google.com/drive/11Zy99koiE90JKJ4u_KPTaEBMQFzbfU3P?usp=sharing>`_

    Parameters
    ----------
    server: str
        A string with the URL to a HAPI compliant server. (A HAPI URL \
        always ends with ``/hapi``).
    dataset: str
        A string specifying a dataset from a `server`
    parameters: str
        A comma-separated list of parameters in `dataset`
    start: str
        The start time of the requested data
    stop: str or None
        The end time of the requested data; end times are exclusive - the
        last data record returned by a HAPI server should have a timestamp
        before `stop`. If `None`, `stopDate` is used.
    options: dict
            `logging` (``False``) - If ``True``, add a stdout handler to the Python ``logging`` module and set log level to INFO. If the Python ``logging`` module has already been configured for the ``hapiclient`` logger (external handlers or log level set), the ``logging`` kwarg is ignored.

            `cache` (``True``) - Save responses and processed responses in cachedir

            `cachedir` (``'./hapi-data'``)

            `usecache` (``True``) - Use files in `cachedir` if found

            `serverlist` (``'https://github.com/hapi-server/servers/raw/master/all.txt'``)

            `format` (``'binary'``) ``'binary'`` or ``'csv'``; ``'csv``' will force the use of ``format=csv`` in request to server.

            `parallel` (``False``) If ``True``, make up to `n_parallel` requests to server \
                in parallel (uses threads)

            `n_parallel` (``5``) Maximum number of parallel requests to server.\
                Max allowed is 5.

            `n_chunks` (``None``) Get data by making `n_chunks` requests by splitting \
                requested time range. `dt_chunk` is ignored if `n_chunks` is \
                not `None`. Allowed values are integers > 1.

            `dt_chunk` (``'infer'``) For requests that span a time range larger \
                than the default chunk size for a given dataset cadence, the \
                client will split request into chunks if `dt_chunk` is not \
                `None`.

                Allowed values of `dt_chunk` are 'infer', `None`, and an ISO 8601 \
                duration that is unambiguous (durations that include Y and M are not \
                allowed). The default chunk size is determined based on the cadence \
                of the dataset requested according to

                    * cadence < PT1S              dt_chunk='PT1H'
                    * PT1S <= cadence <= PT1H     dt_chunk='P1D'
                    * cadence > PT1H              dt_chunk='P30D'
                    * cadence >= P1D              dt_chunk='P365D'

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

                        1. start/stop=1999-11-12/start=1999-11-13
                        2. start/stop=1999-11-13/start=1999-11-14

                        and trim performed


    Returns
    -------
    result: varies
        `result` depends on the input parameters.

        ``servers = hapi()`` returns a list of available HAPI server URLs from
        https://github.com/hapi-server/data-specification/blob/master/all.txt

        ``dataset = hapi(server)`` returns a dict of datasets available from a
        URL given by the string `server`.  The dictionary structure follows the
        `HAPI catalog response JSON structure <https://github.com/hapi-server/data-specification/blob/master/hapi-dev/HAPI-data-access-spec-dev.md#35-catalog>`_.

        ``parameters = hapi(server, dataset)`` returns a dict containing the HAPI info metadata for all parameters
        in the string `dataset`. The dictionary structure follows the 
        `HAPI info response JSON structure <https://github.com/hapi-server/data-specification/blob/master/hapi-dev/HAPI-data-access-spec-dev.md#36-info>`_.

        ``meta = hapi(server, dataset, parameters)`` returns a dict containing the  HAPI info metadata
        for each parameter in the comma-separated string ``parameters``. The
        dictionary structure follows 
        `HAPI info response JSON structure <https://github.com/hapi-server/data-specification/blob/master/hapi-dev/HAPI-data-access-spec-dev.md#36-info>`_.

        ``data, = hapi(server, dataset, parameters, start, stop)`` returns a
        NumPy array with named fields with field names corresponding to ``parameters``, e.g., if
        ``parameters = 'scalar,vector'`` and the number of records in the time
        range ``start`` <= t < ``stop`` returned is N, then

          ``data['scalar']`` is a NumPy array of shape (N)

          ``data['vector']`` is a NumPy array of shape (N,3)

          ``data['Time']`` is a NumPy array of byte literals with shape (N).

          Byte literal times can be converted to Python ``datetimes`` using

          ``dtarray = hapitime2datetime(data['Time'])``

        ``data, meta = hapi(server, dataset, parameters, start, stop)`` returns
        the HAPI info metadata for parameters in `meta` (and should contain the
        same content as ``meta = hapi(server, dataset, parameters)``).


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
        if STOP is not None and STOP[-1] != 'Z':
            # TODO: Consider warning.
            STOP = STOP + 'Z'


    if 'logging' in kwargs and not isinstance(kwargs['logging'], bool):
        raise ValueError("logging keyword must be True or False")

    configure_logging(kwargs.get('logging', None))

    # Override defaults
    opts = setopts(hapiopts(), kwargs)

    assert (opts['cache'] in [True, False]), "cache keyword must be True of False"
    assert (opts['usecache'] in [True, False]), "usecache keyword must be True of False"
    assert (opts['format'] in ['binary', 'csv']), "format keyword must be 'csv' or 'binary'"
    assert (opts['method'] in ['', 'pandas', 'numpy', 'pandasnolength', 'numpynolength'])
    assert (opts['parallel'] in [True, False]), 'parallel keyword must be True or False'
    assert (isinstance(opts['n_parallel'], int) and opts['n_parallel'] > 1)
    assert (opts['n_chunks'] is None or isinstance(opts['n_chunks'], int) and opts['n_chunks'] > 0)
    assert (opts['dt_chunk'] in [None, 'infer', 'PT1H', 'P1D', 'P1M', 'P1Y'])

    from hapiclient import __version__
    log('Running hapi.py version %s' % __version__)

    if nin == 4:
        error('A stop time is required if a start time is given.')

    # hapi()
    if nin == 0:
        return servers()

    # hapi(SERVER)
    if nin == 1:
        return catalog(SERVER)

    # hapi(SERVER, DATASET)
    if nin == 2:
        return info(SERVER, DATASET, None, opts)

    # hapi(SERVER, DATASET, PARAMETERS)
    if nin == 3:
        return info(SERVER, DATASET, PARAMETERS, opts)

    # hapi(SERVER, DATASET, PARAMETERS, START, STOP)
    if nin == 5:
        return data(SERVER, DATASET, PARAMETERS, START, STOP, opts)

