
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

  If the requested format is not supported by the server, falls back to 'csv'.
  """

  from hapiclient.util import error

  cformats = ['csv', 'binary']  # client formats
  if format not in cformats:
    msg = 'This client does not handle streaming format "%s". Available options: %s'
    error(msg % (format, ', '.join(cformats)))

  if format != 'csv':
    caps = capabilities(SERVER)
    if "outputFormats" not in caps:
      return 'csv'

    formats = caps.get("outputFormats", [])  # Server formats
    if len(formats) == 0:
      return 'csv'

    if format not in formats:
      #from hapiclient.util import warning
      #msg = 'Requested streaming format "%s" not available from %s. Will use "csv". Available options: %s'
      #warning(msg % (format, SERVER, ', '.join(formats)))
      format = 'csv'

    if 'binary' not in formats:
      format = 'csv'

  return format
