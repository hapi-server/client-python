import io
import logging

from hapiclient.hapi import hapi

server     = 'http://hapi-server.org/servers/TestData2.0/hapi'
dataset    = 'dataset1'
parameters = 'scalar'
start      = '1970-01-01T00:00:00'
stop       = '1970-01-01T00:01:00'

def _reset_logger():
  """Remove all handlers and reset level on the hapiclient logger."""
  logger = logging.getLogger("hapiclient")
  logger.handlers.clear()
  logger.setLevel(logging.NOTSET)


class TestLoggingKeywordTrue:
  """Method 1: logging=True logs to console."""

  def setup_method(self):
    _reset_logger()

  def teardown_method(self):
    _reset_logger()

  def test_logs_to_stderr(self, capsys):
    data, meta = hapi(server, dataset, parameters, start, stop, logging=True)
    captured = capsys.readouterr()
    assert 'Running hapi.py version' in captured.err

  def test_adds_stream_handler(self):
    data, meta = hapi(server, dataset, parameters, start, stop, logging=True)
    logger = logging.getLogger("hapiclient")
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

  def test_sets_info_level(self):
    data, meta = hapi(server, dataset, parameters, start, stop, logging=True)
    logger = logging.getLogger("hapiclient")
    assert logger.level == logging.INFO


class TestLoggingKeywordFileObject:
  """Method 2: logging=file_object writes to a file-like object."""

  def setup_method(self):
    _reset_logger()

  def teardown_method(self):
    _reset_logger()

  def test_logs_to_file_object(self):
    buf = io.StringIO()
    data, meta = hapi(server, dataset, parameters, start, stop, logging=buf)
    output = buf.getvalue()
    assert 'Running hapi.py version' in output

  def test_logs_to_real_file(self, tmp_path):
    logfile = tmp_path / "hapiclient.log"
    with open(logfile, "w") as f:
      data, meta = hapi(server, dataset, parameters, start, stop, logging=f)
    content = logfile.read_text()
    assert 'Running hapi.py version' in content


class TestStandardLoggingConsole:
  """Method 3: Standard logging with StreamHandler."""

  def setup_method(self):
    _reset_logger()

  def teardown_method(self):
    _reset_logger()

  def test_logs_to_stream(self):
    buf = io.StringIO()
    logger = logging.getLogger("hapiclient")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(buf)
    logger.addHandler(handler)

    data, meta = hapi(server, dataset, parameters, start, stop)
    output = buf.getvalue()
    assert 'Running hapi.py version' in output

  def test_logging_false_ignored_when_externally_configured(self):
    """logging=False should be ignored when logger is already configured."""
    buf = io.StringIO()
    logger = logging.getLogger("hapiclient")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(buf)
    logger.addHandler(handler)

    data, meta = hapi(server, dataset, parameters, start, stop, logging=False)
    output = buf.getvalue()
    assert 'Running hapi.py version' in output


class TestStandardLoggingFile:
  """Method 4: Standard logging with FileHandler."""

  def setup_method(self):
    _reset_logger()

  def teardown_method(self):
    _reset_logger()

  def test_logs_to_file(self, tmp_path):
    logfile = tmp_path / "hapiclient.log"
    logger = logging.getLogger("hapiclient")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(str(logfile))
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)

    data, meta = hapi(server, dataset, parameters, start, stop)
    handler.close()

    content = logfile.read_text()
    assert 'Running hapi.py version' in content


class TestLoggingKeywordFalse:
  """Default: logging=False suppresses INFO messages."""

  def setup_method(self):
    _reset_logger()

  def teardown_method(self):
    _reset_logger()

  def test_no_info_output(self, capsys):
    data, meta = hapi(server, dataset, parameters, start, stop, logging=False)
    captured = capsys.readouterr()
    assert 'Running hapi.py version' not in captured.err
    assert 'Running hapi.py version' not in captured.out


if __name__ == "__main__":
    import pytest
    #pytest.main([__file__])
    pytest.main([__file__ + "::TestLoggingKeywordFalse", "-v"])
    pytest.main([__file__ + "::TestLoggingKeywordTrue", "-v"])
    pytest.main([__file__ + "::TestLoggingKeywordFileObject", "-v"])
    pytest.main([__file__ + "::TestStandardLoggingConsole", "-v"])
    pytest.main([__file__ + "::TestStandardLoggingFile", "-v"])