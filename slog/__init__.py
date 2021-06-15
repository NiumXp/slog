import sys
import __main__

from ._log import Log, unique_log

__version__ = "1.0.0"

__all__ = (
    "Log",
    "unique_log",

    "debbug",
    "warning",
    "info",
    "error",
    "warn",
    "crit",

    "quiet",
    "unquiet",
)

_log = Log(name=__main__.__name__, file=sys.stdout)

quiet   = _log.quiet
unquiet = _log.unquiet

debbug      = _log.debbug
warning     = _log.warning
critical    = _log.critical
info        = _log.info
error       = _log.error
observe     = _log.observe
warn        = _log.warn
crit        = _log.crit
dbug        = _log.dbug
