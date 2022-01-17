import os
import isodate

from datetime import datetime
from hapiclient import hapi
from hapiclient.hapitime import hapitime2datetime, hapitime_reformat
from hapiclient.test.compare import equal

# See comments in test_hapitime2datetime.py for execution options.

compare_logging = True
hapi_logging = False

logfile = os.path.realpath(__file__)[0:-2] + "log"
with open(logfile, "w") as f:
    # Create empty file
    pass

def xprint(msg):
    print(msg)
    f = open(logfile, "a")
    f.write(msg + "\n")
    f.close()


def compare(data1, data2, meta1, meta2, opts1, opts2):
    if compare_logging:
        xprint('_'*80)
        xprint('request  : %s, %s, %s, %s, %s' % \
                (meta1['x_dataset'], meta1['x_parameters'], meta1['x_time.min'], meta1['x_time.max'], meta1['cadence']))
        xprint('options 1: %s' % opts1)
        xprint('options 2: %s' % opts2)
        xprint('x_totalTime1 = %6.4f s' % (meta1['x_totalTime']))
        xprint('x_totalTime2 = %6.4f s' % (meta2['x_totalTime']))
        if False and 'x_downloadTimes' in meta2:
            print(meta1['x_downloadTime'])
            print(meta1['x_readTime'])
            print(meta2['x_downloadTimes'])
            print(meta2['x_readTimes'])
            print(meta2['x_trimTime'])
            print(meta2['x_catTime'])
    
    assert equal(data1, data2)


def cat(d1, d2):
    # Python 2-compatable dict concatenation.
    # https://treyhunner.com/2016/02/how-to-merge-dictionaries-in-python/
    d12 = d1.copy()
    d12.update(d2)
    return d12


opts0 = {'logging': hapi_logging, 'usecache': False, 'cache': False}

# Test dict.
# Key indicates chunk size to use for chunk test
td = {
        "P1Y": {
                "__comment": "dataset3 has cadence of P1D",
                "server": "http://hapi-server.org/servers-dev/TestData2.0/hapi",
                "dataset": "dataset3",
                "parameters": "scalar",
                "start": "1971-01-01T01:50:00Z",
                "stop": "1975-08-03T06:50:00Z"
        },
        "P1M": {
                "__comment": "dataset3 has cadence of P1D",
                "server": "http://hapi-server.org/servers-dev/TestData2.0/hapi",
                "dataset": "dataset3",
                "parameters": "scalar",
                "start": "1971-01-01T01:50:00Z",
                "stop": "1971-08-03T06:50:00Z"
        },
        "P1D":
            {
                "__comment": "dataset2 has cadence of P1H",
                "server": "http://hapi-server.org/servers-dev/TestData2.0/hapi",
                "dataset": "dataset2",
                "parameters": "scalar",
                "start": "1970-01-01T00:00:00.000Z",
                "stop": "1970-01-10T00:00:00.000Z"
        },
        "PT1H": {
                "__comment": "dataset1 has cadence of PT1S",
                "server": "http://hapi-server.org/servers-dev/TestData2.0/hapi",
                "dataset": "dataset1",
                "parameters": "scalar",
                "start": "1970-01-01T00:00:00.000Z",
                "stop": "1970-01-01T05:00:00.000Z"
        }
}


def test_chunks():

    # Test of dt_chunk and n_chunks keyword arguments
    for key in td:

        s = td[key]['server']
        d = td[key]['dataset']
        p = td[key]['parameters']

        if '-dev' in s:
            import warnings
            warnings.warn("Change server from dev to production for these tests")


        # Reference result. No splitting will be performed.
        opts1 = cat(opts0, {'dt_chunk': None})
        data1, meta1 = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts1)

        opts = opts0
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        compare(data1, data, meta1, meta, opts1, opts)

        opts = cat(opts0, {'n_chunks': 2})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        compare(data1, data, meta1, meta, opts1, opts)

        opts = cat(opts0, {'dt_chunk': key})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        compare(data1, data, meta1, meta, opts1, opts)

        opts = cat(opts0, {'parallel': True, 'n_chunks': 2})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        compare(data1, data, meta1, meta, opts1, opts)

        opts = cat(opts0, {'parallel': True, 'dt_chunk': key})
        data, meta = hapi(s, d, p, td[key]['start'], td[key]['stop'], **opts)
        compare(data1, data, meta1, meta, opts1, opts)


def test_chunk_threshold():

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
    opts1 = cat(opts0, {'dt_chunk': None})
    data1, meta1 = hapi(s, d, p, start, stop, **opts1)

    opts = cat(opts0, {'dt_chunk': 'infer'})
    data, meta = hapi(s, d, p, start, stop, **opts)
    
    compare(data1, data, meta1, meta, opts1, opts)


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
    compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%m-%d, data: %Y-%m-%d
    data, meta = hapi(s, d, p, start_doy, stop_ymd, **opts)
    compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%j, data: %Y-%m-%d
    data, meta = hapi(s, d, p, start_doy, stop_doy, **opts)
    compare(data1, data, meta1, meta, opts1, opts)

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
    compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%m-%d, data: %Y-%j
    data, meta = hapi(s, d, p, start_doy, stop_ymd, **opts)
    compare(data1, data, meta1, meta, opts1, opts)

    # start: %Y-%j, stop: %Y-%j, data: %Y-%j
    data, meta = hapi(s, d, p, start_doy, stop_doy, **opts)
    compare(data1, data, meta1, meta, opts1, opts)


if __name__ == '__main__':
    test_chunks()
    test_chunk_threshold()
    test_timeformats()
