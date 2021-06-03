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
    "save_path"
)

_log = Log(name=__main__.__name__, file=sys.stdout)

quiet = _log.quiet
unquiet = _log.unquiet
debbug = _log.debbug
warning = _log.warning
info = _log.info
fatal = _log.fatal
observe = _log.observe

@property
def save_path():
    return _log.save_at

@save_path.setter
def save_path(x):
    _log.save_path = x
