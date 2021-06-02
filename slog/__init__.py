import sys
import __main__

from ._log import Log

__version__ = "1.0.0"

__all__ = (
    "Log",
    "debbug",
    "warning",
    "info",
    "fatal",
    "quiet",
    "unquiet",
)

_log = Log(name=__main__.__name__, file=sys.stdout, save=False)

quiet = _log.quiet
unquiet = _log.unquiet
debbug = _log.debbug
warning = _log.warning
info = _log.info
fatal = _log.fatal
observe = _log.observe
