import logging as _logging

_logger = _logging.getLogger("hapiclient")

_INTERNAL_HANDLER_ATTR = "_hapiclient_internal_handler"
_INTERNAL_LEVEL_ATTR = "_hapiclient_internal_level"

# Per Python library best practices, add a NullHandler and leave propagation
# enabled so the application controls output. When running under pytest,
# disable propagation to prevent hapiclient INFO messages from leaking into
# pytest's captured log output.
import sys as _sys
_logger.addHandler(_logging.NullHandler())
_logger.propagate = "pytest" not in _sys.modules
del _sys


def configure_logging(logging):
    """Configure the hapiclient logger based on opts['logging'].

    If the hapiclient logger has been configured externally (level != NOTSET
    or handlers present) and logging=False, the logging kwarg is ignored.
    """
    has_user_level = _logger.level != _logging.NOTSET and \
                     _logger.level != getattr(_logger, _INTERNAL_LEVEL_ATTR, None)
    has_user_handlers = any(
        not getattr(handler, _INTERNAL_HANDLER_ATTR, False)
        for handler in _logger.handlers
    ) or bool(_logging.root.handlers)

    if logging is True:
        _logger.setLevel(_logging.INFO)
        setattr(_logger, _INTERNAL_LEVEL_ATTR, _logging.INFO)
        _logger.propagate = False  # use our own handler when logging=True
        _has_internal = any(getattr(h, _INTERNAL_HANDLER_ATTR, False) for h in _logger.handlers)
        if not _has_internal:
            import sys
            _handler = _logging.StreamHandler(sys.stdout)
            _handler.setFormatter(_logging.Formatter("%(message)s"))
            setattr(_handler, _INTERNAL_HANDLER_ATTR, True)
            _logger.addHandler(_handler)

    if logging is False:
        if has_user_level or has_user_handlers:
            _logger.propagate = True  # ensure messages reach the user-configured handler
            #from .util import warning
            if has_user_handlers:
                pass
                #warning("Ignoring logging=False because standard Python logger for 'hapiclient' already configured with handlers.")
            else:
                pass
                #warning("Ignoring logging=False because standard Python logger for 'hapiclient' already configured with log_level != NOTSET.")
        else:
            _logger.setLevel(_logging.WARNING)
            setattr(_logger, _INTERNAL_LEVEL_ATTR, _logging.WARNING)


def log(msg, opts=None):
    """Log message using the 'hapiclient' logger.
    """

    # opts is not used but kept for backward compatibility
    import sys

    pre = sys._getframe(1).f_code.co_name + '(): '
    _logger.info("hapiclient." + pre + msg)
