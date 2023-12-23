import types
from functools import partial

from asyncgui import _current_task, _sleep_forever

from .constants import DEFAULT_PRIORITY


def _resume_task(task_step, filter, event):
    r = filter(event)
    if r:
        task_step(event)
    return r


def _accept_any(event):
    '''default filter'''
    return True


@types.coroutine
def sdl_event(partial, resume_task, subscribe, *, priority=DEFAULT_PRIORITY, filter=_accept_any):
    task = (yield _current_task)[0][0]
    sub = subscribe(partial(resume_task, task._step, filter), priority)
    try:
        return (yield _sleep_forever)[0][0]
    finally:
        sub.cancel()


sdl_event = partial(sdl_event, partial, _resume_task)


class sdl_frequent_event:
    __slots__ = ('_subscribe', '_filter', '_priority', '_sub', )

    def __init__(self, subscribe, *, filter=_accept_any, priority=DEFAULT_PRIORITY):
        self._subscribe = subscribe
        self._filter = filter
        self._priority = priority

    @staticmethod
    @types.coroutine
    def _wait_for_an_event_to_occur(_sleep_forever=_sleep_forever):
        return (yield _sleep_forever)[0][0]

    @types.coroutine
    def __aenter__(self):
        task = (yield _current_task)[0][0]
        self._sub = self._subscribe(
            partial(_resume_task, task._step, self._filter),
            self._priority,
        )
        return self._wait_for_an_event_to_occur

    async def __aexit__(self, *args):
        self._sub.cancel()
