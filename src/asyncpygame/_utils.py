__all__ = (
    'capture_current_frame', 'block_inputs',
)

from typing import Awaitable, ContextManager
from asyncgui import ExclusiveEvent
from pygame.surface import Surface

from .constants import INPUT_EVENTS
from ._priority_executor import PriorityExecutor
from ._sdlevent import SDLEvent, Subscriber


async def capture_current_frame(source: Surface, priority, executor: PriorityExecutor, **unused) -> Awaitable[Surface]:
    '''
    .. code-block::

        surface = await capture_current_frame(screen, priority, executor)
    '''
    e = ExclusiveEvent()
    with executor.register(e.fire, priority):
        await e.wait()

    return source.copy()


def block_inputs(priority, sdlevent: SDLEvent, **unused) -> ContextManager[Subscriber]:
    '''
    Returns a context manager that blocks input events.

    .. code-block::

        with block_inputs(priority, sdlevent):
            ...

    .. warning::

        The context manager starts having the effect when it is created, not when its ``__enter__()`` method is
        called.
    '''
    return sdlevent.subscribe(INPUT_EVENTS, lambda e: True, priority)
