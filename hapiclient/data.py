def data(server, dataset, parameters, start, stop, opts):

  import os
  import time

  from datetime import datetime

  from hapiclient.log import log
  from hapiclient.util import warning, subset_meta, unicode_check, fix_parameters, missing_length
  from hapiclient.cache import cachedir, data_cache_read_metax, data_cache_read_npy, data_cache_write
  from hapiclient.get import get_binary, get_csv
  from hapiclient.info import info
  from hapiclient.capabilities import capabilities

  unicode_check(dataset, parameters)
  parameters = fix_parameters(parameters)

  urld = cachedir(opts["cachedir"], server)
  if opts['usecache'] or opts['cache']:
    log('cache subdirectory = %s' % urld)

  if stop is None:
    log('STOP was given as None. Getting stopDate for dataset.')
    meta = info(server, dataset, None, opts)
    stop = meta['stopDate']
    log(f'Using STOP = {stop}')

  tic_totalTime = time.time()

  meta = data_cache_read_metax(server, dataset, parameters, start, stop, opts)
  metaFromCache = meta is not None
  if not metaFromCache:
    meta = info(server, dataset, None, opts)

  # Add information to metadata so we can figure out the request needed
  # to generate it. Will also be used for labeling plots by hapiplot().
  meta.update({"x_server": server})
  meta.update({"x_dataset": dataset})

  if opts["cache"]:
    if not os.path.exists(urld):
      os.makedirs(urld)

  if opts['dt_chunk'] == 'infer':
    opts['dt_chunk'] = _dt_chunk_infer(meta, opts)

  if opts['n_chunks'] is not None or opts['dt_chunk'] is not None:
    chunk_result = _get_chunks(server, dataset, parameters, start, stop, opts, tic_totalTime)
    if chunk_result is not None:
      return chunk_result

  if not metaFromCache:
    meta = subset_meta(meta, parameters)

  tic = time.time()
  data_cached = data_cache_read_npy(server, dataset, parameters, start, stop, opts)
  if data_cached is not None:
    meta['x_totalTime'] = time.time() - tic_totalTime
    meta['x_readTime'] = tic - tic_totalTime
    meta['x_downloadTime'] = 0
    return data_cached, meta

  caps = capabilities(server, opts)
  opts['format'] = _get_format(caps, opts)

  # length attribute required for all parameters when serving binary but
  # is only required for time parameter when serving CSV. This catches
  # case where server provides binary but is missing a length attribute
  # in one or more string parameters that were requested. In this case,
  # there is not enough information to parse binary.
  if opts['format'] == 'binary' and missing_length(meta, opts):
    warning('Requesting CSV instead of binary because a string or isotime parameter is missing a length attribute.')
    opts['format'] = 'csv'

  # Read the data. toc0 is time to download to file or into buffer;
  # toc is time to parse.
  if opts['format'] == 'binary':
    data_result, toc0, toc = get_binary(meta, server, dataset, parameters, start, stop, opts)
  else:
    data_result, toc0, toc = get_csv(meta, server, dataset, parameters, start, stop, opts)

  # Extra metadata associated with request will be saved in
  # a pkl file with same base name as npy data file.
  meta.update({"x_server": server})
  meta.update({"x_dataset": dataset})
  meta.update({"x_parameters": parameters})
  meta.update({"x_time.min": start})
  meta.update({"x_time.max": stop})
  meta.update({"x_requestDate": datetime.now().isoformat()[0:19]})
  meta.update({"x_capabilities": caps})
  meta.update({"x_cacheDir": urld})
  meta.update({"x_downloadTime": toc0})
  meta.update({"x_readTime": toc})

  data_cache_write(data_result, meta, server, dataset, parameters, start, stop, opts)

  meta['x_totalTime'] = time.time() - tic_totalTime

  return data_result, meta


def _get_format(caps, opts):
  """Return the streaming format to use, accounting for server capabilities.

  If the requested format is not supported by the server, falls back to 'csv'.
  """

  from hapiclient.util import error

  format = opts['format']

  cformats = ['csv', 'binary']  # client formats
  if format not in cformats:
    msg = 'This client does not handle streaming format "%s". Available options: %s'
    error(msg % (format, ', '.join(cformats)))

  if format == 'csv':
    # All servers must support CSV, so no need to check capabilities.
    return format

  if "outputFormats" not in caps:
    return 'csv'

  formats = caps.get("outputFormats", [])  # Server formats
  if len(formats) == 0:
    return 'csv'

  if format not in formats:
    #from hapiclient.util import warning
    #msg = 'Requested streaming format "%s" not available from %s. Will use "csv". Available options: %s'
    #warning(msg % (format, SERVER, ', '.join(formats)))
    format = 'csv'

  if 'binary' not in formats:
    format = 'csv'

  return format


def _dt_chunk_infer(meta, opts):

  import isodate
  from datetime import datetime

  cadence = meta.get('cadence', None)

  # If cadence not given, use 1-day chunks.
  if cadence is None:
    cadence = 'PT1M'
  else:
    cadence = isodate.parse_duration(cadence)
    if isinstance(cadence, isodate.Duration):
      # When a duration does not correspond to an unambiguous
      # time duration (e.g., P1M), parse_duration returns an
      # isodate.duration.Duration object. Otherwise, it returns
      # a datetime.timedelta object.
      cadence = cadence.totimedelta(start=datetime.now())

  pt1s = isodate.parse_duration('PT1S')
  pt1h = isodate.parse_duration('PT1H')
  p1d = isodate.parse_duration('P1D')

  if cadence < pt1s:
    return 'PT1H'
  elif pt1s <= cadence <= pt1h:
    return 'P1D'
  elif cadence > pt1h:
    return 'P1M'
  elif cadence >= p1d:
    return 'P1Y'


def _get_chunks(server, dataset, parameters, start, stop, opts, tic_totalTime):

  import sys
  import time
  import isodate
  import numpy as np

  from datetime import datetime, timedelta
  from joblib import Parallel, delayed
  from hapiclient.log import log
  from hapiclient.hapitime import hapitime2datetime, hapitime_reformat

  def padz(value):
    return value if 'Z' in value else value + 'Z'

  pSTART = hapitime2datetime(padz(start))[0]
  pSTOP = hapitime2datetime(padz(stop))[0]

  if opts['dt_chunk']:
    pDELTA = isodate.parse_duration(opts['dt_chunk'])

    if opts['dt_chunk'] == 'P1Y':
      half = isodate.parse_duration('P365D') / 2
    elif opts['dt_chunk'] == 'P1M':
      half = isodate.parse_duration('P30D') / 2
    else:
      half = pDELTA / 2

    if (pSTOP - pSTART) < half:
      opts['n_chunks'] = None
      opts['dt_chunk'] = None
      return data(server, dataset, parameters, start, stop, opts)

    if opts['dt_chunk'] == 'P1Y':
      pSTART = datetime(pSTART.year, 1, 1)
      pSTOP = datetime(pSTOP.year + 1, 1, 1)
      opts['n_chunks'] = pSTOP.year - pSTART.year
    elif opts['dt_chunk'] == 'P1M':
      pSTART = datetime(pSTART.year, pSTART.month, 1)
      pSTOP = datetime(pSTOP.year, pSTOP.month + 1, 1)
      opts['n_chunks'] = (pSTOP.year - pSTART.year) * 12 + (pSTOP.month - pSTART.month)
    elif opts['dt_chunk'] == 'P1D':
      pSTART = datetime.combine(pSTART.date(), datetime.min.time())
      pSTOP = datetime.combine(pSTOP.date(), datetime.min.time()) + timedelta(days=1)
      opts['n_chunks'] = (pSTOP - pSTART).days
    elif opts['dt_chunk'] == 'PT1H':
      pSTART = datetime.combine(pSTART.date(), datetime.min.time()) + timedelta(hours=pSTART.hour)
      pSTOP = datetime.combine(pSTOP.date(), datetime.min.time()) + timedelta(hours=pSTOP.hour + 1)
      opts['n_chunks'] = int(((pSTOP - pSTART).total_seconds() / 60) / 60)
  else:
    pDIFF = pSTOP - pSTART
    pDELTA = pDIFF / opts['n_chunks']

  n_chunks = opts['n_chunks']
  opts['n_chunks'] = None
  opts['dt_chunk'] = None

  backend = 'sequential'
  if opts['parallel']:
    # Note that this does not often lead to significant speed-up.
    # Needs further testing and optimization.
    backend = 'threading'
    # multiprocessing not working.
    #backend = 'multiprocessing'
    # loky works, but not speed-up.
    #backend = 'loky'

  log('backend = {}'.format(backend))

  verbose = 0
  if opts.get('logging'):
    verbose = 100

  def nhapi(server, dataset, parameters, pSTART, pDELTA, i, **opts):
    start = pSTART + (i * pDELTA)
    start = str(start.date())+'T'+str(start.time())

    stop = pSTART + ((i + 1) * pDELTA)
    stop = str(stop.date()) + 'T' + str(stop.time())

    data_chunk, meta = data(server, dataset, parameters, start, stop, opts)
    return data_chunk, meta

  resD, resM = zip(
    *Parallel(n_jobs=opts['n_parallel'], verbose=verbose, backend=backend)(
      delayed(nhapi)(
          server,
          dataset,
          parameters,
          pSTART,
          pDELTA,
          i,
          **opts
      ) for i in range(n_chunks)
    )
  )

  resD = list(resD)

  tic_trimTime = time.time()

  start = hapitime_reformat(resD[0]['Time'][0].decode('UTF-8'), start)
  resD[0] = resD[0][resD[0]['Time'] >= bytes(start, 'UTF-8')]

  stop = hapitime_reformat(resD[-1]['Time'][0].decode('UTF-8'), stop)
  resD[-1] = resD[-1][resD[-1]['Time'] < bytes(stop, 'UTF-8')]

  trimTime = time.time() - tic_trimTime

  tic_catTime = time.time()
  data_concat = np.concatenate(resD)
  catTime = time.time() - tic_catTime

  meta = resM[0].copy()
  meta['x_time.max'] = resM[-1]['x_time.max']
  meta['x_dataFile'] = None
  meta['x_dataFiles'] = [resM[i]['x_dataFile'] for i in range(len(resM))]
  meta['x_downloadTime'] = sum([resM[i]['x_downloadTime'] for i in range(len(resM))])
  meta['x_downloadTimes'] = [resM[i]['x_downloadTime'] for i in range(len(resM))]
  meta['x_readTime'] = sum([resM[i]['x_readTime'] for i in range(len(resM))])
  meta['x_readTimes'] = [resM[i]['x_readTime'] for i in range(len(resM))]
  meta['x_trimTime'] = trimTime
  meta['x_catTime'] = catTime
  meta['x_totalTime'] = time.time() - tic_totalTime
  meta['x_dataFileParsed'] = None
  meta['x_dataFilesParsed'] = [resM[i]['x_dataFileParsed'] for i in range(len(resM))]

  return data_concat, meta
