
def capabilities(SERVER, opts):
  """Return the /capabilities response from a HAPI server.

  Args:
    SERVER (str): The base URL of the HAPI server.

  Returns:
    dict: A dictionary containing the capabilities of the server.
  """

  import hapiclient as hc

  caps = hc.cache.meta_cache_read(SERVER, None, 'capabilities', opts)
  if caps is not None:
    return caps

  caps = hc.util.urlopen(SERVER + '/capabilities', parse_json=True)

  hc.cache.meta_cache_write(caps, SERVER, None, 'capabilities', opts)

  return caps
