import os
import sys
import time
import warnings

import pandas
import numpy as np

from hapiclient.util import log, error, urlopen, urlretrieve, query_name
from hapiclient.cache import (
    cachedir, data_cache_paths,
    _compute_dt, _missing_length,
)


def get_binary(meta, SERVER, DATASET, PARAMETERS, START, STOP, opts):

  _, fnamebin, _, _ = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts)
  urld = cachedir(opts["cachedir"], SERVER)

  urlcsv = (SERVER + '/data?' + query_name(meta, 'dataset') + '=' + DATASET
            + '&parameters=' + PARAMETERS
            + '&' + query_name(meta, 'start') + '=' + START
            + '&' + query_name(meta, 'stop') + '=' + STOP)
  urlbin = urlcsv + '&format=binary'

  dt, _, _, _, _ = _compute_dt(meta, opts)

  if opts['method'] != '':
    warnings.warn("Method argument is ignored when format='binary.")

  if opts["cache"]:
    log('Writing %s to %s' % (urlbin, fnamebin.replace(urld + '/', '')), opts)
    tic0 = time.time()
    urlretrieve(urlbin, fnamebin)
    toc0 = time.time() - tic0
    log('Reading and parsing %s' % fnamebin.replace(urld + '/', ''), opts)
    tic = time.time()
    data = _parse_binary(fnamebin, dt, meta, opts, urlbin)
  else:
    from io import BytesIO
    log('Writing %s to buffer' % urlbin.replace(urld + '/', ''), opts)
    tic0 = time.time()
    buff = BytesIO(urlopen(urlbin).read())
    toc0 = time.time() - tic0
    log('Parsing BytesIO buffer.', opts)
    tic = time.time()
    data = _parse_binary(buff, dt, meta, opts, urlbin)

  toc = time.time() - tic

  return data, toc0, toc


def _parse_binary(source, dt, meta, opts, urlbin):
  # Handle Unicode strings (since HAPI 3.1)
  dto = []
  for i in range(len(dt)):
    dto.append(dt[i])
    if isinstance(dt[i][1], str) and dt[i][1][0] == 'U' and meta['parameters'][i]['type'] == 'string':
      # numpy.frombuffer() requires S instead of U
      # because Unicode is variable length.
      dt[i] = list(dt[i])
      dt[i][1] = dt[i][1].replace('U', 'S')
      dt[i] = tuple(dt[i])

  try:
    if isinstance(source, str):
      data = np.fromfile(source, dtype=dt)
    else:
      data = np.frombuffer(source.read(), dtype=dt)
  except Exception as e:
    error('Malformed response? Could not read {}: {}'.format(urlbin, e))

  # Handle Unicode
  time_name = meta['parameters'][0]['name']
  datanew = np.ndarray(shape=data[time_name].shape, dtype=dto)
  for i in range(0, len(dto)):
    name = meta['parameters'][i]['name']
    if sys.version_info[0] < 3:
      # str() here is needed for Python 2.7. Numpy does not allow
      # Unicode names in this version and if a dt is created
      # with Unicode, it automatically converts Unicode chars to
      # slash encoded ASCII.
      name = str(name)
    if data[name].size > 0 and isinstance(dt[i][1], str) and 'U' in dto[i][1]:
      # Decode data.
      datanew[name] = np.char.decode(data[name])
    else:
      datanew[name] = data[name]

  return datanew


def get_csv(meta, SERVER, DATASET, PARAMETERS, START, STOP, opts):
  # HAPI CSV
  fnamecsv, _, _, _ = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts)
  urld = cachedir(opts["cachedir"], SERVER)

  urlcsv = (SERVER + '/data?' + query_name(meta, 'dataset') + '=' + DATASET
            + '&parameters=' + PARAMETERS
            + '&' + query_name(meta, 'start') + '=' + START
            + '&' + query_name(meta, 'stop') + '=' + STOP)

  dt, cols, psizes, pnames, ptypes = _compute_dt(meta, opts)
  missing_length = _missing_length(meta, opts)

  file_empty = False

  if opts["cache"]:
    log('Writing %s to %s' % (urlcsv, fnamecsv.replace(urld + '/', '')), opts)
    tic0 = time.time()
    urlretrieve(urlcsv, fnamecsv)
    toc0 = time.time() - tic0
    log('Reading and parsing %s' % fnamecsv.replace(urld + '/', ''), opts)
    tic = time.time()
    if os.path.getsize(fnamecsv) == 0:
      file_empty = True
      data = np.array([], dtype=dt)
  else:
    from io import StringIO
    log('Writing %s to buffer' % urlcsv.replace(urld + '/', ''), opts)
    tic0 = time.time()
    fnamecsv = StringIO(urlopen(urlcsv).read().decode())
    fnamecsv.seek(0, os.SEEK_END)
    if fnamecsv.tell() == 0:
      file_empty = True
      data = np.array([], dtype=dt)
    else:
      fnamecsv.seek(0)
    toc0 = time.time() - tic0
    log('Parsing StringIO buffer.', opts)
    tic = time.time()

  if not file_empty:
    if not missing_length:
      data = _parse_csv(fnamecsv, dt, cols, psizes, pnames, ptypes, opts, urlcsv)
    else:
      data = _parse_csv_missing_length(fnamecsv, dt, cols, psizes, pnames, ptypes, opts, urlcsv)

  toc = time.time() - tic

  return data, toc0, toc


def _parse_csv(fnamecsv, dt, cols, psizes, pnames, ptypes, opts, urlcsv):
  # All string and isotime parameters have a length in metadata.
  if opts['method'] == 'numpy':
    try:
      kwargs = {
          'dtype': dt,
          'delimiter': ',',
          'replace_space': ' ',
          'deletechars': '',
          'encoding': 'utf-8'
      }
      data = np.genfromtxt(fnamecsv, **kwargs)
    except Exception as e:
      error('np.genfromtxt({}) gave {} using data from {}'.format(fnamecsv, e, urlcsv))

  if opts['method'] == '' or opts['method'] == 'pandas':
    # Read file into Pandas DataFrame
    kwargs = {
        'sep': ',',
        'header': None,
        'encoding': 'utf-8',
        'skipinitialspace': True,
        'keep_default_na': False,
        'na_values': ['NaN', 'nan', 'Nan', 'naN', ' "NaN"', ' "nan"', ' "Nan"', ' "naN"', '"NaN"', '"nan"', '"Nan"', '"naN"']
    }
    """
    Note that this does not handle trailing whitespace after
    any of the na_values. (There is no skiptrailingspace option).
    Stripping trailing whitespace would require adding something
    like
        def strip_field(x):
            # Strip whitespace and normalize NaN values.
            x = x.strip()
            return np.nan if x.lower() == "nan" else x

        ncols = cols[-1][1] + 1
        csv_kwargs["converters"] = {i: strip_field for i in range(ncols)}
    """
    try:
      df = pandas.read_csv(fnamecsv, **kwargs)
    except Exception as e:
      error('pandas.read_csv({}) gave {} using data from {}'.format(fnamecsv, e, urlcsv))

    # Allocate output N-D array (It is not possible to pass dtype=dt
    # as computed to pandas.read_csv; pandas dtype is different
    # from numpy's dtype.)
    data = np.ndarray(shape=(len(df)), dtype=dt)
    # Insert data from dataframe 'df' columns into N-D array 'data'
    for i in range(0, len(pnames)):
      shape = np.append(len(data), psizes[i])
      # In numpy 1.8.2 and Python 2.7, this throws an error
      # for no apparent reason. Works as expected in numpy 1.10.4
      datap = df.values[:, np.arange(cols[i][0], cols[i][1] + 1)]
      data[pnames[i]] = np.squeeze(np.reshape(datap, shape))

  return data


def _parse_csv_missing_length(fnamecsv, dt, cols, psizes, pnames, ptypes, opts, urlcsv):

  # At least one requested string or isotime parameter does not
  # have a length in metadata. More work to do to read.
  if opts['method'] == 'numpy' or opts['method'] == 'numpynolength':
    # If requested method was numpy, use numpynolength method.

    ncols = cols[-1][1] + 1

    def normalize_field(value):
      if isinstance(value, bytes):
        value = value.decode('utf-8')
      value = value.strip()
      if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1].strip()
      if value.lower() == 'nan':
        return 'nan'
      return value

    converters = {i: normalize_field for i in range(ncols)}

    kwargs = {
      'dtype': None,
      'delimiter': ',',
      'replace_space': ' ',
      'deletechars': '',
      'encoding': 'utf-8',
      'converters': converters
    }
    try:
      table = np.genfromtxt(fnamecsv, **kwargs)
    except Exception as e:
      error('np.genfromtxt({}) gave {} using data from {}'.format(fnamecsv, e, urlcsv))

    # table is a 1-D array. Each element is a row in the file.
    # - If the data types are not the same for each column,
    # the elements are tuples with length equal to the number
    # of columns.
    # - If the data types are the same for each column, which
    # will happen if only Time is requested or Time and
    # a string or isotime parameter is requested, then table
    # has rows that are 1-D numpy arrays.

    # Contents of 'table' will be placed into N-D array 'data'.
    data = np.ndarray(shape=(len(table)), dtype=dt)

    # Insert data from 'table' into N-D array 'data'
    if table.dtype.names is None:
      if len(pnames) == 1:
        # Only time parameter requested.
        data[pnames[0]] = table[:]
      else:
        # All columns in 'table' have the same data type
        # so table is a 2-D numpy matrix
        for i in range(0, len(pnames)):
          shape = np.append(len(data), psizes[i])
          datap = table[:, np.arange(cols[i][0], cols[i][1] + 1)]
          data[pnames[i]] = np.squeeze(np.reshape(datap, shape))
    else:
      # Table is not a 2-D numpy matrix.
      # Extract each column (don't know how to do this with slicing
      # notation, e.g., data['varname'] = table[:][1:3]). Instead,
      # loop over each parameter (pn) and aggregate columns.
      # Then insert aggregated columns into N-D array 'data'.
      for pn in range(0, len(cols)):
        shape = np.append(len(data), psizes[pn])
        for c in range(cols[pn][0], cols[pn][1] + 1):
          if c == cols[pn][0]:
            # New parameter
            tmp = table[table.dtype.names[c]]
          else:
            # Aggregate
            tmp = np.vstack((tmp, table[table.dtype.names[c]]))
        tmp = np.squeeze(np.reshape(np.transpose(tmp), shape))

        data[pnames[pn]] = tmp

  if opts['method'] == '' or opts['method'] == 'pandas' or opts['method'] == 'pandasnolength':
    # If requested method was pandas, use pandasnolength method.

    # TODO: Duplicate code.
    # Read file into Pandas DataFrame
    csv_kwargs = {
      'sep': ',',
      'header': None,
      'encoding': 'utf-8',
      'skipinitialspace': True,
      'keep_default_na': False,
      'na_values': ['NaN', 'nan', 'Nan', 'naN', ' "NaN"', ' "nan"', ' "Nan"', ' "naN"', '"NaN"', '"nan"', '"Nan"', '"naN"']
    }
    try:
      df = pandas.read_csv(fnamecsv, **csv_kwargs)
    except Exception as e:
      error('pandas.read_csv({}) gave {} using data from {}'.format(fnamecsv, e, urlcsv))

    # Allocate output N-D array (It is not possible to pass dtype=dt
    # as computed to pandas.read_csv, so need to create new ND array.)
    data = np.ndarray(shape=(len(df)), dtype=dt)

    # Insert data from dataframe into N-D array
    for i in range(0, len(pnames)):
      shape = np.append(len(data), psizes[i])
      # In numpy 1.8.2 and Python 2.7, this throws an error for no apparent reason.
      # Works as expected in numpy 1.10.4
      datap = df.values[:, np.arange(cols[i][0], cols[i][1] + 1)]
      data[pnames[i]] = np.squeeze(np.reshape(datap, shape))

  # Any of the string parameters that do not have an associated
  # length in the metadata will have dtype='O' (object).
  # These parameters must be converted to have a dtype='SN', where
  # N is the maximum string length. N is determined automatically
  # when using astype('<S') (astype uses largest N needed).
  dt2 = []  # Will have dtypes with strings lengths calculated.
  for i in range(0, len(pnames)):
    if data[pnames[i]].dtype == 'O':
      if ptypes[i] == 'isotime':
        dtype = (pnames[i], str(data[pnames[i]].astype('<S').dtype), psizes[i])
      else:
        dtype = (pnames[i], str(data[pnames[i]].astype('<U').dtype), psizes[i])
    else:
      dtype = dt[i]

    # https://numpy.org/doc/stable/release/1.17.0-notes.html#shape-1-fields-in-dtypes-won-t-be-collapsed-to-scalars-in-a-future-version
    if len(dtype) > 2 and dtype[2] == 1:
      dtype = dtype[0:2]
    dt2.append(dtype)

  # Create new N-D array that won't have any parameters with
  # type = 'O'.
  data2 = np.ndarray(data.shape, dt2)

  for i in range(0, len(pnames)):
    if data[pnames[i]].dtype == 'O':
      data2[pnames[i]] = data[pnames[i]].astype(dt2[i][1])
    else:
      data2[pnames[i]] = data[pnames[i]]
      # Save memory by not copying (does this help?)
      # data2[pnames[i]] = np.array(data[pnames[i]],copy=False)

  return data2
