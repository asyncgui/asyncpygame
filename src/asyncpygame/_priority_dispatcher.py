from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from heapq import merge as heapq_merge
import types
from functools import partial

from asyncgui import _current_task, _sleep_forever

from .constants import DEFAULT_PRIORITY, STOP_DISPATCHING


def _resume_task(task_step, filter, event):
    r = filter(event)
    if r:
        task_step(event)
    return r


def _accept_any(event):
    '''default filter'''
    return True


@dataclass(slots=True)
class Subscriber:
    _priority: int

    callback: Callable
    '''
    The callback function registered using the :meth:`PriorityDispatcher.add_subscriber` call that returned this
    instance. You can replace it with another one by simply assigning to this attribute.

    .. code-block::

        sub = priority_dispatcher.add_subscriber(...)
        sub.callback = another_function
    '''

    _cancelled: bool = False

    def cancel(self):
        self._cancelled = True

    def __eq__(self, other):
        return self._priority == other._priority

    def __ne__(self, other):
        return self._priority != other._priority

    def __lt__(self, other):
        return self._priority > other._priority

    def __le__(self, other):
        return self._priority >= other._priority

    def __gt__(self, other):
        return self._priority < other._priority

    def __ge__(self, other):
        return self._priority <= other._priority


class PriorityDispatcher:
    '''
    An observer pattern implementation with priority support.

    .. code-block::

        d = PriorityDispatcher()
        values = []

        # Add subscribers with the same priority.
        sub1 = d.add_subscriber(values.append, priority=0)
        sub2 = d.add_subscriber(lambda v: values.append(v.lower()), priority=0)

        # Because the priorities of 'sub1' and 'sub2' are the same, we cannot predict which one will be called first.
        d.dispatch("A")
        assert set(values) == {"A", "a", }
        d.dispatch("B")
        assert set(values[2:]) == {"B", "b", }

        # The higher the priority of a subscriber is, the earlier its callback function will be called.
        d.add_subscriber(lambda v: values.append(v + v), priority=1)
        d.dispatch("C")
        assert values[4] == "CC"
        assert set(values[5:]) == {"C", "c", }

    To unsubscribe:

    .. code-block::

        sub = d.add_subscriber(...)
        sub.cancel()
    '''
    __slots__ = ('_subs', '_subs_2', '_subs_to_be_added', '_subs_to_be_added_2', )

    def __init__(self):
        self._subs: list[Subscriber] = []
        self._subs_2: list[Subscriber] = []  # double buffering
        self._subs_to_be_added: list[Subscriber] = []
        self._subs_to_be_added_2: list[Subscriber] = []  # double buffering

    def dispatch(self, *args):
        subs = self._subs
        subs_tba = self._subs_to_be_added
        if subs_tba:
            subs_tba.sort()
            sub_iter = heapq_merge(subs, subs_tba)
            subs_tba2 = self._subs_to_be_added_2
            subs_tba2.clear()
            self._subs_to_be_added = subs_tba2
            self._subs_to_be_added_2 = subs_tba
            del subs_tba2
        else:
            sub_iter = iter(subs)
        del subs_tba

        STOP_DISPATCHING_ = STOP_DISPATCHING
        subs2 = self._subs_2
        subs2_append = subs2.append
        try:
            for sub in sub_iter:
                if sub._cancelled:
                    continue
                subs2_append(sub)
                if sub.callback(*args) is STOP_DISPATCHING_:
                    subs2.extend(sub_iter)
                    return
        finally:
            subs.clear()
            self._subs = subs2
            self._subs_2 = subs

    def add_subscriber(self, func, priority=DEFAULT_PRIORITY) -> Subscriber:
        sub = Subscriber(priority, func)
        self._subs_to_be_added.append(sub)
        return sub

    @types.coroutine
    def wait(self, *, priority=DEFAULT_PRIORITY, filter=_accept_any) -> Awaitable:
        '''
        Waits for anything to be dispatched (by default).

        .. code-block::

            async def async_fn():
                obj = await d.wait()
                assert obj == 'Hello'

            d = PriorityDispatcher()
            asyncpygame.start(async_fn())
            d.dispatch('Hello')

        You probably want to wait for something specific in most cases, which can be achieved by the ``filter``
        parameter.

        .. code-block::

            async def async_fn():
                e = await d.wait(filter=lambda e: e.type == pygame.FINGERDOWN)
                print(e.x, e.y)
        '''
        task = (yield _current_task)[0][0]
        sub = self.add_subscriber(partial(_resume_task, task._step, filter), priority)
        try:
            return (yield _sleep_forever)[0][0]
        finally:
            sub.cancel()

    def repeat_waiting(self, *, priority=DEFAULT_PRIORITY, filter=_accept_any) \
            -> AbstractAsyncContextManager[Callable[[], Awaitable]]:
        '''
        Returns an async context manager that provides an efficient way to repeat waiting.

        .. code-block::

            async with repeat_waiting() as wait_anything:
                while True:
                    obj = await wait_anything()
                    print(obj)

        **Restriction**

        You are not allowed to perform any kind of async operations inside the with-block except the one in the
        as-clause.

        .. code-block::

            async with repeat_waiting() as wait_anything:
                await wait_anything()  # OK
                await something_else  # NOT ALLOWED
                async with async_context_manager:  # NOT ALLOWED
                    ...
                async for __ in async_iterator:  # NOT ALLOWED
                    ...
        '''
        return _repeat_waiting(self, filter, priority)


class _repeat_waiting:
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
