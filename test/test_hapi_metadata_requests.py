# See ../README.md for instructions on running tests.
import os
import json
import pytest
import logging

from hapiclient.hapi import hapi

from util.get_logger import get_logger

logger = get_logger(__name__)

kwargs = {
    'cache': False,
    'usecache': False,
    'cachedir': '/tmp/hapi-data',
    'logging': logger.level >= logging.INFO
}

serverbad = 'http://hapi-server.org/servers/TestData/xhapi'
server = 'http://hapi-server.org/servers/TestData2.0/hapi'


def _writejson(fname, var):
    print("Writing " + fname)
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(var, f, indent=2, ensure_ascii=False)


def _readjson(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_hapi():
    """Test that a call with no parameters returns something."""
    logger.info("test_hapi()")
    assert hapi(**kwargs) is not None


def test_catalog1():
    """Test that specifying a server returns something."""
    logger.info("test_catalog1()")
    assert hapi(server, **kwargs) is not None


def test_catalog2():
    """Request for catalog returns correct status and first dataset"""
    logger.info("test_catalog2()")
    meta = hapi(server, **kwargs)
    assert meta['status'] == {'code': 1200, 'message': 'OK'} and meta['catalog'][0]['id'] == 'dataset1'


def test_dataset():
    from deepdiff import DeepDiff
    """Request for dataset returns correct dataset metadata"""
    logger.info("test_dataset()")
    meta = hapi(server, 'dataset1', **kwargs)
    jsonFile = 'test_dataset.json'
    jsonFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', jsonFile)
    if not os.path.isfile(jsonFile):
        _writejson(jsonFile, meta)
        assert True
        return
    else:
        metatest = _readjson(jsonFile)
    assert DeepDiff(meta, metatest) == {}


def test_parameter():
    from deepdiff import DeepDiff
    """Request for dataset returns correct parameter metadata"""
    logger.info("test_parameter()")
    meta = hapi(server, 'dataset1', **kwargs)
    jsonFile = 'test_parameter.json'
    jsonFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', jsonFile)
    if not os.path.isfile(jsonFile):
        _writejson(jsonFile, meta)
        assert True
        return
    else:
        metatest = _readjson(jsonFile)
    assert DeepDiff(meta,metatest) == {}


def test_bad_server_url():
    """Correct error when given bad URL"""
    from hapiclient.util import HAPIError
    logger.info("test_bad_server_url()")
    with pytest.raises(HAPIError):
        hapi(serverbad, **kwargs)


def test_bad_dataset_id():
    """Correct error when given nonexistent dataset id"""
    from hapiclient.util import HAPIError
    logger.info("test_bad_dataset_id()")
    with pytest.raises(HAPIError):
        hapi(server, 'dataset1x')


def test_bad_parameter_name():
    """Correct error when given nonexistent parameter name"""
    from hapiclient.util import HAPIError
    logger.info("test_bad_parameter_name()")
    with pytest.raises(HAPIError):
        hapi(server,'dataset1','scalarx')


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

    for name in data1.dtype.names:
        assert np.array_equal(data1[name], data2[name])


if __name__ == '__main__':
    test_hapi()
    test_catalog1()
    test_catalog2()
    test_dataset()
    test_parameter()
    test_bad_server_url()
    test_bad_dataset_id()
    test_bad_parameter_name()
    test_none_stop()
