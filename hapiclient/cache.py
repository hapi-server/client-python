def server2dirname(server):
  """Convert a server URL to a directory name."""
  import re
  urld = re.sub(r"https*://", "", server)
  urld = re.sub(r'/', '_', urld)

  return urld


def cachedir(*args):
  """HAPI cache directory.

  cachedir() returns tempfile.gettempdir() + os.path.sep + 'hapi-data'

  cachdir(basedir, server) returns basedir + os.path.sep + server2dirname(server)
  """
  import os
  import tempfile

  if len(args) == 2:
    # cachedir(base_dir, server)
    return args[0] + os.path.sep + server2dirname(args[1])
  else:
    # cachedir()
    return tempfile.gettempdir() + os.path.sep + 'hapi-data'


def request2path(*args):
    # request2path(server, dataset, parameters, start, stop)
    # request2path(server, dataset, parameters, start, stop, cachedir)
    import os
    import re

    if len(args) == 5:
        # Use default if cachedir not given.
        cachedirectory = cachedir()
    else:
        cachedirectory = args[5]

    args = list(args)

    # Replace forbidden characters in directory and filename
    # Replacements assume that there will be no name collisions,
    # e.g., one parameter named abc-< and another abc-@lt@.
    # This also introduces an incompatability between caches on Windows
    # Unix.
    import platform
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


def meta_cache_paths(SERVER, DATASET, opts):
  """Return (urld, fnamejson, fnamepkl) for metadata cache files."""
  urld = cachedir(opts["cachedir"], SERVER)
  fname_root = request2path(SERVER, DATASET, '', '', '', opts['cachedir'])
  return urld, fname_root + '.json', fname_root + '.pkl'


def meta_cache_read(SERVER, DATASET, opts):
  """Read metadata from PKL cache. Returns meta dict or None."""
  import os
  import pickle
  from hapiclient.util import log

  if not opts["usecache"]:
    log('Not checking metadata cache because usecache is False.')
    return None

  urld, _, fnamepkl = meta_cache_paths(SERVER, DATASET, opts)
  if os.path.isfile(fnamepkl):
    log('Reading %s' % fnamepkl.replace(urld + '/', ''), opts)
    with open(fnamepkl, 'rb') as f:
      return pickle.load(f)

  if opts["usecache"]:
    log('No metadata cache file found: %s' % fnamepkl.replace(urld + '/', ''), opts)

  return None


def meta_cache_write(meta, SERVER, DATASET, opts):
  """Write metadata to JSON and PKL cache files."""
  import os
  import json
  import pickle
  from hapiclient.util import log

  if not opts["cache"]:
    return

  urld, fnamejson, fnamepkl = meta_cache_paths(SERVER, DATASET, opts)
  if not os.path.exists(urld):
    os.makedirs(urld)

  log('Writing %s ' % fnamejson.replace(urld + '/', ''), opts)
  with open(fnamejson, 'w') as f:
    json.dump(meta, f, indent=4)

  log('Writing %s ' % fnamepkl.replace(urld + '/', ''), opts)
  with open(fnamepkl, 'wb') as f:
    # protocol=2 used for Python 2.7 compatibility.
    pickle.dump(meta, f, protocol=2)


def data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts):
  """Return (fnamecsv, fnamebin, fnamenpy, fnamepklx) for data cache files."""
  fname_root = request2path(SERVER, DATASET, PARAMETERS, START, STOP, opts['cachedir'])
  return fname_root + '.csv', fname_root + '.bin', fname_root + '.npy', fname_root + '.pkl'


def data_cache_read_metax(SERVER, DATASET, PARAMETERS, START, STOP, opts):
  """Read extended request metadata from PKL cache. Returns meta dict or None."""
  import os
  import pickle
  from hapiclient.util import log

  if not opts["usecache"]:
    log('Not checking data cache because usecache is False.')
    return None

  urld = cachedir(opts["cachedir"], SERVER)
  _, _, _, fnamepklx = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts)
  if os.path.isfile(fnamepklx):
    log('Reading %s' % fnamepklx.replace(urld + '/', ''), opts)
    with open(fnamepklx, 'rb') as f:
      return pickle.load(f)
  if opts["usecache"]:
    log('No data cache file found: %s' % fnamepklx.replace(urld + '/', ''), opts)

  return None


def data_cache_read_npy(SERVER, DATASET, PARAMETERS, START, STOP, opts):
  """Read cached numpy data array. Returns None if not cached."""
  import os
  import numpy as np
  from hapiclient.util import log

  if not opts["usecache"]:
    return None

  urld = cachedir(opts["cachedir"], SERVER)
  _, _, fnamenpy, _ = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts)

  if not os.path.isfile(fnamenpy):
    return None

  log('Reading %s ' % fnamenpy.replace(urld + '/', ''))
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
  from hapiclient.util import log

  urld = cachedir(opts["cachedir"], SERVER)
  fnamecsv, fnamebin, fnamenpy, fnamepklx = data_cache_paths(SERVER, DATASET, PARAMETERS, START, STOP, opts)
  _, fnamejson, fnamepkl = meta_cache_paths(SERVER, DATASET, opts)

  meta.update({"x_metaFileParsed": fnamepkl})
  meta.update({"x_dataFileParsed": fnamenpy})
  meta.update({"x_metaFile": fnamejson})
  meta.update({"x_dataFile": fnamebin if opts['format'] == 'binary' else fnamecsv})

  if not opts["cache"]:
    return
  if not os.path.exists(opts["cachedir"]):
    os.makedirs(opts["cachedir"])
  if not os.path.exists(urld):
    os.makedirs(urld)

  log('Writing %s' % fnamepklx, opts)
  with open(fnamepklx, 'wb') as f:
    pickle.dump(meta, f, protocol=2)

  log('Writing %s' % fnamenpy, opts)
  with warnings.catch_warnings():
    # Ignore warning that occurs when saving Unicode data.
    warnings.filterwarnings("ignore",
        message=r"Stored array in format 3\.0.*",
        category=UserWarning,
        module=r"numpy\.lib\.format",
    )
    np.save(fnamenpy, data_result)


def _missing_length(meta, opts):
  """Return True if any string or isotime parameter is missing length attribute in metadata."""

  """
  missing_length = True will be set if HAPI String or ISOTime
  parameter has no length attribute in metadata (length attribute is
  required for both in binary but only for primary time column in CSV).
  When missing_length=True the CSV read gets more complicated.
  """

  if opts['format'] == 'csv':
    if opts['method'] == 'numpynolength' or opts['method'] == 'pandasnolength':
      return True

  for param in meta['parameters']:
    if param['type'] in ['string', 'isotime'] and 'length' not in param:
      return True

  return False


def _compute_dt(meta, opts):
  import numpy as np

  # Compute data type variable dt used to read HAPI response into
  # a data structure.
  pnames, psizes, ptypes, dt = [], [], [], []

  # Each element of cols is an array with start/end column number of
  # parameter.
  cols = np.zeros([len(meta["parameters"]), 2], dtype=np.int32)
  ss = 0  # running sum of prod(size)

  # Extract sizes and types of parameters.
  for i in range(0, len(meta["parameters"])):
      ptype = meta["parameters"][i]["type"]

      ptypes.append(ptype)

      pnames.append(str(meta["parameters"][i]["name"]))
      if 'size' in meta["parameters"][i]:
          psizes.append(meta["parameters"][i]['size'])
      else:
          psizes.append(1)

      # For size = [N] case, readers want
      # dtype = ('name', type, N)
      # not
      # dtype = ('name', type, [N])
      if type(psizes[i]) is list and len(psizes[i]) == 1:
          psizes[i] = psizes[i][0]

      if type(psizes[i]) is list and len(psizes[i]) > 1:
          # psizes[i] = list(reversed(psizes[i]))
          psizes[i] = list(psizes[i])

      # First column of ith parameter.
      cols[i][0] = ss
      # Last column of ith parameter.
      cols[i][1] = ss + np.prod(psizes[i]) - 1
      # Running sum of columns.
      ss = cols[i][1] + 1

      # HAPI numerical formats are 64-bit LE floating point and 32-bit LE
      # signed integers.
      if ptype == 'double':
          dtype = (pnames[i], '<d', psizes[i])
      if ptype == 'integer':
          dtype = (pnames[i], np.dtype('<i4'), psizes[i])

      if ptype == 'string' or ptype == 'isotime':
          if 'length' in meta["parameters"][i]:
              # length is specified for parameter in metadata. Use it.
              if ptype == 'string':
                  dtype = (pnames[i], 'U' + str(meta["parameters"][i]["length"]), psizes[i])
              if ptype == 'isotime':
                  dtype = (pnames[i], 'S' + str(meta["parameters"][i]["length"]), psizes[i])
          else:
              # A string or isotime parameter did not have a length.
              # Will need to use slower CSV read method.
              if ptype == 'string' or ptype == 'isotime':
                  dtype = (pnames[i], object, psizes[i])

      # For testing reader. Force use of slow read method.
      if opts['format'] == 'csv':
          if opts['method'] == 'numpynolength' or opts['method'] == 'pandasnolength':
            if ptype == 'string' or ptype == 'isotime':
              dtype = (pnames[i], object, psizes[i])

      # https://numpy.org/doc/stable/release/1.17.0-notes.html#shape-1-fields-in-dtypes-won-t-be-collapsed-to-scalars-in-a-future-version
      if dtype[2] == 1:
        dtype = dtype[0:2]

      dt.append(dtype)

  return dt, cols, psizes, pnames, ptypes
