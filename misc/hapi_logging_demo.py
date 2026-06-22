import logging

from hapiclient import hapi

server     = 'http://hapi-server.org/servers/TestData2.0/hapi'
dataset    = 'dataset1'
parameters = 'scalar'
start      = '1970-01-01T00:00:00'
stop       = '1970-01-01T00:01:00'


def reset_hapiclient_logging():
  logger = logging.getLogger("hapiclient")
  for handler in list(logger.handlers):
    logger.removeHandler(handler)
    handler.close()
  logger.setLevel(logging.NOTSET)
  logger.propagate = False
  if hasattr(logger, "_hapiclient_internal_level"):
    delattr(logger, "_hapiclient_internal_level")


for method in range(1, 7):

  reset_hapiclient_logging()

  print(80*"-")
  print("Method {}: ".format(method))
  print(80*"-")

  # 1. Log to console using logging keyword (legacy)
  if 1 <= method <= 3:
    if method == 1:
      # No logging kwarg, so no logging
      data, meta = hapi(server, dataset, parameters, start, stop)
    if method == 2:
      # Use internal logging because logging=True and no standard logging handlers defined
      data, meta = hapi(server, dataset, parameters, start, stop, logging=True)
    if method == 3:
      # No logging because logging=False and no standard logging handlers defined
      data, meta = hapi(server, dataset, parameters, start, stop, logging=False)

  # 2. Log to console using Python's standard logging module
  if 4 <= method <= 6:
    import logging
    logger = logging.getLogger("hapiclient")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
    formatter.default_msec_format = '%s.%03d'
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if method == 4:
      # Use standard logging because defined
      data, meta = hapi(server, dataset, parameters, start, stop)
    if method == 5:
      # Use standard logging because defined
      data, meta = hapi(server, dataset, parameters, start, stop, logging=True)
    if method == 6:
      # Warning because standard logging defined but logging=False
      data, meta = hapi(server, dataset, parameters, start, stop, logging=False)

  print(80*"-" + "\n")
