import pytest
import os
import pickle
import numpy as np

from deepdiff import DeepDiff
from hapiclient.hapi import hapi
from hapiclient.test.readcompare import readcompare, clearcache

serverbad = 'http://hapi-server.org/servers/TestData/xhapi'
server = 'http://hapi-server.org/servers/TestData/hapi'

# To use in program, use, e.g.,
# from hapiclient.test.test_hapi import test_reader_short
# test_reader_short()

def writepickle(fname, var):
    print("!!!!!!!!!!!!!!")
    print("Writing " + fname)
    print("!!!!!!!!!!!!!!")
    with open(fname, 'wb') as pickle_file:
        pickle.dump(var, pickle_file)
    pickle_file.close()

def readpickle(fname):
    with open(fname, 'rb') as pickle_file:
        var = pickle.load(pickle_file)
    pickle_file.close()
    return var

def test_hapi():
    """Test that a call with no parameters returns something."""
    assert hapi() is not None

def test_server_list():
    """Test that specifying a server returns something."""
    assert hapi(server) is not None

def test_catalog():
    """Request for catalog returns correct status and first dataset"""
    meta = hapi(server)
    assert meta['status'] == {'code': 1200, 'message': 'OK'} and meta['catalog'][0]['id'] == 'dataset1'

def test_dataset():
    """Request for dataset returns correct dataset metadata"""
    meta = hapi(server,'dataset1')
    pklFile = 'test_dataset.pkl'
    pklFile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data',pklFile)
    if not os.path.isfile(pklFile):
        writepickle(pklFile,meta)
        assert True
        return
    else:
        metatest = readpickle(pklFile)
    assert DeepDiff(meta,metatest) == {}

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
 
def test_bad_server_url():
    """Correct error when given bad URL"""
    with pytest.raises(Exception):
        hapi(serverbad, {'logging': True})

def test_bad_dataset_name():
    """Correct error when given nonexistent dataset name"""
    with pytest.raises(Exception):
        hapi(server,'dataset1x')

def test_bad_parameter():
    """Correct error when given nonexistent parameter name"""
    with pytest.raises(Exception):
        hapi(server,'dataset1','scalarx')

def test_reader_short():
        
    dataset = 'dataset1'
    run = 'short'
    
    # Cache = False (will read data into buffer)    
    opts = {'logging': False, 'cachedir': '/tmp/hapi-data', 'usecache': False}

    opts['cache'] = False

    # Read one parameter
    clearcache(opts)
    assert readcompare(server, dataset, 'scalar', run, opts)

    # Read two parameters
    clearcache(opts)
    assert readcompare(server, dataset, 'scalar,vector', run, opts)

    # Read all parameters
    clearcache(opts)
    assert readcompare(server, dataset, '', run, opts)

    # Cache = True (will write files then read)
    opts['cache'] = True

    # Read one parameter
    clearcache(opts)
    assert readcompare(server, dataset, 'scalar', run, opts)

    # Read two parameters
    clearcache(opts)
    assert readcompare(server, dataset, 'scalar,vector', run, opts)
    clearcache(opts)

    # Read all parameters
    clearcache(opts)
    assert readcompare(server, dataset, '', run, opts)
    
def test_cache_short():
    # Compare read with empty cache with read with hot cache and usecache=True
    dataset = 'dataset1'
    start = '1970-01-01'
    stop  = '1970-01-01T00:00:03'

    opts = {'logging': False, 'cachedir': '/tmp/hapi-data', 'cache': True}

    opts['usecache'] = False
    clearcache(opts)
    data, meta  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    opts['usecache'] = True
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    assert np.array_equal(data, data2)

def test_subset_short():
    
    dataset = 'dataset1'
    start = '1970-01-01'
    stop  = '1970-01-01T00:00:03'
    opts = {'logging': False, 'cachedir': '/tmp/hapi-data', 'cache': True}

    opts['usecache'] = False
    
    # Request two subsets with empty cache. Common parts should be same.
    clearcache(opts)
    data, meta  = hapi(server, dataset, 'scalarint', start, stop, **opts)

    clearcache(opts)
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['scalarint'], data2['scalarint'])
    assert ok

    # Request all parameters and single parameter. Common parameter should be same.
    clearcache(opts)
    data, meta  = hapi(server, dataset, '', start, stop, **opts)

    clearcache(opts)
    data2, meta2  = hapi(server, dataset, 'vectorint', start, stop, **opts)
        
    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['vectorint'], data2['vectorint'])
    assert ok

    opts['usecache'] = True
    
    # Request two subsets with hot cache. Common parts should be same.
    data, meta  = hapi(server, dataset, 'scalarint', start, stop, **opts)
    data2, meta2  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['scalarint'], data2['scalarint'])
    assert ok

    # Request all parameters and single parameter with hot cache. Common parameter should be same.
    clearcache(opts)
    data, meta  = hapi(server, dataset, '', start, stop, **opts)

    clearcache(opts)
    data2, meta2  = hapi(server, dataset, 'vectorint', start, stop, **opts)
        
    ok = np.array_equal(data['Time'], data2['Time'])
    ok = ok and np.array_equal(data['vectorint'], data2['vectorint'])
    assert ok

@pytest.mark.long
def test_reader_long():
    
    opts = {'logging': False, 'cachedir': '/tmp/hapi-data', 'cache': False, 'usecache': False}
    dataset = 'dataset1'
    
    run = 'long'
    
    # Read two parameters
    clearcache(opts)
    assert readcompare(server, dataset, 'scalar,vector', run, opts)
        