from hapiclient.util import log, urlopen


def servers():
  server_list = 'https://github.com/hapi-server/servers/raw/master/all.txt'

  log('Reading %s' % server_list)
  # decode('utf8') in following needed to make Python 2 and 3 types match.
  data = urlopen(server_list).read().decode('utf8').split('\n')
  data = [x for x in data if x]  # Remove empty items (if blank lines)
  # Display server URLs to console.
  log('List of HAPI servers in %s:' % server_list)
  for url in data:
      log("   %s" % url)
  return data
