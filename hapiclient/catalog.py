from hapiclient.util import log, urlopen, jsonparse


def catalog(SERVER):
  # TODO: Cache
  url = SERVER + '/catalog'
  log('Reading %s' % url)
  res = urlopen(url)
  meta = jsonparse(res, url)

  return meta
