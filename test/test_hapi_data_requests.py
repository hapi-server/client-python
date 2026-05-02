# See ../README.md for instructions on running tests.
import pytest
import shutil

from hapiclient.hapi import hapi

from util import compare

from util.get_logger import get_logger
logger = get_logger(__name__)

kwargs = {
    'cache': False,
    'usecache': False,
    'cachedir': '/tmp/hapi-data',
    'logging': False
}

serverbad = 'http://hapi-server.org/servers/TestData/xhapi'
server = 'http://hapi-server.org/servers/TestData2.0/hapi'


def _reader_run(run):

    def rmcache(cacheopt):
         shutil.rmtree(kwargs['cachedir'], ignore_errors=True)

    dataset = 'dataset1'

    opts = kwargs.copy()

    cacheopts = [
        {'cache': False, 'usecache': False},
        {'cache': True, 'usecache': False},
        {'cache': False, 'usecache': True}
    ]

    for cacheopt in cacheopts:
        opts.update(cacheopt)

        # Read one parameter
        if not cacheopt['usecache']:
            rmcache(cacheopt)
        assert compare.read(server, dataset, 'scalar', run, opts, logger=logger)


def test_reader_timing_short():
    logger.info("test_reader_timing_short()")
    _reader_run('short')


@pytest.mark.long
def test_reader_timing_long():
    logger.info("test_reader_timing_long()")
    _reader_run('long')


def test_all_test_servers():

    # Test that all test servers can be accessed and return something for a
    # request for all parameters for the sample time range.
    def test_server(version):
        from hapiclient import hapi
        from hapiclient.util import warning, unicode_error_message

        server  = 'http://hapi-server.org/servers/TestData{}/hapi'.format(version)
        dataset = 'dataset1'
        start   = '1970-01-01T00:00:00'
        stop    = '1970-01-01T00:01:00'

        # Get catalog with list of datasets
        catalog = hapi(server)
        for dataset in catalog['catalog']:

            if unicode_error_message(dataset['id']) != "":
                logger.warning("Skipping "+ str(dataset['id'].encode('utf-8')) + " due to " + unicode_error_message(dataset))
                continue

            id = dataset['id']
            # Get metadata for dataset to determine sampleStartDate and sampleStopDate
            info = hapi(server, id)

            # Use sampleStartDate and sampleStopDate from metadata if available.
            sampleStartDate = info.get('sampleStartDate', start)
            sampleStopDate = info.get('sampleStopDate', stop)

            # Request all parameters for dataset over time range
            data, meta = hapi(server, id, '', sampleStartDate, sampleStopDate, **kwargs)

    # TODO: Get list of test servers from
    #  https://hapi-server.org/meta/abouts-test.json

    for version in ['2.0', '2.1', '3.0', '3.1', '3.2', '3.3']:
        try:
            test_server(version)
        except Exception as e:
            pytest.fail("test_server('%s') raised: %s" % (version, e))


def test_cache_short():

    # Compare read with empty cache with read with hot cache and usecache=True
    dataset = 'dataset1'
    start = '1970-01-01'
    stop  = '1970-01-01T00:00:03'

    opts = {**kwargs, 'cache': True}

    opts['usecache'] = False
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    opts['usecache'] = True
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    assert compare.equal(data, data2)


def test_subset_short():

    dataset = 'dataset1'
    start = '1970-01-01'
    stop  = '1970-01-01T00:00:03'
    opts = {**kwargs, 'cache': True}

    opts['usecache'] = False

    # Request two subsets with empty cache. Common parts should be same.
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, 'scalarint', start, stop, **opts)

    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    ok = compare.equal(data, data2, names=['Time'])
    ok = ok and compare.equal(data, data2, names=['scalarint'])
    assert ok

    # Request all parameters and single parameter. Common parameter should be same.
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, '', start, stop, **opts)

    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data2, meta2  = hapi(server, dataset, 'vectorint', start, stop, **opts)

    ok = compare.equal(data, data2, names=['Time'])
    ok = ok and compare.equal(data, data2, names=['vectorint'])
    assert ok


    opts['usecache'] = True

    # Request two subsets, with the second request using the cache. Common
    # parts should be same.
    data, meta  = hapi(server, dataset, 'scalarint', start, stop, **opts)
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    ok = compare.equal(data, data2, names=['Time'])
    ok = ok and compare.equal(data, data2, names=['scalarint'])
    assert ok

    # Request all parameters and single parameter, with the single parameter
    # request using the cache with hot cache. Common parameter should be same.
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, '', start, stop, **opts)
    data2, meta2  = hapi(server, dataset, 'vectorint', start, stop, **opts)

    ok = compare.equal(data, data2, names=['Time'])
    ok = ok and compare.equal(data, data2, names=['vectorint'])
    assert ok


def test_request2path():

    from hapiclient.hapi import request2path

    import platform
    if platform.system() == 'Windows':
        p = request2path('http://server/dir1/dir2','xx','abc<>:"/|?*.','2000-01-01T00:00:00.Z','2000-01-01T00:00:00.Z','')
        assert p == 'server_dir1_dir2\\xx_abc@lt@@gt@@colon@@doublequote@@forwardslash@@pipe@@questionmark@@asterisk@._20000101T000000_20000101T000000'
    else:
        p = request2path('http://server/dir1/dir2','xx/yy','abc/123','2000-01-01T00:00:00.Z','2000-01-01T00:00:00.Z','')
        assert p == 'server_dir1_dir2/xx@forwardslash@yy_abc@forwardslash@123_20000101T000000_20000101T000000'


def test_unicode():

    from hapiclient.util import warning, unicode_error_message

    logger.info("test_unicode()")
    server   = 'http://hapi-server.org/servers/TestData3.1/hapi'
    datasets = ["dataset1-Aα☃"]

    run = 'short'

    opts = kwargs.copy()

    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    for dataset in datasets:
        if unicode_error_message(dataset) != "":
            warning("Skipping "+ str(dataset.encode('utf-8')) + " due to " + unicode_error_message(dataset))
            continue
        meta = hapi(server, dataset)
        for p in meta['parameters']:

            # Read one parameter
            parameter = p['name']
            if unicode_error_message(parameter) != "":
                warning("Skipping "+ str(parameter.encode('utf-8')) + " due to " + unicode_error_message(parameter))
                continue

            assert compare.read(server, dataset, parameter, run, opts.copy(), logger=logger)
            assert compare.cache(server, dataset, parameter, opts.copy(), logger=logger)


if __name__ == '__main__':
    test_subset_short()
    test_reader_timing_short()
    test_reader_timing_long()
    test_all_test_servers()
    test_subset_short()
    test_cache_short()
    test_request2path()
    test_unicode()
