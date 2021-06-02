# slog

## Sample
```python
import slog
import contextlib

@slog.observe()
def two(num: int, a):
    if num == 2:
        raise ValueError("nooooooooooo")

    return num + 2

number = int(input("Numero: "))
slog.debbug("Number: {!r}", number)

for n in range(number):
    if n == 4:
        slog.fatal("3!")
    else:
        with contextlib.suppress(ValueError):
            two(n, a=2)
```

```
Numero: 10
21/06/02 19:06:57 [DEBBUG       ] Number: 10
┌ 21/06/02 19:06:57 [OBSERVE    ] 'two' at c:/Users/Nium/Documents/pepe/main.py:5
│ Args: (0,)
│ Kwargs: {'a': 2}
└ Return: 2
┌ 21/06/02 19:06:57 [OBSERVE    ] 'two' at c:/Users/Nium/Documents/pepe/main.py:5
│ Args: (1,)
│ Kwargs: {'a': 2}
└ Return: 3
┌ 21/06/02 19:06:57 [OBSERVE    ] 'two' at c:/Users/Nium/Documents/pepe/main.py:5
│ Args: (2,)
│ Kwargs: {'a': 2}
└ Return (Raised): ValueError('nooooooooooo')
┌ 21/06/02 19:06:57 [OBSERVE    ] 'two' at c:/Users/Nium/Documents/pepe/main.py:5
│ Args: (3,)
│ Kwargs: {'a': 2}
└ Return: 5
21/06/02 19:06:57 [FATAL        ] 3!
```
