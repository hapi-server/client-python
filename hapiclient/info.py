def info(SERVER, DATASET, PARAMETERS, opts):

  from hapiclient.util import urlopen, subset, unicode_check, fix_parameters, query_name
  from hapiclient.cache import meta_cache_read, meta_cache_write
  from hapiclient.catalog import catalog

  unicode_check(DATASET, PARAMETERS)
  PARAMETERS = fix_parameters(PARAMETERS)

  meta = meta_cache_read(SERVER, DATASET, opts)
  if meta is not None:
      return meta

  cat = catalog(SERVER)
  url = SERVER + '/info?' + query_name(cat, 'dataset') + '=' + DATASET
  meta = urlopen(url, parse_json=True)

  meta_cache_write(meta, SERVER, DATASET, opts)

  meta.update({"x_server": SERVER})
  meta.update({"x_dataset": DATASET})

  if PARAMETERS is not None:
    return subset(meta, PARAMETERS)
  else:
    return meta
