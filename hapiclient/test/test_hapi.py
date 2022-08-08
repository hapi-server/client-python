# -*- coding: utf-8 -*-
# Above line can be removed when Python 2.7 support is dropped.
import os
import pytest
import pickle
import shutil

import numpy as np

from deepdiff import DeepDiff
from hapiclient.hapi import hapi
from hapiclient.test import compare

# To run tests on a specific function, edit the function calls in the
# if __name__ == '__main__' block and then execute 
#
#    python test_hapi.py
#
# See comments in test_hapitime2datetime.py for other execution options.

logging = False
serverbad = 'http://hapi-server.org/servers/TestData/xhapi'
server = 'http://hapi-server.org/servers/TestData2.0/hapi'

def writepickle(fname, var):
    print("!!!!!!!!!!!!!!")
    print("Writing " + fname)
    print("!!!!!!!!!!!!!!")
    with open(fname, 'wb') as pickle_file:
        pickle.dump(var, pickle_file, protocol=2)
    pickle_file.close()


def readpickle(fname):
    with open(fname, 'rb') as pickle_file:
        var = pickle.load(pickle_file)
    pickle_file.close()
    return var


@pytest.mark.short
def test_hapi():
    """Test that a call with no parameters returns something."""
    assert hapi() is not None


@pytest.mark.short
def test_server_list():
    """Test that specifying a server returns something."""
    assert hapi(server) is not None


@pytest.mark.short
def test_catalog():
    """Request for catalog returns correct status and first dataset"""
    meta = hapi(server)
    assert meta['status'] == {'code': 1200, 'message': 'OK'} and meta['catalog'][0]['id'] == 'dataset1'


@pytest.mark.short
def test_dataset():
    """Request for dataset returns correct dataset metadata"""
    meta = hapi(server,'dataset1')
    pklFile = 'test_dataset.pkl'
    pklFile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data',pklFile)
    if not os.path.isfile(pklFile):
        writepickle(pklFile, meta)
        assert True
        return
    else:
        metatest = readpickle(pklFile)
    assert DeepDiff(meta,metatest) == {}


@pytest.mark.short
def test_parameter():
    """Request for dataset returns correct parameter metadata"""
    meta = hapi(server,'dataset1')
    pklFile = 'test_parameter.pkl'
    pklFile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data',pklFile)
    if not os.path.isfile(pklFile):
        writepickle(pklFile,meta)
        assert True
        return
    else:
        metatest = readpickle(pklFile)
    assert DeepDiff(meta,metatest) == {}
 

@pytest.mark.short
def test_bad_server_url():
    """Correct error when given bad URL"""
    with pytest.raises(Exception):
        hapi(serverbad, {'logging': logging})


@pytest.mark.short
def test_bad_dataset_name():
    """Correct error when given nonexistent dataset name"""
    with pytest.raises(Exception):
        hapi(server,'dataset1x')


@pytest.mark.short
def test_bad_parameter():
    """Correct error when given nonexistent parameter name"""
    with pytest.raises(Exception):
        hapi(server,'dataset1','scalarx')


@pytest.mark.short
def test_reader_short():
        
    dataset = 'dataset1'
    run = 'short'
    
    opts = {'logging': logging, 'cachedir': '/tmp/hapi-data', 'usecache': False}

    opts['cache'] = False

    # Read one parameter
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    assert compare.read(server, dataset, 'scalar', run, opts)

    # Read two parameters
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    assert compare.read(server, dataset, 'scalar,vector', run, opts)

    # Read all parameters
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    assert compare.read(server, dataset, '', run, opts)

    # Cache = True (will write files then read)
    opts['cache'] = True

    # Read one parameter
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    assert compare.read(server, dataset, 'scalar', run, opts)

    # Read two parameters
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    assert compare.read(server, dataset, 'scalar,vector', run, opts)
    shutil.rmtree(opts['cachedir'], ignore_errors=True)

    # Read all parameters
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    assert compare.read(server, dataset, '', run, opts)


@pytest.mark.short
def test_cache_short():

    # Compare read with empty cache with read with hot cache and usecache=True
    dataset = 'dataset1'
    start = '1970-01-01'
    stop  = '1970-01-01T00:00:03'

    opts = {'logging': logging, 'cachedir': '/tmp/hapi-data', 'cache': True}

    opts['usecache'] = False
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    opts['usecache'] = True
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    assert np.array_equal(data, data2)


@pytest.mark.short
def test_subset_short():
    
    dataset = 'dataset1'
    start = '1970-01-01'
    stop  = '1970-01-01T00:00:03'
    opts = {'logging': logging, 'cachedir': '/tmp/hapi-data', 'cache': True}

    opts['usecache'] = False
    
    # Request two subsets with empty cache. Common parts should be same.
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, 'scalarint', start, stop, **opts)

    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['scalarint'], data2['scalarint'])
    assert ok

    # Request all parameters and single parameter. Common parameter should be same.
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, '', start, stop, **opts)

    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data2, meta2  = hapi(server, dataset, 'vectorint', start, stop, **opts)
        
    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['vectorint'], data2['vectorint'])
    assert ok


    opts['usecache'] = True
    
    # Request two subsets, with the second request using the cache. Common
    # parts should be same.
    data, meta  = hapi(server, dataset, 'scalarint', start, stop, **opts)
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['scalarint'], data2['scalarint'])
    assert ok

    # Request all parameters and single parameter, with the single parameter
    # request using the cache with hot cache. Common parameter should be same.
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, meta  = hapi(server, dataset, '', start, stop, **opts)
    data2, meta2  = hapi(server, dataset, 'vectorint', start, stop, **opts)
        
    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['vectorint'], data2['vectorint'])
    assert ok

@pytest.mark.short
def test_request2path():

    from hapiclient.hapi import request2path;

    import platform
    if platform.system() == 'Windows':
        p = request2path('http://server/dir1/dir2','xx','abc<>:"/|?*.','2000-01-01T00:00:00.Z','2000-01-01T00:00:00.Z','')
        assert p == 'server_dir1_dir2\\xx_abc@lt@@gt@@colon@@doublequote@@forwardslash@@pipe@@questionmark@@asterisk@._20000101T000000_20000101T000000'
    else:
        p = request2path('http://server/dir1/dir2','xx/yy','abc/123','2000-01-01T00:00:00.Z','2000-01-01T00:00:00.Z','')
        assert p == 'server_dir1_dir2/xx@forwardslash@yy_abc@forwardslash@123_20000101T000000_20000101T000000'


@pytest.mark.short
def test_unicode():

    from hapiclient.util import warning, unicode_error_message

    server     = 'http://hapi-server.org/servers/TestData3.1/hapi';
    #datasets   = ["dataset1", "dataset1-Zα☃"]
    datasets   = ["dataset1-Zα☃"]
    #datasets = ["dataset1"]

    run = 'short'

    opts = {
                'logging': True,
                'cachedir': '/tmp/hapi-data',
                'usecache': False,
                'cache': False
            }


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

            assert compare.read(server, dataset, parameter, run, opts.copy())
            assert compare.cache(server, dataset, parameter, opts.copy())


@pytest.mark.long
def test_reader_long():
    
    dataset = 'dataset1'
    run = 'long'
    
    # Read three parameters
    opts = {'logging': logging, 'cachedir': '/tmp/hapi-data', 'cache': False, 'usecache': False}
    assert compare.read(server, dataset, 'scalar,vector,spectra', run, opts)

    opts = {'logging': logging, 'cachedir': '/tmp/hapi-data', 'cache': True, 'usecache': False}
    assert compare.read(server, dataset, 'scalar,vector,spectra', run, opts)

    opts = {'logging': logging, 'cachedir': '/tmp/hapi-data', 'cache': False, 'usecache': True}
    assert compare.read(server, dataset, 'scalar,vector,spectra', run, opts)


@pytest.mark.short
def test_none_stop():
    import numpy as np

    from hapiclient import hapi
    from hapiclient import hapitime2datetime
    from hapiclient import datetime2hapitime
    from datetime import timedelta

    server     = 'http://hapi-server.org/servers/TestData2.0/hapi'
    dataset    = 'dataset1'
    parameters = 'scalar'

    meta = hapi(server, dataset)
    stop = meta['stopDate']
    stop_dt = hapitime2datetime(stop)[0]

    start_dt = stop_dt - timedelta(minutes=1)
    start = datetime2hapitime(start_dt)

    data1, meta1 = hapi(server, dataset, parameters, start, None)

    data2, meta2 = hapi(server, dataset, parameters, start, stop)

    allequal = True
    for name in data1.dtype.names:
        assert np.array_equal(data1[name], data2[name])


def runall():
    from hapiclient.test import test_hapi
    for i in dir(test_hapi):
        item = getattr(test_hapi,i)
        if callable(item) and item.__name__.startswith("test_"):
            if item.__name__ == 'test_reader_long':
                continue
            print("Running " + item.__name__)
            item()


if __name__ == '__main__':
    #runall()
    #test_dataset()
    #test_reader_short()
    #test_unicode()
    #test_request2path()
    #test_reader_long()
    test_none_stop()
