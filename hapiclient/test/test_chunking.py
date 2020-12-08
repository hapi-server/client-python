import isodate
from datetime import datetime
from hapiclient import hapi, hapitime2datetime
from hapiclient.hapi import hapitime_reformat
from hapiclient.test.readcompare import equal

compare_logging = True
hapi_logging = False

def compare(data1, data2, meta1, meta2, opts1, opts2):
    if compare_logging:
        print('_'*80)
        print('options 1: %s' % opts1)
        print('options 2: %s' % opts2)
        print('x_totalTime1 = %6.4f s' % (meta1['x_totalTime']))
        print('x_totalTime2 = %6.4f s' % (meta2['x_totalTime']))
    assert equal(data1, data2)


def cat(d1, d2):
    # Python 2-compatable dict concatenation.
    # https://treyhunner.com/2016/02/how-to-merge-dictionaries-in-python/
    d12 = d1.copy()
    d12.update(d2)
    return d12


opts0 = {'logging': hapi_logging, 'usecache': False, 'cache': False}

# Test dict.
td = {
        "P1Y":
            {
                "start": "1970-01-02T01:50:00Z",
                "stop": "1970-08-03T06:50:00Z"
        },
        "P1M": {
                "start": "1971-06-02T01:50:00Z",
                "stop": "1974-08-03T06:50:00Z"
        },
        "P1D": {
                "server": 'http://hapi-server.org/servers/SSCWeb/hapi',
                "dataset": 'ace',
                "parameters": 'X_GSM',
                "start": "2000-01-01T00:00:00.000Z",
                "stop": "2000-01-10T00:00:00.000Z"
        },
        "PT1H": {
                "server": "http://hapi-server.org/servers/TestData2.0/hapi",
                "dataset": "dataset1",
                "parameters": "scalar",
                "start": "1970-01-01T00:00:00.000Z",
                "stop": "1970-01-01T05:00:00.000Z"
        }
}


def test_chunks():

    # Test of dt_chunk and n_chunks keyword arguments
    for key in td:

        if key != 'PT1H':# and key != 'P1D':
            # Only regularly test 1-hour for now.
            # TODO: Update when lower cadence TestData datasets are available.
            continue

        if compare_logging:
            print('server:     ', td[key]['server'])
            print('dataset:    ', td[key]['dataset'])
            print('parameters: ', td[key]['parameters'])
            print('start:      ', td[key]['start'])
            print('stop:       ', td[key]['stop'])

        s = td[key]['server']
        d = td[key]['dataset']
        p = td[key]['parameters']

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
    #print(stop)
    #import pdb;pdb.set_trace()
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

    s = td[key]['server']
    d = td[key]['dataset']
    p = td[key]['parameters']

    start_ymd = td[key]['start']
    start_doy = hapitime_reformat('1989-272T00:00:00.000Z',start_ymd)

    stop_ymd = td[key]['stop']
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
