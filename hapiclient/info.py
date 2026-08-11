def info(server, dataset, parameters, opts):

  import hapiclient as hc

  hc.util.unicode_check(dataset, parameters)
  parameters = hc.util.fix_parameters(parameters)

  meta = hc.cache.meta_cache_read(server, dataset, 'info', opts)
  if meta is not None:
    return meta

  cat = hc.catalog.catalog(server, opts)
  url = server + '/info?' + hc.util.query_name(cat, 'dataset') + '=' + dataset
  meta = hc.util.urlopen(url, parse_json=True)

  hc.cache.meta_cache_write(meta, server, dataset, 'info', opts)

  meta.update({"x_server": server})
  meta.update({"x_dataset": dataset})

  if parameters is not None:
    hc.util.subset_meta(meta, parameters)
    return meta
  else:
    return meta
