import os
import sys
import logging
import inspect


def get_logger(name):

  if name == '__main__':
    log_level = logging.INFO
  else:
    # Under pytest, use NOTSET so pytest's --log-level controls output.
    log_level = logging.NOTSET

  caller_frame = inspect.stack()[1]
  script_path = os.path.abspath(caller_frame.filename)
  logfile = os.path.splitext(script_path)[0] + ".log"

  logger = logging.getLogger(name)
  logger.setLevel(log_level)
  logger.propagate = False
  logger.handlers = []
  effective_log_level = logger.getEffectiveLevel()

  formatter = logging.Formatter("%(message)s")

  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

  if effective_log_level >= logging.INFO:
    file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

  return logger
