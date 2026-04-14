def get_logger(name, log_level=None):

  if name == '__main__':
    # Command line execution of script containing caller outside of a function.
    if log_level is None:
      log_level = "INFO"
  else:
    # Caller was executed using pytest. This allows pytest's --log-level
    # option to control the log level of this logger. In this case, `name``
    # will be the base name of the calling script.
    log_level="NOTSET"

  import os
  import sys
  import logging
  import inspect

  caller_frame = inspect.stack()[1]
  script_path = os.path.abspath(caller_frame.filename)
  base, _ = os.path.splitext(script_path)
  logfile = base + ".log"

  logger = logging.getLogger(name)
  logger.setLevel(log_level)
  logger.handlers = []
  logger.propagate = False

  formatter = logging.Formatter("%(message)s")

  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setFormatter(formatter)

  logger.addHandler(stream_handler)

  if logging.getLevelName(log_level) >= logging.INFO:
    file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

  return logger

