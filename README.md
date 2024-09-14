# AsyncPygame

Let's say you want to do:

1. `print('A')`
1. wait for 1000ms to elapse
1. `print('B')`
1. wait for a mouse button to be pressed
1. `print('C')`

in that order.
The `asyncpygame` module allows you to implement that like this:

```python
async def what_you_want_to_do(*, clock, sdlevent, **kwargs):
    print('A')
    await clock.sleep(1000)
    print('B')
    e = await sdlevent.wait(MOUSEBUTTONDOWN)
    print('C')
```

[Youtube](https://youtu.be/kvy0_aVUFLM)


## Installation

Pin the minor version.

```text
poetry add asyncpygame@~0.1
pip install "asyncpygame>=0.1,<0.2"
```


## Tested on

- CPython 3.10 + pygame-ce 2.5
- CPython 3.11 + pygame-ce 2.5
- CPython 3.12 + pygame-ce 2.5

