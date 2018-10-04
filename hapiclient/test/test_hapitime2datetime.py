import pytest
from hapiclient.hapi import hapitime2datetime
import numpy as np

logging = False
expected = '1970-01-01T00:00:00.000000Z'

def test_parse_string_input():
	Time = '1970-01-01T00:00:00.000Z'
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_list_of_strings_input():
	Time = ['1970-01-01T00:00:00.000Z']
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_ndarray_of_strings_input():
	Time = np.array(['1970-01-01T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_byte_input():
	Time = b'1970-01-01T00:00:00.000Z'
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_list_of_bytes_input():
	Time = [b'1970-01-01T00:00:00.000Z']
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_ndarray_of_bytes_input():
	Time = np.array([b'1970-01-01T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

##################################################################
# Known cases where pandas fails and manual parsing needed.
def test_parse_manual_1970_001T00_00_00_000Z():
	Time = np.array([b'1970-001T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00_00Z():
	Time = np.array([b'1970-001T00:00:00.00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00_0Z():
	Time = np.array([b'1970-001T00:00:00.0Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00_Z():
	Time = np.array([b'1970-001T00:00:00.Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00Z():
	Time = np.array([b'1970-001T00:00:00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00Z():
	Time = np.array([b'1970-001T00:00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00Z():
	Time = np.array([b'1970-001T00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001Z():
	Time = np.array([b'1970-001Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_01Z():
	Time = np.array([b'1970-01Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970Z():
	Time = np.array([b'1970Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected
