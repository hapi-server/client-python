import logging as _logging

_logger = _logging.getLogger("hapiclient")

_INTERNAL_HANDLER_ATTR = "_hapiclient_internal_handler"
_INTERNAL_LEVEL_ATTR = "_hapiclient_internal_level"

# Disable propagation and add NullHandler by default so hapiclient
# is silent unless explicitly configured by user. This is the standard
# practice for library loggers.
_logger.propagate = False
_logger.setLevel(_logging.NOTSET)
if not _logger.handlers:
    _null_handler = _logging.NullHandler()
    setattr(_null_handler, _INTERNAL_HANDLER_ATTR, True)
    _logger.addHandler(_null_handler)


def configure_logging(opts):
    """Configure the hapiclient logger based on opts['logging'].

    If the hapiclient logger has been configured externally (level != NOTSET
    or handlers present), the logging kwarg.
    """
    has_user_level = _logger.level != _logging.NOTSET and \
                     _logger.level != getattr(_logger, _INTERNAL_LEVEL_ATTR, None)
    has_user_handlers = any(
        not getattr(handler, _INTERNAL_HANDLER_ATTR, False)
        for handler in _logger.handlers
    )

    if opts['logging']:
        _logger.setLevel(_logging.INFO)
        setattr(_logger, _INTERNAL_LEVEL_ATTR, _logging.INFO)
        _logger.propagate = False
        if not _logger.handlers:
            import sys
            _handler = _logging.StreamHandler(sys.stdout)
            _handler.setFormatter(_logging.Formatter("%(message)s"))
            setattr(_handler, _INTERNAL_HANDLER_ATTR, True)
            _logger.addHandler(_handler)
    else:
        if has_user_level or has_user_handlers:
            # Don't log when logging is disabled - would cause output during tests
            pass
        else:
            _logger.setLevel(_logging.NOTSET)
            setattr(_logger, _INTERNAL_LEVEL_ATTR, _logging.NOTSET)


def log(msg, opts=None):
    """Log message using the 'hapiclient' logger.
    """

    # opts is not used but kept for backward compatibility
    import sys

    pre = sys._getframe(1).f_code.co_name + '(): '
    _logger.info("hapiclient." + pre + msg)
