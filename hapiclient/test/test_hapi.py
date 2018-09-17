import pytest
import os
import pickle
from hapiclient.hapi import hapi
from deepdiff import DeepDiff

serverbad = 'http://hapi-server.org/servers/TestData/xhapi'
server = 'http://hapi-server.org/servers/TestData/hapi'

def writepickle(fname, var):
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data',fname)
    with open(fname, 'wb') as pickle_file: 
        pickle.dump(var, pickle_file)
    pickle_file.close()

def readpickle(fname):
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data',fname)
    with open(fname, 'rb') as pickle_file: 
        var = pickle.load(pickle_file)
    pickle_file.close()
    return var

def test_hapi():
    """Test that a call with no parameters returns something."""
    assert hapi() is not None

def test_server_list():
    """Test that specifying a server returns something."""
    server = 'http://hapi-server.org/servers/SSCWeb/hapi'
    assert hapi(server) is not None

def test_catalog():
    """Request for catalog returns correct status and first dataset"""
    meta = hapi(server)
    assert meta['status'] == {'code': 1200, 'message': 'OK'} and meta['catalog'][0]['id'] == 'dataset1'

def test_dataset():
    """Request for dataset returns dataset metadata"""
    meta = hapi(server,'dataset1')
    pklFile = 'test_dataset.pkl'
    if not os.path.isfile(pklFile):
        writepickle(pklFile,meta)
        assert True
        return
    else:
        metatest = readpickle(pklFile)
    assert DeepDiff(meta,metatest) == {}

def test_parameter():
    """Request for dataset returns parameter metadata"""
    meta = hapi(server,'dataset1')
    pklFile = 'test_parameter.pkl'
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
        hapi(serverbad)

def test_bad_dataset_name():
    """Correct error when given nonexistent dataset name"""
    with pytest.raises(Exception):
        hapi(server,'dataset1x')

def test_bad_parameter():
    """Correct error when given nonexistent parameter name"""
    with pytest.raises(Exception):
        hapi(server,'dataset1','scalarx')

def test_deprecation():
    import warnings
    warnings.warn(
        "This is deprecated, but shouldn't raise an exception, unless "
        "enable_deprecations_as_exceptions() called from conftest.py",
        DeprecationWarning)
