"""Functions for manipulating HAPI times (restricted ISO 8601 strings)."""
import re
import time

import pandas
import isodate
import numpy as np

from hapiclient.util import error, log

def hapitime_reformat(form_to_match, given_form, logging=False):
    """Reformat a given HAPI time to match format of another HAPI time.

    ``hapitime_reformat(match, given)`` truncates or pads ``given`` so that it has
    the same format as ``match``.

    This function allows for efficient subsetting of arrays of HAPI time
    strings. For example, to select all time elements after a time of ``start``,
    first convert ``start`` so that it has the same format as the elements of
    ``data['Time']``

    ::

        start = hapitime_reformat(data['Time'][0], start)
    
    Then subset using
    
    ::

        data = data[data['Time'] >= start]

    This is much more efficient than converting ``data['Time']`` to ``datetime``
    objects and using ``datetime`` comparsion methods.

    Examples
    --------
    ::

        hapitime_format_str('1989Z', '1989-01Z') # 1989Z
        hapitime_format_str('1989-001T00:00Z', '1999-01-21Z') # 1999-021T00:00Z

    """

    log('ref:       {}'.format(form_to_match), {'logging': logging})
    log('given:     {}'.format(given_form), {'logging': logging})

    if 'T' in given_form:
        dt_given = isodate.parse_datetime(given_form)
    else:
        # Remove trailing Z b/c parse_date does not implement of date with
        # trailing Z, which is valid IS8601.
        dt_given = isodate.parse_date(given_form[0:-1])

    # Get format string, e.g., %Y-%m-%dT%H
    format_ref = hapitime_format_str([form_to_match])

    if '%f' in format_ref:
        form_to_match = form_to_match.strip('Z')
        form_to_match_fractional = form_to_match.split('.')[-1]
        form_to_match = ''.join(form_to_match.split('.')[:-1])

        given_form_fractional = '000000000'
        given_form_fmt = hapitime_format_str([given_form])
        given_form = given_form.strip('Z')

        if '%f' in given_form_fmt:
            given_form_fractional = given_form.split('.')[-1]
            given_form = ''.join(given_form.split('.')[:-1])

        converted = hapitime_reformat(form_to_match+'Z', given_form+'Z')
        converted = converted.strip('Z')
        
        converted_fractional = '{:0<{}.{}}'.format(given_form_fractional, 
                                                   len(form_to_match_fractional),
                                                   len(form_to_match_fractional))
        converted = converted + '.' + converted_fractional

        if 'Z' in format_ref:
            return converted + 'Z'
        
        return converted

    converted = dt_given.strftime(format_ref)
    
    if len(converted) > len(form_to_match):
        converted = converted[0:len(form_to_match)-1] + "Z"

    log('converted: {}'.format(converted), {'logging': logging})
    log('ref fmt:   {}'.format(format_ref), {'logging': logging})
    log('----', {'logging': logging})

    return converted


def hapitime_format_str(Time):
    """Determine the time format string for a HAPI time."""

    d = 0
    # Catch case where no trailing Z
    # Technically HAPI ISO 8601 must have trailing Z; See
    # https://github.com/hapi-server/data-specification/blob/master/
    # hapi-dev/HAPI-data-access-spec-dev.md#representation-of-time
    if not re.match(r".*Z$", Time[0]):
        d = 1

    # Parse date part
    # If h=True then hour given.
    # If hm=True, then hour and minute given.
    # If hms=True, them hour, minute, and second given.
    (h, hm, hms) = (False, False, False)

    if len(Time[0]) == 4 or (len(Time[0]) == 5 and Time[0][-1] == "Z"):
        fmt = '%Y'
    elif re.match(r"[0-9]{4}-[0-9]{3}", Time[0]):
        # YYYY-DOY format
        fmt = "%Y-%j"
        if len(Time[0]) >= 12 - d:
            h = True
        if len(Time[0]) >= 15 - d:
            hm = True
        if len(Time[0]) >= 18 - d:
            hms = True
    elif re.match(r"[0-9]{4}-[0-9]{2}", Time[0]):
        # YYYY-MM-DD format
        fmt = "%Y-%m"
        if len(Time[0]) > 8:
            fmt = fmt + "-%d"
        if len(Time[0]) >= 14 - d:
            h = True
        if len(Time[0]) >= 17 - d:
            hm = True
        if len(Time[0]) >= 20 - d:
            hms = True
    else:
        # TODO: Also check for invalid time string lengths. Use JSON schema
        # regular expressions for allowed versions of ISO 8601.
        # https://github.com/hapi-server/verifier-nodejs/tree/master/schemas
        error('First time value %s is not a valid HAPI Time' % Time[0])

    if h:
        fmt = fmt + "T%H"
    if hm:
        fmt = fmt + ":%M"
    if hms:
        fmt = fmt + ":%S"

    if re.match(r".*\.[0-9].*$", Time[0]):
        fmt = fmt + ".%f"
    if re.match(r".*\.$", Time[0]) or re.match(r".*\.Z$", Time[0]):
        fmt = fmt + "."

    if re.match(r".*Z$", Time[0]):
        fmt = fmt + "Z"

    return fmt


def hapitime2datetime(Time, **kwargs):
    """Convert HAPI timestamps to Python datetimes.

    A HAPI-compliant server represents time as an ISO 8601 string
    (with several constraints - see the `HAPI specification
    <https://github.com/hapi-server/data-specification/blob/master/hapi-dev/HAPI-data-access-spec-dev.md#representation-of-time>`_)
    
    `hapi()` reads these time strings into a NumPy array of Python byte literals.
    This function converts these byte literals to Python datetime objects.
    
    Typical usage:
    
    ::
    
        data = hapi(...) # Get data
        DateTimes = hapitime2datetime(data['Time']) # Convert
    
    
    All HAPI time strings must have a trailing Z. This function only checks the
    first element in Time array for compliance.
    
    Parameter
    ---------
    Time:
        - A numpy array of HAPI timestamp byte literals
        - A numpy array of HAPI timestamp strings
        - A list of HAPI timestamp byte literals
        - A list of HAPI timestamp strings
        - A HAPI timestamp byte literal
        - A HAPI timestamp strings
    
    Returns
    -------
    A NumPy array Python of datetime objects with length = len(Time)
    
    Examples
    --------
    All of the following return
    
    ::
    
        array([datetime.datetime(1970, 1, 1, 0, 0, tzinfo=<UTC>)], dtype=object)
    
    ::
    
        from hapiclient.time import hapitime2datetime
        import numpy as np
    
        hapitime2datetime(np.array([b'1970-01-01T00:00:00.000Z']))
        hapitime2datetime(np.array(['1970-01-01T00:00:00.000Z']))
    
        hapitime2datetime([b'1970-01-01T00:00:00.000Z'])
        hapitime2datetime(['1970-01-01T00:00:00.000Z'])
    
        hapitime2datetime([b'1970-01-01T00:00:00.000Z'])
        hapitime2datetime('1970-01-01T00:00:00.000Z')
    """
    from datetime import datetime

    try:
        # Python 2
        import pytz
        tzinfo = pytz.UTC
    except:
        tzinfo = datetime.timezone.utc

    if type(Time) == list:
        Time = np.asarray(Time)
        if not all(list( map(lambda x: type(x) in [np.str_, np.bytes_, str, bytes], Time) )):
            raise ValueError

    allow_missing_Z = False
    if 'allow_missing_Z' in kwargs and kwargs['allow_missing_Z'] == True:
        allow_missing_Z = True

    opts = kwargs.copy()

    if type(Time) == list:
        Time = np.asarray(Time)
    if type(Time) == str or type(Time) == bytes:
        Time = np.asarray([Time])

    if type(Time) != np.ndarray:
        error('Problem with time data.' + '\n')
        return

    if Time.size == 0:
        error('Time array is empty.' + '\n')
        return

    reshape = False
    if Time.shape[0] != Time.size:
        reshape = True
        shape = Time.shape
        Time = Time.flatten()

    if type(Time[0]) == np.bytes_:
        try:
            Time = Time.astype('U')
        except:
            error('Problem with time data. First value: ' + str(Time[0]) + '\n')
            return

    tic = time.time()


    if Time[0][-1] != "Z" and allow_missing_Z == False:
        error("HAPI Times must have trailing Z. First element of input " + \
              "Time array does not have trailing Z.")

    try:
        # This is the fastest conversion option. But it will fail on YYYY-DOY
        # format and other valid ISO 8601 dates such as 2001-01-01T00:00:03.Z
        # When infer_datetime_format is used, a TimeStamp object returned,
        # which is the reason for the to_pydatetime() call. (When format=... is
        # used, a datetime object is returned.)
        # Although all HAPI timestamps will have trailing Z, in some cases,
        # infer_datetime_format will not return a timezone-aware Timestamp. This
        # is the reason for the call to tz_convert(tzinfo).
        # TODO: Use hapitime_format_str() and pass this as format=...
        Timeo = Time[0]
        Time = pandas.to_datetime(Time, infer_datetime_format=True).tz_convert(tzinfo).to_pydatetime()
        if reshape:
            Time = np.reshape(Time, shape)
        toc = time.time() - tic
        log("Pandas processing time = %.4fs, first time = %s" % (toc, Timeo), opts)
        return Time
    except:
        log("Pandas processing failed, first time = %s" % Time[0], opts)


    # Convert from Python byte literals to unicode strings
    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html
    # https://www.b-list.org/weblog/2017/sep/05/how-python-does-unicode/
    Time = Time.astype('U')
    # The new Time variable requires 4x more memory.
    # Could save memory at cost of speed by decoding at each iteration below, e.g.
    # Time[i] -> Time[i].decode('utf-8')

    pythonDateTime = np.empty(len(Time), dtype=object)

    fmt = hapitime_format_str(Time)

    # TODO: Will using pandas.to_datetime here with fmt work?
    try:
        parse_error = True
        for i in range(0, len(Time)):
            if Time[i][-1] != "Z" and allow_missing_Z == False:
                parse_error = False
                raise
            pythonDateTime[i] = datetime.strptime(Time[i], fmt).replace(tzinfo=tzinfo)
    except:
        if parse_error:
            error('Could not parse time value ' + Time[i] + ' using ' + fmt)
        else:
            error("HAPI Times must have trailing Z. Time[" + str(i) + "] = " \
                  + Time[i] + " does not have trailing Z.")

    toc = time.time() - tic
    log("Manual processing time = %.4fs, Input = %s, fmt = %s" % \
        (toc, Time[0], fmt), opts)

    if reshape:
        pythonDateTime = np.reshape(pythonDateTime, shape)

    return pythonDateTime


def datetime2hapitime(dts):
    """Convert Python datetime object(s) to ISO 8601 string(s)

     Typical usage:
    
    ::
    
        import datetime
        dts = [datetime.datetime(2000,1,1),datetime.datetime(2000,1,2)]
        hapi_times = datetime2hapitime(dts)
        print(hapi_timies)    
    
    Parameter
    ---------
    dts:
        - A Python datetime object
        - A list of Python datetime object(s)

    Returns
    -------
    - A ISO 8601 string (if input is Python datetime object)
    - A list of ISO 8601 strings (if input is list of Python datetime object)
    """

    # TODO: Add minimal keyword?

    import datetime

    single = False
    if isinstance(dts, list) == False:
        single = True
        dts = [dts]

    hapitimes = [dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ') for dt in dts]

    if single == True:
        return hapitimes[0]
    else:
        return hapitimes
