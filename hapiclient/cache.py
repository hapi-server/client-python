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


def request2path(*args):
  # request2path(server, dataset, parameters, start, stop)
  # request2path(server, dataset, parameters, start, stop, cachedir)
  import os
  import re
  import platform

  if len(args) == 5:
    # Use default if cachedir not given.
    cachedirectory = cachedir()
  else:
    cachedirectory = args[5]

  args = list(args)

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
      args[1] = re.sub(element[0], element[1], args[1])
      args[2] = re.sub(element[0], element[1], args[2])

  else:
    args[1] = re.sub('/','@forwardslash@',args[1])
    args[2] = re.sub('/','@forwardslash@',args[2])

  # To shorten filenames.
  args[3] = re.sub(r'-|:|\.|Z', '', args[3])
  args[4] = re.sub(r'-|:|\.|Z', '', args[4])

  # URL subdirectory
  urldirectory = server2dirname(args[0])
  fname = '%s_%s_%s_%s' % (args[1], args[2], args[3], args[4])

  return os.path.join(cachedirectory, urldirectory, fname)


def meta_cache_paths(SERVER, DATASET, cachedir):
  """Return dict with metadata cache directory and file names."""

  fname_root = request2path(SERVER, DATASET, '', '', '', cachedir)

  return {
    'json': fname_root + '.json',
    'pkl': fname_root + '.pkl'
  }


def meta_cache_read(SERVER, DATASET, opts):
  """Read metadata from PKL cache. Returns meta dict or None."""

  import os
  import pickle

  from hapiclient.log import log

  if not opts["usecache"]:
    log('Not checking metadata cache because usecache is False.')
    return None

  fnamepkl = meta_cache_paths(SERVER, DATASET, opts['cachedir'])['pkl']
  if os.path.isfile(fnamepkl):
    log('Reading %s' % os.path.basename(fnamepkl))
    with open(fnamepkl, 'rb') as f:
      return pickle.load(f)

  if opts["usecache"]:
    log('No metadata cache file found: %s' % os.path.basename(fnamepkl))

  return None


def meta_cache_write(meta, SERVER, DATASET, opts):
  """Write metadata to JSON and PKL cache files."""

  import os
  import json
  import pickle

  from hapiclient.log import log

  if not opts["cache"]:
    return

  paths = meta_cache_paths(SERVER, DATASET, opts['cachedir'])
  fnamejson, fnamepkl = paths['json'], paths['pkl']

  server_dir = cachedir(opts["cachedir"], SERVER)
  os.makedirs(server_dir, exist_ok=True)

  log('Writing %s ' % os.path.basename(fnamejson))
  with open(fnamejson, 'w') as f:
    json.dump(meta, f, indent=4)

  log('Writing %s ' % os.path.basename(fnamepkl))
  with open(fnamepkl, 'wb') as f:
    # protocol=2 used for Python 2.7 compatibility.
    pickle.dump(meta, f, protocol=2)


def data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, cachedir):
  """Return dict with data cache file names."""

  fname_root = request2path(SERVER, DATASET, PARAMETERS, START, STOP, cachedir)

  return {
    'csv': fname_root + '.csv',
    'bin': fname_root + '.bin',
    'npy': fname_root + '.npy',
    'pkl': fname_root + '.pkl'
  }


def data_cache_read_metax(SERVER, DATASET, PARAMETERS, START, STOP, opts):
  """Read extended request metadata from PKL cache. Returns meta dict or None."""

  import os
  import pickle

  from hapiclient.log import log

  if not opts["usecache"]:
    log('Not checking subsetted metadata cache because usecache is False.')
    return None

  fnamepklx = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts['cachedir'])['pkl']
  if os.path.isfile(fnamepklx):
    log('Reading subsetted metadata cache %s' % os.path.basename(fnamepklx))
    with open(fnamepklx, 'rb') as f:
      return pickle.load(f)
  if opts["usecache"]:
    log('No subsetted metadata cache file found: %s' % os.path.basename(fnamepklx))

  return None


def data_cache_read_npy(SERVER, DATASET, PARAMETERS, START, STOP, opts):
  """Read cached numpy data array. Returns None if not cached."""

  import os
  import numpy as np

  from hapiclient.log import log

  if not opts["usecache"]:
    return None

  fnamenpy = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts['cachedir'])['npy']

  if not os.path.isfile(fnamenpy):
    return None

  log('Reading %s ' % os.path.basename(fnamenpy))
  with open(fnamenpy, 'rb') as f:
    data = np.load(f)

  return data


def data_cache_write(data_result, meta, SERVER, DATASET, PARAMETERS, START, STOP, opts):
  """Write data array and extended metadata to cache files.

  Also updates meta with file-related x_ fields before writing.
  """

  import os
  import pickle
  import warnings
  import numpy as np

  from hapiclient.log import log

  data_paths = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts['cachedir'])
  fnamecsv, fnamebin, fnamenpy, fnamepklx = data_paths['csv'], data_paths['bin'], data_paths['npy'], data_paths['pkl']

  meta_paths = meta_cache_paths(SERVER, DATASET, opts['cachedir'])
  fnamejson, fnamepkl = meta_paths['json'], meta_paths['pkl']

  meta.update({"x_metaFileParsed": fnamepkl})
  meta.update({"x_dataFileParsed": fnamenpy})
  meta.update({"x_metaFile": fnamejson})
  meta.update({"x_dataFile": fnamebin if opts['format'] == 'binary' else fnamecsv})

  if not opts["cache"]:
    # Need to return after meta is updated.
    return

  server_dir = cachedir(opts["cachedir"], SERVER)
  os.makedirs(server_dir, exist_ok=True)

  log('Writing %s' % os.path.basename(fnamepklx))
  with open(fnamepklx, 'wb') as f:
    pickle.dump(meta, f, protocol=2)

  log('Writing %s' % os.path.basename(fnamenpy))
  with warnings.catch_warnings():
    # Ignore warning that occurs when saving Unicode data.
    kwargs = {
        'message': r"Stored array in format 3\.0.*",
        'category': UserWarning,
        'module': r"numpy\.lib\.format"
    }
    warnings.filterwarnings("ignore", **kwargs)
    np.save(fnamenpy, data_result)
