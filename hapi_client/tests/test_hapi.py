import pytest
from ..hapi import hapi


def test_hapi():
    """Test that a call with no parameters returns something."""
    assert hapi() is not None


def test_hapi():
    """Test that specifying a server returns something."""
    server = 'http://hapi-server.org/servers/SSCWeb/hapi'
    assert hapi(server) is not None


def test_deprecation():
    import warnings
    warnings.warn(
        "This is deprecated, but shouldn't raise an exception, unless "
        "enable_deprecations_as_exceptions() called from conftest.py",
        DeprecationWarning)
