from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
import types
from functools import partial

from pygame.event import Event
from asyncgui import _current_task, _sleep_forever

from .constants import DEFAULT_PRIORITY
from ._priority_dispatcher import PriorityDispatcher


def _resume_task(task_step, filter, event):
    r = filter(event)
    if r:
        task_step(event)
    return r


def _accept_any(event):
    '''default filter'''
    return True


class SDLEventDispatcher(PriorityDispatcher):

    @types.coroutine
    def wait_sdl_event(self, *, priority=DEFAULT_PRIORITY, filter=_accept_any) -> Awaitable[Event]:
        '''
        Waits for a SDL event to occur.

        .. code-block::

            e = await wait_sdl_event()
            print(f"A {pygame.event.event_name(e.type)} event occurred.")

        You probably want to wait for an event of specific type(s).

        .. code-block::

            e = await wait_sdl_event(filter=lambda e: e.type == pygame.FINGERDOWN)
            print("A FINGERDOWN event occurred")
        '''
        task = (yield _current_task)[0][0]
        sub = self.add_subscriber(partial(_resume_task, task._step, filter), priority)
        try:
            return (yield _sleep_forever)[0][0]
        finally:
            sub.cancel()

    def wait_sdl_event_repeatedly(self, *, priority=DEFAULT_PRIORITY, filter=_accept_any) \
            -> AbstractAsyncContextManager[Callable[[], Awaitable[Event]]]:
        '''
        Returns an async context manager that provides an efficient way to repeat waiting for a SDL event to occur.

        .. code-block::

            async with wait_sdl_event_repeatedly() as wait_any_event:
                while True:
                    e = await wait_any_event()
                    print(f"A {pygame.event.event_name(e.type)} event occurred.")

        This API is designed to handle SDL events that may frequently occur, such as ``MOUSEMOTION`` or
        ``FINGERMOTION``:

        .. code-block::

            def filter(event, allowed_list=(MOUSEMOTION, MOUSEBUTTONUP)):
                return event.type in allowed_list

            async with wait_sdl_event_repeatedly(filter=filter) as wait_mouse_event:
                while True:
                    e = await wait_mouse_event()
                    if e.type == MOUSEBUTTONUP:
                        break
                    print(f"The mouse cursor moved to ({e.x}, {e.y}).")

        **Restriction**

        You are not allowed to perform any kind of async operations inside the with-block except the one in the
        as-clause.

        .. code-block::

            async with wait_sdl_event_repeatedly() as wait_any_event:
                await wait_any_event()  # OK
                await something_else  # NOT ALLOWED
                async with async_context_manager:  # NOT ALLOWED
                    ...
                async for __ in async_iterator:  # NOT ALLOWED
                    ...
        '''
        return _wait_sdl_event_repeatedly(self, filter, priority)


class _wait_sdl_event_repeatedly:
    __slots__ = ('dispatcher', 'filter', 'priority', 'sub', )

    def __init__(self, dispatcher, filter, priority):
        self.dispatcher = dispatcher
        self.filter = filter
        self.priority = priority

    @staticmethod
    @types.coroutine
    def _wait_for_an_event_to_occur(_sleep_forever=_sleep_forever):
        return (yield _sleep_forever)[0][0]

    @types.coroutine
    def __aenter__(self):
        task = (yield _current_task)[0][0]
        self.sub = self.dispatcher.add_subscriber(
            partial(_resume_task, task._step, self.filter),
            self.priority,
        )
        return self._wait_for_an_event_to_occur

    async def __aexit__(self, *args):
        self.sub.cancel()
