from hapiclient import hapi

server     = 'http://hapi-server.org/servers/TestData2.0/hapi'
dataset    = 'dataset1'
parameters = 'scalar'
start      = '1970-01-01T00:00:00'
stop       = '1970-01-01T00:01:00'

method = 3

# 1. Log to console using logging keyword (legacy)
if method == 1:
  data, meta = hapi(server, dataset, parameters, start, stop, logging=True)

# 2. Log to console using Python's standard logging module
if method == 2:
  import logging
  logger = logging.getLogger("hapiclient")
  logger.setLevel(logging.INFO)
  handler = logging.StreamHandler()
  formatter = logging.Formatter("%(asctime)s [%(name)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
  formatter.default_msec_format = '%s.%03d'
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  data, meta = hapi(server, dataset, parameters, start, stop)

# 3. Log to a file using Python's standard logging module
if method == 3:
  import logging
  logger = logging.getLogger("hapiclient")
  logger.setLevel(logging.INFO)
  handler = logging.FileHandler("hapi_logging_demo.log")
  formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
  formatter.default_msec_format = '%s.%03d'
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  data, meta = hapi(server, dataset, parameters, start, stop)

  # Note that logging keyword is ignored when using Python's standard logging module.
  data, meta = hapi(server, dataset, parameters, start, stop, logging=False)
