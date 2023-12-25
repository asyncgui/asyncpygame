from collections.abc import AsyncIterator
import types
from contextlib import AbstractAsyncContextManager
from collections.abc import Callable, Awaitable

from asyncgui import Cancelled, ISignal, _current_task, _sleep_forever, wait_any_cm, Task
from ._timer import TimeUnit


# These will be initialized by 'asyncpygame.init()'
schedule_once = None
schedule_interval = None


async def sleep(duration) -> Awaitable[None]:
    '''
    Waits for a specified period of time (in milli seconds).

    .. code-block::

        await sleep(1000)
    '''
    sig = ISignal()
    event = schedule_once(sig.set, duration)

    try:
        await sig.wait()
    except Cancelled:
        event.cancel()
        raise


def move_on_after(timeout) -> AbstractAsyncContextManager[Task]:
    '''
    Returns an async context manager that applies a time limit to its code block,
    like :func:`trio.move_on_after` does.

    .. code-block::

        async with move_on_after(3000) as bg_task:  # 3-second time limit
            ...

        if bg_task.finished:
            print("The code block was interrupted due to a timeout")
        else:
            print("The code block exited gracefully.")
    '''
    return wait_any_cm(sleep(timeout))


class repeat_sleeping:
    '''
    :meta private:

    An async form of :func:`asyncpygame.schedule_interval`.
    The following callback-style code:

    .. code-block::

        def callback(dt):
            print(dt)

        schedule_interval(callback, 1000)

    is equivalent to the following async/await-style code:

    .. code-block::

        async with repeat_sleeping(1000) as sleep:
            while True:
                dt = await sleep()
                print(dt)

    **Restriction**

    You are not allowed to perform any kind of async operations inside the with-block except you can
    ``await`` the return value of the function that is bound to the identifier of the as-clause.

    .. code-block::

        async with repeat_sleeping() as sleep:
            await sleep()  # OK
            await something_else  # NOT ALLOWED
            async with async_context_manager:  # NOT ALLOWED
                ...
            async for __ in async_iterator:  # NOT ALLOWED
                ...
    '''

    __slots__ = ('_interval', '_event', )

    def __init__(self, interval: TimeUnit=0):
        self._interval = interval

    @staticmethod
    @types.coroutine
    def _sleep(_f=_sleep_forever):
        return (yield _f)[0][0]

    @types.coroutine
    def __aenter__(self) -> Awaitable[Callable[[], Awaitable[TimeUnit]]]:
        task = (yield _current_task)[0][0]
        self._event = schedule_interval(task._step, self._interval)
        return self._sleep

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._event.cancel()


async def anim_with_dt(*, step=0) -> AsyncIterator[TimeUnit]:
    '''
    Repeats sleeping at specified intervals.

    .. code-block::

        async for dt in anim_with_dt(step=1000):
            print(dt)

    **Restriction**

    You are not allowed to perform any kind of async operations during the loop.

    .. code-block::

        async for dt in anim_with_dt():
            await awaitable  # NOT ALLOWED
            async with async_context_manager:  # NOT ALLOWED
                ...
            async for __ in async_iterator:  # NOT ALLOWED
                ...
    '''
    async with repeat_sleeping(step) as sleep:
        while True:
            yield await sleep()


async def anim_with_et(*, step=0) -> AsyncIterator[TimeUnit]:
    '''
    Same as :func:`anim_with_dt` except this one produces the elapsed time of the loop.

    .. code-block::

        timeout = 3000
        async for et in anim_with_et():
            ...
            if et > timeout:
                break

    You can calculate the ``et`` by yourself if you want to:

    .. code-block::

        et = 0
        timeout = 3000
        async for dt in anim_with_dt():
            et += dt
            ...
            if et > timeout:
                break

    which should be as performant as the former.

    The API is under the same restriction as :func:`anim_with_dt`'s.
    '''
    et = 0.
    async with repeat_sleeping(step) as sleep:
        while True:
            et += await sleep()
            yield et


async def anim_with_dt_et(*, step=0) -> AsyncIterator[tuple[TimeUnit, TimeUnit]]:
    '''
    :func:`anim_with_dt` and :func:`anim_with_et` combined.

    .. code-block::

        timeout = ...
        async for dt, et in anim_with_dt_et():
            ...
            if et > timeout:
                break

    The API is under the same restriction as :func:`anim_with_dt`'s.
    '''
    et = 0.
    async with repeat_sleeping(step) as sleep:
        while True:
            dt = await sleep()
            et += dt
            yield dt, et


async def anim_with_ratio(*, duration=1000, step=0) -> AsyncIterator[float]:
    '''
    Same as :func:`anim_with_et` except this one produces the progression ratio of the loop.

    .. code-block::

        async for p in anim_with_ratio(duration=3000):
            print(p * 100, "%")

    The API is under the same restriction as :func:`anim_with_dt`'s.
    '''
    et = 0.
    async with repeat_sleeping(step) as sleep:
        while et < duration:
            et += await sleep()
            yield et / duration


async def anim_with_dt_et_ratio(*, duration=1000, step=0) -> AsyncIterator[tuple[TimeUnit, TimeUnit, float]]:
    '''
    :func:`anim_with_dt`, :func:`anim_with_et` and :func:`anim_with_ratio` combined

    .. code-block::

        async for dt, et, p in anim_with_dt_et_ratio(duration=3000):
            ...

    The API is under the same restriction as :func:`anim_with_dt`'s.
    '''
    et = 0.
    async with repeat_sleeping(step) as sleep:
        while et < duration:
            dt = await sleep()
            et += dt
            yield dt, et, et / duration
