import os
import sys
import inspect
import __main__
import traceback
import itertools
import contextlib

_main_path, _ = os.path.split(__main__.__file__)
_logs_path = os.path.join(_main_path, "logs")

_separate = False


def unique_log():
    global _separate
    _separate = True


class _QuietManager:
    def __init__(self, callback) -> None:
        self.callback = callback

    def __enter__(self):
        pass

    def __exit__(self, *_):
        self.callback()


class Log:
    _file = None

    def __init__(self, name: str = None, file = None, template: str = None) -> None:
        frame_info = inspect.getframeinfo(sys._getframe(1))

        if name is None:
            _, name = os.path.split(frame_info.filename)
            name, _ = os.path.splitext(name)

        if file is None:
            with contextlib.suppress(FileExistsError):
                os.mkdir(_logs_path)

            if not _separate:
                if self._file is not None:
                    file = self._file
                else:
                    path = os.path.join(_logs_path, ".log")
                    file = open(path, 'w')
                    self._file = file
            else:
                path = os.path.join(_logs_path, f"{name}.log")
                file = open(path, 'w')

        if template is None:
            template = "[{type_}] {file}:{line} {message}"

        self.name = name
        self.file = file
        self.template = template

        self._quiet = set()
        self._quiet_all = False

    def quiet(self, *types) -> _QuietManager:
        if not types:
            self._quiet_all = True
        else:
            self._quiet.update(map(str.upper, types))

        callback = lambda *types: self.unquiet(*types)
        return _QuietManager(callback)

    def unquiet(self, *types) -> None:
        if not types:
            self._quiet_all = False
            return self._quiet.clear()

        for type_ in map(str.upper, types):
            if type_ in self._quiet:
                self._quiet.remove(type_)

    def _raw(self, type_, *args, **kwargs):
        if self._quiet_all:
            return

        type_ = type_.upper()
        if type_ in self._quiet:
            return

        if len(args) == 0:
            message = ''
        else:
            message, *args = args
            message = message.format(*args, **kwargs)

        frame = sys._getframe(2)
        frame = inspect.getframeinfo(frame)

        path = os.path.relpath(frame.filename, _main_path)
        if path == '.':
            path = os.path.basename(frame.filename)

        message = self.template.format(name=self.name, type_=type_, file=path,
                                       line=frame.lineno, message=message)

        self.file.write(message + '\n')

    def debbug(self, *args, **kwargs) -> None:
        if len(args) == 0:
            return

        if type(args[0]) is str:
            return self._raw("DEBBUG", *args, **kwargs)

        # frame = sys._getframe(1)

        message = ''
        for arg in itertools.chain(args, kwargs.values()):
            message += f"\n| ({type(arg)}, {arg!r})"

        self._raw("DEBBUG", message)

    dbug = debbug

    def info(self, *args, **kwargs) -> None:
        self._raw("INFO", *args, **kwargs)

    def warning(self, *args, **kwargs) -> None:
        self._raw("WARNING", *args, **kwargs)

    warn = warning

    def error(self, *errors_or_message, **kwargs) -> None:
        raise NotImplementedError()

    def critical(self, *args, **kwargs) -> None:
        self._raw("CRITICAL", *args, **kwargs)

    crit = critical

    def observe(self, suppress: bool = False):
        def decorator(function):
            def wrapper(*args, **kwargs):
                try:
                    result = function(*args, **kwargs)
                except Exception as e:
                    message = f"({e.__class__.__qualname__}: {e!s})"

                    for fs in traceback.extract_tb(e.__traceback__)[1:]:
                        # The slice above is to ignore the "execution" inside
                        # the try statement code.

                        try:
                            filename = os.path.relpath(fs.filename, os.getcwd())
                        except ValueError:
                            filename = fs.filename

                        filename += ':' + str(fs.lineno)
                        message += f"\n| {filename} <- {fs.line}"

                    self._raw("ERROR", message)

                    if not suppress:
                        raise
                else:
                    message = function.__name__
                    if args:
                        message += '\n' + f"| Args\t: {args}"
                    if kwargs:
                        message += '\n' + f"| Kwargs: {kwargs}"
                    message += '\n' + f"| Return: {result}"

                    self._raw("OBSERVE", message)

                    return result
            return wrapper
        return decorator

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if self.file == sys.stdout:
            return

        self.file.close()
