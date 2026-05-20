from hapiclient.util import log, urlopen


def catalog(SERVER):
  # TODO: Cache
  url = SERVER + '/catalog'
  meta = urlopen(url, parse_json=True)

  return meta
