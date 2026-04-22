# See ../README.md for instructions on running tests.
import datetime
from hapiclient.hapitime import datetime2hapitime

from util.get_logger import get_logger
logger = get_logger(__name__)

def test_datetime2hapitime():

    logger.info("test_datetime2hapitime()")

    dt = datetime.datetime(2000,1,1)

    logger.info("  Input datetime: {}".format(dt))
    hapi_time = datetime2hapitime(dt)
    logger.info("  Output HAPI time: {}".format(hapi_time))

    assert hapi_time == '2000-01-01T00:00:00.000000Z'


    dts = [datetime.datetime(2000,1,1), datetime.datetime(2000,1,2)]

    logger.info("  Input datetimes: {}".format(dts))
    hapi_times = datetime2hapitime(dts)
    logger.info("  Output HAPI times: {}".format(hapi_times))

    assert hapi_times[0] == '2000-01-01T00:00:00.000000Z'
    assert hapi_times[1] == '2000-01-02T00:00:00.000000Z'


if __name__ == '__main__':
    test_datetime2hapitime()
