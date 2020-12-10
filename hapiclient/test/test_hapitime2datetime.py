# To test from command line, use
#   pytest -v test_hapitime2datetime.py

# To test a single function on the command line, use, e.g.,
#   pytest -v  est_hapitime2datetime.py -k test_parse_string_input

# To use in program, use, e.g.,
#   from hapiclient.test.test_hapitime2datetime import test_parse_string_input
#   test_parse_string_input()

from hapiclient.hapi import hapitime2datetime
import numpy as np

# Create empty file
with open("test_hapitime2datetime.log", "w") as f: pass
logging = open("test_hapitime2datetime.log", "a")

expected = '1970-01-01T00:00:00.000000Z'

def test_parse_string_input():
	Time = '1970-01-01T00:00:00.000Z'
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_list_of_strings_input():
	Time = ['1970-01-01T00:00:00.000Z']
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_ndarray_of_strings_input():
	Time = np.array(['1970-01-01T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_byte_input():
	Time = b'1970-01-01T00:00:00.000Z'
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_list_of_bytes_input():
	Time = [b'1970-01-01T00:00:00.000Z']
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_ndarray_of_bytes_input():
	Time = np.array([b'1970-01-01T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_error_conditions(logging=logging):
	from hapiclient import HAPIError

	Times = [
				['1999Z','1999'],
				['1999-001Z','1999-001'],
				['1999-001T00Z','1999-001T00'],
				['1999-01Z','1999-01'],
				['1999-01-01Z','1999-01-01'],
				['1999-01-01T00Z','1999-01-01T00'],
				['1999-01-01T00:00Z','1999-01-01T00:00'],
				['1999-01-01T00:00Z','1999-01-01T00:00:00']
			]

	for Time in Times:
		if logging:
			print("Checking that hapitime2datetime(" + str(Time) + ") throws HAPIError")
		try:
			hapitime2datetime(Time)
		except HAPIError:
			pass
		else:
			assert False, "HAPIError not raised for hapitime2datetime(" + str(Time) + ")."

	for Time in Times:
		time = Time[0][0:-1] # Remove Z
		if logging:
			print("Checking that hapitime2datetime(" + str(time) + ") throws HAPIError")
		try:
			hapitime2datetime(time)
		except HAPIError:
			pass
		else:
			assert False, "HAPIError not raised for hapitime2datetime(" + str(Time) + ")."

def test_parse_1970_01_01T00_00_00Z():
	Time = np.array([b'1970-001T00:00:00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

# Test cases where pandas fails and manual parsing needed.
def test_parse_manual_1970_001T00_00_00_000Z():
	Time = np.array([b'1970-001T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00_00Z():
	Time = np.array([b'1970-001T00:00:00.00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00_0Z():
	Time = np.array([b'1970-001T00:00:00.0Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00_Z():
	Time = np.array([b'1970-001T00:00:00.Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00_00Z():
	Time = np.array([b'1970-001T00:00:00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00_00Z():
	Time = np.array([b'1970-001T00:00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001T00Z():
	Time = np.array([b'1970-001T00Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_001Z():
	Time = np.array([b'1970-001Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970_01Z():
	Time = np.array([b'1970-01Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

def test_parse_manual_1970Z():
	Time = np.array([b'1970Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected
