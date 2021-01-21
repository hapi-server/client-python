# To test from command line, use
#   pytest -v test_hapitime2datetime.py

# To test a single function on the command line, use, e.g.,
#   pytest -v test_hapitime2datetime.py -k test_parse_string_input

# To use in program, use, e.g.,
#   from hapiclient.test.test_hapitime2datetime import test_parse_string_input
#   test_parse_string_input()

import os
import numpy as np

from hapiclient import hapitime2datetime
from hapiclient.util import log

# Create empty file
with open(os.path.realpath(__file__)[0:-2] + "log", "w") as f: pass
logging = open(os.path.realpath(__file__)[0:-2] + "log", "a")

expected = '1970-01-01T00:00:00.000000Z'

def test_api():

	log("API test.", {'logging': logging})

	Time = '1970-01-01T00:00:00.000Z'
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

	Time = ['1970-01-01T00:00:00.000Z']
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

	Time = np.array(['1970-01-01T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

	Time = b'1970-01-01T00:00:00.000Z'
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

	Time = [b'1970-01-01T00:00:00.000Z']
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected

	Time = np.array([b'1970-01-01T00:00:00.000Z'])
	a = hapitime2datetime(Time,logging=logging)
	assert a[0].tzinfo.__class__.__name__ == 'UTC'
	assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected


def test_parsing():

	log("Parse test.", {'logging': logging})

	dts = [
			"1989Z",

			"1989-01Z",

			"1989-001Z",
			"1989-01-01Z",

			"1989-001T00Z",
			"1989-01-01T00Z",

			"1989-001T00:00Z",
			"1989-01-01T00:00Z",

			"1989-001T00:00:00.Z",
			"1989-01-01T00:00:00.Z",

			"1989-01-01T00:00:00.0Z",
			"1989-001T00:00:00.0Z",

			"1989-01-01T00:00:00.00Z",
			"1989-001T00:00:00.00Z",

			"1989-01-01T00:00:00.000Z",
			"1989-001T00:00:00.000Z",

			"1989-01-01T00:00:00.0000Z",
			"1989-001T00:00:00.0000Z",

			"1989-01-01T00:00:00.00000Z",
			"1989-001T00:00:00.00000Z",

			"1989-01-01T00:00:00.000000Z",
			"1989-001T00:00:00.000000Z"
		]

	expected = '1989-01-01T00:00:00.000000Z'

	for i in range(len(dts)):
		a = hapitime2datetime(dts[i],logging=logging)
		assert a[0].tzinfo.__class__.__name__ == 'UTC'
		assert a[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected


def test_error_conditions(logging=logging):
	from hapiclient import HAPIError


	Time = "1999"
	log("Checking that hapitime2datetime(" + str(Time) + ") throws HAPIError", {'logging': logging})
	try:
		hapitime2datetime(Time, logging=logging)
	except HAPIError:
		pass
	else:
		assert False, "HAPIError not raised for hapitime2datetime(" + str(Time) + ")."


if __name__ == '__main__':
	test_api()
	test_parsing()
	test_error_conditions()
