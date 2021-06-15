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


def unique_log() -> None:
    """Makes all logs share the same file."""
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
    """
    Note
    ----
    The logs are saved in the `logs` folder in the main file path.

    You can use the instances of this class as a context manager, like
    `open` function.

    ```python
    with Log() as log:
        log.info("Example!")
    ```

    Attributes
    ----------
    name : Optional[str]
        The name of log. If not given, the name of file where the
        instance was created is used.
    file : Optional[SupportsWrite]
        The file that log will write into. If not given, it creates one
        file named `{name}.log`.
    template : Optional[str]
        The template to output messages to. You can use `type_`, `file`,
        `line`, `message` and `name`.
    """
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

    def quiet(self, *types: str) -> _QuietManager:
        """Quiet `types`. If `types` is not given, all logs will be
        silenced.

        This function returns a context manager that calls `unquiet`.
        ```python
        slog.debbug("Hey!")  # Will be written.

        with slog.quiet("debbug"):
            slog.debbug("Hello?")  # Will not be written 
        ```"""
        if not types:
            self._quiet_all = True
        else:
            self._quiet.update(map(str.upper, types))

        callback = lambda *types: self.unquiet(*types)
        return _QuietManager(callback)

    def unquiet(self, *types: str) -> None:
        """Unquiet `types`. If `types` is not given, all logs are heard
        again."""
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
        """Makes a `DEBBUG` log.

        If the first item of `args` is a str, you can use ther others
        `args` and `kwargs` to format it.
        ```python
        # Will transform the string to `I see you, NiumXp!`
        slog.debbug("I see you, {}!", "NiumXp")
        slog.debbug("I see you, {name}!", name="NiumXp")
        ```
        Otherwise, `args` and `kwargs` are writen using
        `(<type>, <repr>)`.
        ```python
        slog.debbug(1, True, [])
        # (<class 'int'>, 1)
        # (<class 'bool'>, True)
        # (<class 'list'>, [])
        ```"""
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

    def info(self, message: str, *args, **kwargs) -> None:
        """Makes an `INFO` log.

        You can use `args` and `kwargs` to format the `message`.
        ```python
        # Will transform the string to `Hello, NiumXp!`
        slog.info("Hello, {}!", "NiumXp")
        slog.info("Hello, {name}!", name="NiumXp")
        ```"""
        self._raw("INFO", message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Makes a `WARNING` log.

        You can use `args` and `kwargs` to format the `message`.
        ```python
        # Will transform the string to `Take care, NiumXp!`
        slog.warning("Take care, {}!", "NiumXp")
        slog.warning("Take care, {name}!", name="NiumXp")
        ```"""
        self._raw("WARNING", message, *args, **kwargs)

    warn = warning

    def error(self, *errors_or_message, **kwargs) -> None:
        raise NotImplementedError()

    def critical(self, message: str, *args, **kwargs) -> None:
        """Makes a `CRITICAL` log.

        You can use `args` and `kwargs` to format the `message`.
        ```python
        # Will transform the string to `Run, NiumXp!`
        slog.critical("Run, {}!", "NiumXp")
        slog.critical("Run, {name}!", name="NiumXp")
        ```"""
        self._raw("CRITICAL", *args, **kwargs)

    crit = critical

    def observe(self, suppress: bool = False):
        """The decorator to observe a function when it's called and
        raises an error.

        When the error is logged, the error is raised again, you can
        `suppress` it.
        """
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
