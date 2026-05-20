import logging as _logging

_logger = _logging.getLogger("hapiclient")

_INTERNAL_HANDLER_ATTR = "_hapiclient_internal_handler"
_INTERNAL_LEVEL_ATTR = "_hapiclient_internal_level"


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
            if has_user_handlers:
                log("Ignoring logging=%s because standard Python logger for 'hapiclient' already configured with handlers." % opts['logging'])
            else:
                log("Ignoring logging=%s because standard Python logger for 'hapiclient' already configured with log_level != NOTSET." % opts['logging'])
        else:
            _logger.setLevel(_logging.WARNING)
            setattr(_logger, _INTERNAL_LEVEL_ATTR, _logging.WARNING)


def log(msg):
    """Log message using the 'hapiclient' logger."""

    import sys

    pre = sys._getframe(1).f_code.co_name + '(): '

    _logger.info("hapiclient." + pre + msg)
