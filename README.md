# slog
A simple Python log library easy to use.

## Install
```
python -m pip install -U git+https://github.com/NiumXp/slog
```

## Sample
You can find more examples [here](/examples).

```python
import slog


def error(message):
    raise Exception(message)


@slog.observe(suppress=True)
def greeting(user: str):
    return error("Hello " + user + '!')


name = input("Name: ")
slog.debbug("User typed '{}'", name)

greeting(name)
```

Expected output:
```
[DEBBUG] observe.py:14 User typed 'NiumXp'
[ERROR] observe.py:16 (Exception: Hello NiumXp!)
| observe.py:10 <- return error("Hello " + user + '!')
| observe.py:5 <- raise Exception(message)
```
