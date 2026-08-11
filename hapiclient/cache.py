def server2dirname(server):
  """Convert a server URL to a directory name."""

  import re

  urld = re.sub(r"https*://", "", server)
  urld = re.sub(r'/', '_', urld)

  return urld


def cachedir(*args):
  """HAPI cache directory.

  cachedir() returns os.path.join(tempfile.gettempdir(), 'hapi-data')

  cachedir(basedir, server) returns os.path.join(basedir, server2dirname(server))
  """

  import os
  import tempfile

  if len(args) != 0 and len(args) != 2:
    raise ValueError('cachedir() takes either 0 or 2 arguments.')

  if len(args) == 0:
    # cachedir()
    return os.path.join(tempfile.gettempdir(), 'hapi-data')

  if len(args) == 2:
    # cachedir(base_dir, server)
    return os.path.join(args[0], server2dirname(args[1]))


def request2path(server, dataset=None, parameters=None, start=None, stop=None, cache_dir=None, endpoint=None):

  import os
  import re
  import platform

  if cache_dir is None:
    # Use default if cache_dir not given.
    cachedirectory = cachedir()
  else:
    cachedirectory = cache_dir

  args = [server, dataset, parameters, start, stop]

  # Replace forbidden characters in directory and filename
  # Replacements assume that there will be no name collisions,
  # e.g., one parameter named abc-< and another abc-@lt@.
  # This also introduces an incompatibility between caches on Windows
  # Unix.
  if platform.system() == 'Windows':
    # List and code from responses in
    # https://stackoverflow.com/q/1976007
    reps = (
              ('<', '@lt@'),
              ('>', '@gt@'),
              (':', '@colon@'),
              ('"', '@doublequote@'),
              ('/', '@forwardslash@'),
              ('/', '@backslash@'),
              ('\\|', '@pipe@'),
              ('\\?', '@questionmark@'),
              ('\\*', '@asterisk@')
          )

    for element in reps:
      if dataset is not None:
        dataset = re.sub(element[0], element[1], dataset)
      if parameters is not None:
        parameters = re.sub(element[0], element[1], parameters)

  else:
    if dataset is not None:
      dataset = re.sub('/','@forwardslash@', dataset)
    if parameters is not None:
      parameters = re.sub('/','@forwardslash@', parameters)

  # To shorten filenames.
  if start is not None:
    start = re.sub(r'-|:|\.|Z', '', start)
  if stop is not None:
    stop = re.sub(r'-|:|\.|Z', '', stop)

  # URL subdirectory
  urldirectory = server2dirname(args[0])

  if not dataset and not endpoint:
    raise ValueError('Either dataset or endpoint must be specified.')

  if endpoint is None:
    endpoint = ''

  if dataset is None:
    fname = endpoint
  else:
    fname = dataset
    if parameters is not None:
      fname += '_' + parameters
    if start is not None:
      fname += '_' + start
    if stop is not None:
      fname += '_' + stop

  return os.path.join(cachedirectory, urldirectory, endpoint, fname)


def meta_cache_paths(server, dataset, endpoint, cache_dir):
  """Return dict with metadata cache directory and file names."""

  fname_root = request2path(server, dataset, cache_dir=cache_dir, endpoint=endpoint)

  return {
    'json': fname_root + '.json',
    'pkl': fname_root + '.pkl'
  }


def meta_cache_read(server, dataset, endpoint, opts):
  """Read metadata from PKL cache. Returns meta dict or None."""

  import os
  import pickle

  from hapiclient.log import log

  if not opts["usecache"]:
    if endpoint in ['', 'info']:
      log(f'Not checking metadata cache for /info?dataset={dataset} response because usecache is False.')
    else:
      log(f'Not checking metadata cache for /{endpoint} response because usecache is False.')
    return None

  fnamepkl = meta_cache_paths(server, dataset, endpoint, opts['cachedir'])['pkl']
  if os.path.isfile(fnamepkl):
    log('Reading %s' % os.path.basename(fnamepkl))
    with open(fnamepkl, 'rb') as f:
      return pickle.load(f)

  if opts["usecache"]:
    log('No metadata cache file found: %s' % os.path.basename(fnamepkl))

  return None


def meta_cache_write(meta, server, dataset, endpoint, opts):
  """Write metadata to JSON and PKL cache files."""

  import os

  from hapiclient.log import log
  from hapiclient.util import write_atomic

  if not opts["cache"]:
    return

  paths = meta_cache_paths(server, dataset, endpoint, opts['cachedir'])
  fnamejson, fnamepkl = paths['json'], paths['pkl']

  log('Writing %s ' % os.path.basename(fnamejson))
  write_atomic(fnamejson, meta)

  log('Writing %s ' % os.path.basename(fnamepkl))
  write_atomic(fnamepkl, meta)


def data_cache_paths(server, dataset, parameters, start, stop, cache_dir):
  """Return dict with data cache file names."""

  fname_root = request2path(server, dataset, parameters, start, stop, cache_dir, 'data')

  return {
    'csv': fname_root + '.csv',
    'bin': fname_root + '.bin',
    'npy': fname_root + '.npy',
    'pkl': fname_root + '.pkl'
  }


def data_cache_read_metax(server, dataset, parameters, start, stop, opts):
  """Read extended request metadata from PKL cache. Returns meta dict or None."""

  import os
  import pickle

  from hapiclient.log import log

  if not opts["usecache"]:
    log('Not checking subsetted metadata cache because usecache is False.')
    return None

  fnamepklx = data_cache_paths(server, dataset, parameters, start, stop, opts['cachedir'])['pkl']
  if os.path.isfile(fnamepklx):
    log('Reading subsetted metadata cache %s' % os.path.basename(fnamepklx))
    with open(fnamepklx, 'rb') as f:
      return pickle.load(f)
  if opts["usecache"]:
    log('No subsetted metadata cache file found: %s' % os.path.basename(fnamepklx))

  return None


def data_cache_read_npy(server, dataset, parameters, start, stop, opts):
  """Read cached numpy data array. Returns None if not cached."""

  import os
  import numpy as np

  from hapiclient.log import log

  if not opts["usecache"]:
    return None

  fnamenpy = data_cache_paths(server, dataset, parameters, start, stop, opts['cachedir'])['npy']

  if not os.path.isfile(fnamenpy):
    return None

  log('Reading %s ' % os.path.basename(fnamenpy))
  with open(fnamenpy, 'rb') as f:
    data = np.load(f)

  return data


def data_cache_write(data_result, meta, server, dataset, parameters, start, stop, opts):
  """Write data array and extended metadata to cache files.

  Also updates meta with file-related x_ fields before writing.
  """

  import os

  from hapiclient.log import log
  from hapiclient.util import write_atomic

  data_paths = data_cache_paths(server, dataset, parameters, start, stop, opts['cachedir'])
  fnamecsv, fnamebin, fnamenpy, fnamepklx = data_paths['csv'], data_paths['bin'], data_paths['npy'], data_paths['pkl']

  meta_paths = meta_cache_paths(server, dataset, 'info', opts['cachedir'])
  fnamejson, fnamepkl = meta_paths['json'], meta_paths['pkl']

  meta.update({"x_metaFileParsed": fnamepkl})
  meta.update({"x_dataFileParsed": fnamenpy})
  meta.update({"x_metaFile": fnamejson})
  meta.update({"x_dataFile": fnamebin if opts['format'] == 'binary' else fnamecsv})

  if not opts["cache"]:
    # Need to return after meta is updated.
    return

  log('Writing %s' % os.path.basename(fnamepklx))
  write_atomic(fnamepklx, meta)

  log('Writing %s' % os.path.basename(fnamenpy))
  write_atomic(fnamenpy, data_result)
