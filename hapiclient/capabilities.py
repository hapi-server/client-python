
def capabilities(SERVER):
  """Return the capabilities of a HAPI server.

  Args:
    SERVER (str): The base URL of the HAPI server.

  Returns:
    dict: A dictionary containing the capabilities of the server.
  """
  from hapiclient.util import urlopen

  caps = urlopen(SERVER + '/capabilities', parse_json=True)

  return caps


def get_format(SERVER, format):
  """Return the transport format to use, accounting for server capabilities.

  If the requested format is not supported by the server, falls back to 'csv'
  with a warning.
  """

  from hapiclient.util import error, warning

  cformats = ['csv', 'binary']  # client formats
  if format not in cformats:
    msg = 'This client does not handle transport format "%s". Available options: %s'
    error(msg % (format, ', '.join(cformats)))

  if format != 'csv':
    caps = capabilities(SERVER)
    sformats = caps["outputFormats"]  # Server formats
    if format not in sformats:
      msg = 'Requested transport format "%s" not avaiable from %s. Will use "csv". Available options: %s'
      warning(msg % (format, SERVER, ', '.join(sformats)))
      format = 'csv'
    if 'binary' not in sformats:
      format = 'csv'

  return format
