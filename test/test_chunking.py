import logging
import isodate

from datetime import datetime

from hapiclient import hapi
from hapiclient.hapitime import hapitime2datetime, hapitime_reformat
from util.compare import equal

from util.get_logger import get_logger

logger = get_logger(__name__)

hapi_logging = False
if logging.getLevelName(logger.level) == 'DEBUG':
    hapi_logging = True

#server = "http://hapi-server.org/servers-dev/TestData2.0/hapi"
server = "http://hapi-server.org/servers/TestData2.0/hapi"


def _compare(data1, data2, meta1, meta2, opts1, opts2):
    logger.info('  request:   %s, %s, %s, %s, %s' % \
            (meta1['x_dataset'], meta1['x_parameters'], meta1['x_time.min'], meta1['x_time.max'], meta1['cadence']))
    logger.info('  options 1: %s' % opts1)
    logger.info('  options 2: %s' % opts2)
    logger.info('  x_totalTime1 = %6.4f s' % (meta1['x_totalTime']))
    logger.debug(f'    x_downloadTime1 = {meta1["x_downloadTime"]}')
    logger.debug(f'    x_readTime1 = {meta1["x_readTime"]}')

    logger.info('  x_totalTime2 = %6.4f s' % (meta2['x_totalTime']))
    logger.debug(f'    x_downloadTimes2 = {meta2["x_downloadTimes"]}')
    logger.debug(f'    x_readTimes2 = {meta2["x_readTimes"]}')
    logger.debug(f'    x_trimTime2 = {meta2["x_trimTime"]}')
    logger.debug(f'    x_catTime2 = {meta2["x_catTime"]}')

    logger.info('')
    assert equal(data1, data2)


def _cat(d1, d2):
    # Python 2-compatable dict concatenation.
    # https://treyhunner.com/2016/02/how-to-merge-dictionaries-in-python/
    d12 = d1.copy()
    d12.update(d2)
    return d12


opts0 = {
    'logging': hapi_logging,
    'usecache': False,
    'cache': False,
    'format': 'csv'
}

# Test dict.
# Key is chunk size to use for certain tests.
td = {
        "P1Y": {
                "__comment": "dataset3 has cadence of P1D",
                "server": server,
                "dataset": "dataset3",
                "parameters": "scalar",
                "start": "1971-01-01T01:50:00Z",
                "stop": "1975-08-03T06:50:00Z"
        },
        "P1M": {
                "__comment": "dataset3 has cadence of P1D",
                "server": server,
                "dataset": "dataset3",
                "parameters": "scalar",
                "start": "1971-01-01T01:50:00Z",
                "stop": "1971-08-03T06:50:00Z"
        },
        "P1D":
            {
                "__comment": "dataset2 has cadence of P1H",
                "server": server,
                "dataset": "dataset2",
                "parameters": "scalar",
                "start": "1970-01-01T00:00:00.000Z",
                "stop": "1970-01-10T00:00:00.000Z"
        },
        "PT1H": {
                "__comment": "dataset1 has cadence of PT1S",
                "server": server,
                "dataset": "dataset1",
                "parameters": "scalar",
                "start": "1970-01-01T00:00:00.000Z",
                "stop": "1970-01-01T05:00:00.000Z"
        }
}


def test_chunks():

    logger.info("test_chunks()")
    # Test of dt_chunk and n_chunks keyword arguments
    for key in td:
        s = td[key]['server']
        d = td[key]['dataset']
        p = td[key]['parameters']

        if '-dev' in s:
            import warnings
            warnings.warn("Change server from dev to production for these tests")

        # Reference result. No chunking.
        opts1 = _cat(opts0, {'dt_chunk': None})
        data1, meta1 = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts1)

        # Default chunking.
        opts = opts0
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        _compare(data1, data, meta1, meta, opts1, opts)

        opts = _cat(opts0, {'n_chunks': 2})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        _compare(data1, data, meta1, meta, opts1, opts)

        opts = _cat(opts0, {'dt_chunk': key})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        _compare(data1, data, meta1, meta, opts1, opts)


def test_parallel():

    logger.info("test_parallel()")

    # Note that parallel option does not often lead to speedup. Parallel option
    # needs work.
    for key in td:
        s = td[key]['server']
        d = td[key]['dataset']
        p = td[key]['parameters']

        # Reference result. No chunking.
        opts1 = _cat(opts0, {'dt_chunk': None})
        data1, meta1 = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts1)

        opts = _cat(opts0, {'parallel': True, 'n_chunks': 2})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        _compare(data1, data, meta1, meta, opts1, opts)

        opts = _cat(opts0, {'parallel': True, 'dt_chunk': key})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        _compare(data1, data, meta1, meta, opts1, opts)


def test_chunk_threshold():

    logger.info("test_chunk_threshold()")

    # Test case when time span is less than minimum threshold for automatic
    # chunking. Code executed should be the same in both cases. This test does
    # not check that same code was executed, however.

    key = 'PT1H'
    chunk = 'P1D'

    s = td[key]['server']
    d = td[key]['dataset']
    p = td[key]['parameters']

    # Default chunk size for 1-second data is P1D. No chunking performed if
    # stop-start < PT1D/2.
    start = td[key]['start']
    stop = hapitime2datetime(start) + isodate.parse_duration(chunk)/3
    stop = datetime.isoformat(stop[0])[0:19] + "Z"

    # Reference result
    opts1 = _cat(opts0, {'dt_chunk': None})
    data1, meta1 = hapi(s, d, p, start, stop, **opts1)

    opts = _cat(opts0, {'dt_chunk': 'infer'})
    data, meta = hapi(s, d, p, start, stop, **opts)

    _compare(data1, data, meta1, meta, opts1, opts)


def test_timeformats():

    # Data are efficiently subsetted using a NumPy operation of the form
    # data['Time'][ data['Time'] >= bytes('2000-01-01T00', 'UTF-8')]
    # Internally, the start and stop strings must be converted to 
    # the ISO 8601 format of the data.

    # The following tests the possible combinations of start, stop, and
    # data time formats.

    key = "PT1H"

    s = td[key]['server']
    d = td[key]['dataset']
    p = td[key]['parameters']

    start_ymd = td[key]['start']
    start_doy = hapitime_reformat('1989-272T00:00:00.000Z',start_ymd)

    stop_ymd = td[key]['stop']
    stop_doy = hapitime_reformat('1989-272T00:00:00.000Z',stop_ymd)

    # Reference result.
    # start: %Y-%m-%d, stop: %Y-%m-%d, data: %Y-%m-%d
    opts1 = {'usecache': False, 'cache': False, 'dt_chunk': None}
    data1, meta1 = hapi(s, d, p, start_ymd, stop_ymd, **opts1)

    opts = {'usecache': False, 'cache': False, 'dt_chunk': 'infer'}

    # start: %Y-%m-%d, stop: %Y-%j, data: %Y-%m-%d
    data, meta = hapi(s, d, p, start_ymd, stop_doy, **opts)
    _compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%m-%d, data: %Y-%m-%d
    data, meta = hapi(s, d, p, start_doy, stop_ymd, **opts)
    _compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%j, data: %Y-%m-%d
    data, meta = hapi(s, d, p, start_doy, stop_doy, **opts)
    _compare(data1, data, meta1, meta, opts1, opts)

    ############################################################################
    # Switch to use a server that serves data in %Y-%j format. Change to
    # TestData server when it has a data set served in %Y-%j format.
    ############################################################################

    key = "P1D"
    tdx = {
            "P1D": {
                    "__comment": "Timeformat is YYYY-DOY",
                    "server": 'http://hapi-server.org/servers/SSCWeb/hapi',
                    "dataset": 'ace',
                    "parameters": 'X_GSM',
                    "start": "2000-01-01T00:00:00.000Z",
                    "stop": "2000-01-02T00:00:00.000Z"
            }
    }

    s = tdx[key]['server']
    d = tdx[key]['dataset']
    p = tdx[key]['parameters']

    start_ymd = tdx[key]['start']
    start_doy = hapitime_reformat('1989-272T00:00:00.000Z',start_ymd)

    stop_ymd = tdx[key]['stop']
    stop_doy = hapitime_reformat('1989-272T00:00:00.000Z',stop_ymd)

    # Reference result
    # start: %Y-%m-%d, stop: %Y-%m-%d, data: %Y-%j
    data1, meta1 = hapi(s, d, p, start_ymd, stop_ymd, **opts1)

    # start: %Y-%m-%d, stop: %Y-%j, data: %Y-%j
    data, meta = hapi(s, d, p, start_ymd, stop_doy, **opts)
    _compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%m-%d, data: %Y-%j
    data, meta = hapi(s, d, p, start_doy, stop_ymd, **opts)
    _compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%j, data: %Y-%j
    data, meta = hapi(s, d, p, start_doy, stop_doy, **opts)
    _compare(data1, data, meta1, meta, opts1, opts)


if __name__ == '__main__':
    test_chunks()
    test_parallel()
    test_chunk_threshold()
    test_timeformats()
