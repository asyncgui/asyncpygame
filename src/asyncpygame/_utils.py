__all__ = (
    'capture_current_frame', 'block_input_events',
)

from typing import Awaitable, ContextManager
from asyncgui import ExclusiveEvent
from pygame.surface import Surface

from .constants import INPUT_EVENTS
from ._priority_executor import PriorityExecutor
from ._sdlevent import SDLEvent, Subscriber


async def capture_current_frame(executor: PriorityExecutor, priority, source: Surface) -> Awaitable[Surface]:
    '''
    .. code-block::

        surface = await capture_current_frame(executor, priority, source)
    '''
    e = ExclusiveEvent()
    with executor.register(e.fire, priority):
        await e.wait()

    return source.copy()


def block_input_events(sdlevent: SDLEvent, priority) -> ContextManager[Subscriber]:
    '''
    Returns a context manager that blocks input events.

    .. code-block::

        with block_input_events(sdlevent, priority):
            ...

    .. warning::

        The context manager starts having the effect when it is created, not when its ``__enter__()`` method is
        called.
    '''
    return sdlevent.subscribe(INPUT_EVENTS, lambda e: True, priority)
