import types
from typing import TypeAlias, TypeVar
from contextlib import AbstractAsyncContextManager
from collections.abc import Callable, Awaitable
from dataclasses import dataclass

from asyncgui import Cancelled, ISignal, _current_task, _sleep_forever, wait_any_cm, Task


TimeUnit = TypeVar("TimeUnit")
TimerCallback: TypeAlias = Callable[[TimeUnit], None]


@dataclass(slots=True)
class TimerEvent:
    _deadline: TimeUnit
    _last_tick: TimeUnit
    callback: TimerCallback
    '''
    The callback function registered using the ``schedule_xxx()`` call that returned this instance.
    You can replace it with another one by simply assigning to this attribute.

    .. code-block::

        event = schedule_xxx(...)
        event.callback = another_function
    '''

    _interval: TimeUnit | None
    _cancelled: bool = False

    def cancel(self):
        self._cancelled = True


class Timer:
    '''
    The Timer class allows you to schedule a function call in the future; once or repeatedly at specified intervals.
    You can get the time elapsed between the scheduling and the calling of the callback via the ``dt`` argument:

    .. code-block::

        # 'dt' means delta-time
        def my_callback(dt):
            pass

        timer = Timer()

        # call my_callback every 100 milli seconds
        timer.schedule_interval(my_callback, 100)

        # call my_callback in 100 milli seconds
        timer.schedule_once(my_callback, 100)

        # call my_callback in the next frame
        timer.schedule_once(my_callback)

    To unschedule:

    .. code-block::

        event = timer.schedule_interval(...)
        event.cancel()

    .. note::

        * Unlike PyGame's USEREVENT, you don't have to worry about running out of event IDs.
        * This class is heavily inspired by :external:kivy:doc:`kivy.clock.Clock <api-kivy.clock>`.
    '''
    __slots__ = ('_cur_time', '_events', '_events_to_be_added', )

    def __init__(self):
        self._cur_time = 0
        self._events: list[TimerEvent] = []
        self._events_to_be_added: list[TimerEvent] = []  # double buffering

    @property
    def current_time(self) -> TimeUnit:
        return self._cur_time

    def progress(self, delta_time):
        '''
        You need to constantly provide the delta-time for each iteration of the main loop for a Timer instance to work.

        .. code-block::

            timer = Timer()

            # the main loop
            running = True
            while running:
                ...
                dt = clock.tick(fps)
                timer.progress(dt)
        '''
        self._cur_time += delta_time
        cur_time = self._cur_time

        events = self._events
        events_tba = self._events_to_be_added
        tba_append = events_tba.append
        if events_tba:
            events.extend(events_tba)
            events_tba.clear()
        for e in events:
            if e._cancelled:
                continue
            if e._deadline > cur_time:
                tba_append(e)
                continue
            e.callback(cur_time - e._last_tick)
            if e._interval is None:
                continue
            e._deadline += e._interval
            e._last_tick = cur_time
            tba_append(e)
        events.clear()
        # swap
        self._events = events_tba
        self._events_to_be_added = events

    def schedule_once(self, func, delay=0) -> TimerEvent:
        '''
        Schedules the ``func`` to be called in ``delay`` milli seconds.

        :param delay: If 0, the ``func`` will be called in the next frame.
        '''
        cur_time = self._cur_time
        event = TimerEvent(cur_time + delay, cur_time, func, None)
        self._events_to_be_added.append(event)
        return event

    def schedule_interval(self, func, interval) -> TimerEvent:
        '''
        Schedules the ``func`` to be called every ``interval`` milli seconds.

        :param interval: If 0, the ``func`` will be called every frame.
        '''
        cur_time = self._cur_time
        event = TimerEvent(cur_time + interval, cur_time, func, interval)
        self._events_to_be_added.append(event)
        return event


async def sleep(timer, duration) -> Awaitable:
    sig = ISignal()
    event = timer.schedule_once(sig.set, duration)

    try:
        await sig.wait()
    except Cancelled:
        event.cancel()
        raise


def move_on_after(timer, timeout) -> AbstractAsyncContextManager[Task]:
    return wait_any_cm(sleep(timer, timeout))


class repeat_sleeping:
    '''
    :meta private:

    An async form of :meth:`asyncpygame._api_impl.timer.Timer.schedule_interval`.
    The following callback-style code:

    .. code-block::

        def callback(dt):
            print(dt)

        timer.schedule_interval(callback, 1000)

    is equivalent to the following async/await-style code:

    .. code-block::

        async with repeat_sleeping(timer, interval=1000) as sleep:
            while True:
                dt = await sleep()
                print(dt)

    **Restriction**

    You are not allowed to perform any kind of async operations inside the with-block except you can
    ``await`` the return value of the function that is bound to the identifier of the as-clause.

    .. code-block::

        async with repeat_sleeping(timer) as sleep:
            await sleep()  # OK
            await something_else  # NOT ALLOWED
            async with async_context_manager:  # NOT ALLOWED
                ...
            async for __ in async_iterator:  # NOT ALLOWED
                ...
    '''

    __slots__ = ('_timer', '_interval', '_event', )

    def __init__(self, timer: Timer, *, interval=0):
        self._timer = timer
        self._interval = interval

    @staticmethod
    @types.coroutine
    def _sleep(_f=_sleep_forever):
        return (yield _f)[0][0]

    @types.coroutine
    def __aenter__(self) -> Awaitable[Callable[[], Awaitable[TimeUnit]]]:
        task = (yield _current_task)[0][0]
        self._event = self._timer.schedule_interval(task._step, self._interval)
        return self._sleep

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._event.cancel()
