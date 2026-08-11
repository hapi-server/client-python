def catalog(SERVER, opts):

  import hapiclient as hc

  cat = hc.cache.meta_cache_read(SERVER, None, 'catalog', opts)
  if cat is not None:
    return cat

  url = SERVER + '/catalog'
  cat = hc.util.urlopen(url, parse_json=True)

  hc.cache.meta_cache_write(cat, SERVER, None, 'catalog', opts)

  return cat
