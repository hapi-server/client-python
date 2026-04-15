import os
import sys
import logging
import inspect


def get_logger(name):

  caller_frame = inspect.stack()[1]
  script_path = os.path.abspath(caller_frame.filename)
  logfile = os.path.splitext(script_path)[0] + ".log"

  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)
  logger.propagate = False
  logger.handlers = []

  formatter = logging.Formatter("%(message)s")

  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

  file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  return logger
