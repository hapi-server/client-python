# See ../README.md for instructions on running tests.
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

server = 'http://hapi-server.org/servers/TestData2.0/hapi'
dataset = 'dataset1'
start = '1970-01-01'
stop  = '1970-01-01T00:00:03'

import pytest

def test_cache_short():

    # Compare read with empty cache with read with hot cache and usecache=True

    opts = {**kwargs, 'cache': True}

    opts['usecache'] = False
    shutil.rmtree(opts['cachedir'], ignore_errors=True)
    data, _  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    opts['usecache'] = True
    data2, _  = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)

    assert compare.equal(data, data2)


@pytest.mark.filterwarnings("ignore::hapiclient.util.HAPIWarning")
def test_cache_error():

    from unittest.mock import patch

    import pathlib
    import tempfile
    from hapiclient.util import write_atomic

    from hapiclient.util import HAPIWarning

    def assert_warns(fn, expected):
        import pytest
        with pytest.warns(HAPIWarning, match=expected):
            result = fn()
        return result

    # Direct calls to write_atomic()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = pathlib.Path(tmpdir) / 'test.json'
        data = {'key': 'value'}

        def call_write_atomic():
            write_atomic(str(path), data)

        # Simulate write failure
        with patch('json.dump', side_effect=OSError('No space left on device')):
            assert_warns(call_write_atomic, 'Failed to write cache file')
        assert not path.exists(), 'File should not exist after write failure'

        # Simulate os.replace failure after successful write
        with patch('os.replace', side_effect=OSError('Permission denied')):
            assert_warns(call_write_atomic, 'Failed to rename cache file from')
        assert not path.exists(), 'File should not exist after rename failure'

        # Simulate write failure AND unlink failure
        patch1 = patch('json.dump', side_effect=OSError('No space left on device'))
        patch2 = patch('pathlib.Path.unlink', side_effect=OSError('Permission denied'))
        with patch1, patch2:
            assert_warns(call_write_atomic, 'Failed to remove temporary cache file')

        # Simulate successful write
        write_atomic(str(path), data)
        assert path.exists(), 'File should exist after successful write'


    # Indirect calls to write_atomic()
    dataset = 'dataset1'
    start = '1970-01-01'
    stop  = '1970-01-01T00:00:03'

    opts = {**kwargs, 'cache': True, 'usecache': False}

    def call_hapi():
        data, meta = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)
        return data, meta

    def assert_data_valid(data):
        msg = hapi(server, dataset, 'scalarint,vectorint', start, stop, **opts)
        assert data['Time'][0] == b'1970-01-01T00:00:00.000Z', msg

    with patch('pickle.dump', side_effect=OSError('No space left on device')):
        data, _ = assert_warns(call_hapi, 'Failed to write cache file')
    assert_data_valid(data)

    with patch('os.replace', side_effect=OSError('Permission denied')):
        data, _ = assert_warns(call_hapi, 'Failed to rename cache file from')
    assert_data_valid(data)

    p1 = patch('pickle.dump', side_effect=OSError('No space left on device'))
    p2 = patch('pathlib.Path.unlink', side_effect=OSError('Permission denied'))
    with p1, p2:
        data, _ = assert_warns(call_hapi, 'Failed to remove temporary cache file')
    assert_data_valid(data)


if __name__ == '__main__':
  test_cache_short()
  test_cache_error()