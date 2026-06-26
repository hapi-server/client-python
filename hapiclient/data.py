def data(SERVER, DATASET, PARAMETERS, START, STOP, opts):

  import os
  import time
  from datetime import datetime

  from hapiclient.log import log
  from hapiclient.util import warning, subset_meta, unicode_check, fix_parameters, missing_length
  from hapiclient.cache import cachedir, data_cache_read_metax, data_cache_read_npy, data_cache_write
  from hapiclient.get import get_binary, get_csv
  from hapiclient.info import info
  from hapiclient.capabilities import get_format

  unicode_check(DATASET, PARAMETERS)
  PARAMETERS = fix_parameters(PARAMETERS)

  urld = cachedir(opts["cachedir"], SERVER)
  if opts['usecache'] or opts['cache']:
    log('cache subdirectory = %s' % urld)

  if STOP is None:
    log('STOP was given as None. Getting stopDate for dataset.')
    meta = info(SERVER, DATASET, None, opts)
    STOP = meta['stopDate']
    log(f'Using STOP = {STOP}')

  tic_totalTime = time.time()

  meta = data_cache_read_metax(SERVER, DATASET, PARAMETERS, START, STOP, opts)
  metaFromCache = meta is not None
  if not metaFromCache:
    meta = info(SERVER, DATASET, None, opts)

  # Add information to metadata so we can figure out the request needed
  # to generate it. Will also be used for labeling plots by hapiplot().
  meta.update({"x_server": SERVER})
  meta.update({"x_dataset": DATASET})

  if opts["cache"]:
    if not os.path.exists(urld):
      os.makedirs(urld)

  if opts['dt_chunk'] == 'infer':
    opts['dt_chunk'] = _dt_chunk_infer(meta, opts)

  if opts['n_chunks'] is not None or opts['dt_chunk'] is not None:
    chunk_result = _get_chunks(SERVER, DATASET, PARAMETERS, START, STOP, opts, tic_totalTime)
    if chunk_result is not None:
      return chunk_result

  if not metaFromCache:
    meta = subset_meta(meta, PARAMETERS)

  tic = time.time()
  data_cached = data_cache_read_npy(SERVER, DATASET, PARAMETERS, START, STOP, opts)
  if data_cached is not None:
    meta['x_totalTime'] = time.time() - tic_totalTime
    meta['x_readTime'] = tic - tic_totalTime
    meta['x_downloadTime'] = 0
    return data_cached, meta

  opts['format'] = get_format(SERVER, opts['format'])

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
    data_result, toc0, toc = get_binary(meta, SERVER, DATASET, PARAMETERS, START, STOP, opts)
  else:
    data_result, toc0, toc = get_csv(meta, SERVER, DATASET, PARAMETERS, START, STOP, opts)

  # Extra metadata associated with request will be saved in
  # a pkl file with same base name as npy data file.
  meta.update({"x_server": SERVER})
  meta.update({"x_dataset": DATASET})
  meta.update({"x_parameters": PARAMETERS})
  meta.update({"x_time.min": START})
  meta.update({"x_time.max": STOP})
  meta.update({"x_requestDate": datetime.now().isoformat()[0:19]})
  meta.update({"x_cacheDir": urld})
  meta.update({"x_downloadTime": toc0})
  meta.update({"x_readTime": toc})

  data_cache_write(data_result, meta, SERVER, DATASET, PARAMETERS, START, STOP, opts)

  meta['x_totalTime'] = time.time() - tic_totalTime

  return data_result, meta


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


def _get_chunks(SERVER, DATASET, PARAMETERS, START, STOP, opts, tic_totalTime):

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

  pSTART = hapitime2datetime(padz(START))[0]
  pSTOP = hapitime2datetime(padz(STOP))[0]

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
      return data(SERVER, DATASET, PARAMETERS, START, STOP, opts)

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

  def nhapi(SERVER, DATASET, PARAMETERS, pSTART, pDELTA, i, **opts):
    START = pSTART + (i * pDELTA)
    START = str(START.date())+'T'+str(START.time())

    STOP = pSTART + ((i + 1) * pDELTA)
    STOP = str(STOP.date()) + 'T' + str(STOP.time())

    data_chunk, meta = data(
        SERVER,
        DATASET,
        PARAMETERS,
        START,
        STOP,
        opts
    )
    return data_chunk, meta

  resD, resM = zip(
    *Parallel(n_jobs=opts['n_parallel'], verbose=verbose, backend=backend)(
      delayed(nhapi)(
          SERVER,
          DATASET,
          PARAMETERS,
          pSTART,
          pDELTA,
          i,
          **opts
      ) for i in range(n_chunks)
    )
  )

  resD = list(resD)

  tic_trimTime = time.time()
  if sys.version_info < (3, ):
    START = hapitime_reformat(str(resD[0]['Time'][0]), START)
    resD[0] = resD[0][resD[0]['Time'] >= START]

    STOP = hapitime_reformat(str(resD[-1]['Time'][0]), STOP)
    resD[-1] = resD[-1][resD[-1]['Time'] < STOP]
  else:
    START = hapitime_reformat(resD[0]['Time'][0].decode('UTF-8'), START)
    resD[0] = resD[0][resD[0]['Time'] >= bytes(START, 'UTF-8')]

    STOP = hapitime_reformat(resD[-1]['Time'][0].decode('UTF-8'), STOP)
    resD[-1] = resD[-1][resD[-1]['Time'] < bytes(STOP, 'UTF-8')]
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
