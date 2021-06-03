import io
import os
import __main__
import datetime
import contextlib

_empty = object()

BREAK_LINE = '\n'
OPEN_MULTLINE_CHAR = "┌ "
PREFIX_MULTILINE_CHAR = "│ "
CLOSE_MULTILINE_CHAR = "└ "
PREFIX_LINE_CHAR = ''


class Log:
    save_path = os.path.dirname(__main__.__file__) + "/logs"

    def __init__(self,
                 name: str,
                 file=None, *,
                 template: str=None,
                 format_: str=None,
                 ignore_if_closed: bool=False,
                 save: bool=True
    ) -> None:
        if file is None:
            if save:
                with contextlib.suppress(FileExistsError):
                    os.makedirs(self.save_path)

                file = open(os.path.join(self.save_path, name + ".txt"), 'w')
            else:
                file = io.StringIO()

        if template is None:
            template = "{} [{}\t] {}"

        if format_ is None:
            format_ = "%y/%m/%d %H:%M:%S"

        self.name = name
        self.file = file
        self.template = template
        self.format_ = format_
        self.ignore_if_closed = ignore_if_closed
        self.save = save

        self._quiet = False

    def _raw_write(self, s) -> None:
        if self._quiet:
            return

        if self.file.closed and self.ignore_if_closed:
            return

        print(s, file=self.file)

    def _write(self, p, s, v=_empty):
        d = datetime.datetime.now()
        d = d.strftime(self.format_)

        if v is not _empty:
            s = s.format(*v)

        s = self.template.format(d, p, s)

        if BREAK_LINE in s:
            s = s.split(BREAK_LINE)

            s[0] = OPEN_MULTLINE_CHAR + s[0]
            for i in range(1, len(s)):
                s[i] = PREFIX_MULTILINE_CHAR + s[i]
            s[-1] = CLOSE_MULTILINE_CHAR + s[-1][len(PREFIX_MULTILINE_CHAR):]

            s = BREAK_LINE.join(s)
        else:
            s = PREFIX_LINE_CHAR + s

        self._raw_write(s)

    def quiet(self) -> None:
        self._quiet = True

        # TODO Context manager? :D

    def unquiet(self) -> None:
        self._quiet = False

    def info(self, message, *v) -> None:
        self._write("INFO", message, v)

    def warning(self, message, *v) -> None:
        self._write("WARNING", message, v)

    def debbug(self, message, *v) -> None:
        self._write("DEBBUG", message, v)

    def fatal(self, message, *v) -> None:
        self._write("FATAL", message, v)
        exit(0)

    def observe(self, args: bool=True, kwargs: bool=True, return_: bool=True):
        def decorator(func):
            def wrapper(*wa, **wk):
                c = func.__code__
                s = f"{func.__qualname__!r} at {c.co_filename}:{c.co_firstlineno+1}"

                if args is True and wa != ():
                    s += '\n' + "Args: " + str(wa)

                if kwargs is True and wk != {}:
                    s += '\n' + "Kwargs: " + str(wk)

                error = False
                try:
                    result = func(*wa, **wk)
                except Exception as e:
                    m = e
                    error = e
                else:
                    m = result

                if return_:
                    m = repr(m)

                    if error:
                        m = "Return (Raised): " + m
                    else:
                        m = "Return: " + m

                    s += '\n' + m

                self._write("OBSERVE", s)

                if error:
                    raise error

                return result

            return wrapper

        return decorator
