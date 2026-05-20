from hapiclient.log import log
from hapiclient.util import urlopen


def catalog(SERVER):
  # TODO: Cache
  url = SERVER + '/catalog'
  meta = urlopen(url, parse_json=True)

  return meta
