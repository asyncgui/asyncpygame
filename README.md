# AsyncPygame

```python
import asyncpygame as ap

# Waits for a 1 second
await ap.sleep(1000)

# Waits for a mouse button to be pressed
event = await ap.sdl_event(filter=lambda event: event.type == MOUSEBUTTONDOWN)
```

(This library is not at a level where it can be used in a production environment.)

## Tested on

- CPython 3.10 + pygame-ce 2.3.2
- CPython 3.11 + pygame-ce 2.3.2
