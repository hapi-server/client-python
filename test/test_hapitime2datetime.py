# To run all tests in the __name__ == '__main__': block
#   python test_hapitime2datetime.py
#
# To run all functions that start with "test_" in this file.
#   pytest -s -v test_hapitime2datetime.py
# To suppress INFO messages, use, e.g.,
#   pytest -s -v test_hapitime2datetime.py --log-level=ERROR
#
# To test a single function on the command line, use, e.g.,
#   pytest -s -v test_hapitime2datetime.py -k test_parse_string_input
# or modify the if __name__ == '__main__': block at the end of this file to
# call only the desired test function(s).


from hapiclient import hapitime2datetime

from util.get_logger import get_logger
logger = get_logger(__name__)


def _assert_utc(dt):
  assert dt.tzinfo is not None
  assert dt.utcoffset().total_seconds() == 0


def test_api():
  import numpy

  expected = '1970-01-01T00:00:00.000000Z'

  logger.info("test_api()")

  times = [
    '1970-01-01T00:00:00.000Z',
    ['1970-01-01T00:00:00.000Z'],
    numpy.array(['1970-01-01T00:00:00.000Z']),
    b'1970-01-01T00:00:00.000Z',
    [b'1970-01-01T00:00:00.000Z'],
    numpy.array([b'1970-01-01T00:00:00.000Z'])
  ]

  for Time in times:
    logger.info("  Testing hapitime2datetime(" + str(Time) + ")")
    t = hapitime2datetime(Time)
    assert t[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected
    _assert_utc(t[0])


def test_parsing():

  logger.info("test_parsing()")

  expected = '1989-01-01T00:00:00.000000Z'

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

  for i in range(len(dts)):
    logger.info("  Testing hapitime2datetime('" + str(dts[i]) + "')")
    t = hapitime2datetime(dts[i])
    assert t[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ") == expected
    _assert_utc(t[0])


def test_error_conditions():
  from hapiclient import HAPIError
  logger.info("test_error_conditions()")

  Time = "1999"
  logger.info("  Checking that hapitime2datetime('" + str(Time) + "') throws HAPIError")
  try:
    hapitime2datetime(Time)
  except HAPIError:
    pass
  else:
    assert False, "HAPIError not raised for hapitime2datetime(" + str(Time) + ")."


if __name__ == '__main__':
  test_api()
  test_parsing()
  test_error_conditions()
