from typing import TypeAlias
from collections.abc import Awaitable, AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager
from concurrent.futures import ThreadPoolExecutor

from asyncgui import Task
from pygame.event import Event
from pygame.surface import Surface

from ._api_impl.timer import TimeUnit
from ._api_impl.constants import DEFAULT_PRIORITY, DEFAULT_ZORDER
from ._api_impl.sdl_event import _accept_any


EventFilter: TypeAlias = Callable[[Event], bool]
EventFilterPro: TypeAlias = Callable[[Event], tuple[bool, bool]]
DrawFunc: TypeAlias = Callable[[Surface], None]


def sleep(duration: TimeUnit) -> Awaitable[None]:
    '''
    Waits for a specified period of time (in milli seconds).

    .. code-block::

        await sleep(1000)
    '''


def move_on_after(timeout: TimeUnit) -> AbstractAsyncContextManager[Task]:
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


def anim_with_dt(*, step: TimeUnit=0) -> AsyncIterator[TimeUnit]:
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


def anim_with_et(*, step: TimeUnit=0) -> AsyncIterator[TimeUnit]:
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


def anim_with_dt_et(*, step: TimeUnit=0) -> AsyncIterator[tuple[TimeUnit, TimeUnit]]:
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


def anim_with_ratio(*, duration: TimeUnit=1000, step: TimeUnit=0) -> AsyncIterator[float]:
    '''
    Same as :func:`anim_with_et` except this one produces the progression ratio of the loop.

    .. code-block::

        async for p in anim_with_ratio(duration=3000):
            print(p * 100, "%")

    The API is under the same restriction as :func:`anim_with_dt`'s.
    '''


def anim_with_dt_et_ratio(*, duration: TimeUnit=1000, step: TimeUnit=0) \
        -> AsyncIterator[tuple[TimeUnit, TimeUnit, float]]:
    '''
    :func:`anim_with_dt`, :func:`anim_with_et` and :func:`anim_with_ratio` combined

    .. code-block::

        async for dt, et, p in anim_with_dt_et_ratio(duration=3000):
            ...

    The API is under the same restriction as :func:`anim_with_dt`'s.
    '''


def run_in_thread(func, *, daemon=None, polling_interval: TimeUnit=2000) -> Awaitable:
    '''
    Creates a new thread, runs a function within it, then waits for the completion of that function.

    .. code-block::

        return_value = await run_in_thread(func)
    '''


def run_in_executor(executer: ThreadPoolExecutor, func, *, polling_interval: TimeUnit=2000) -> Awaitable:
    '''
    Runs a function within a :class:`concurrent.futures.ThreadPoolExecutor` instance, and waits for the completion of
    the function.

    .. code-block::

        executor = ThreadPoolExecutor()
        ...
        return_value = await run_in_executor(executor, func)
    '''


def sdl_event(*, priority=DEFAULT_PRIORITY, filter: EventFilter=_accept_any) -> Awaitable[Event]:
    '''
    Waits for a SDL event to occur.

    .. code-block::

        e = await sdl_event()
        print(f"A {pygame.event.event_name(e.type)} event occurred.")

    You probably want to wait for an event of specific type(s).

    .. code-block::

        e = await sdl_event(filter=lambda e: e.type == pygame.FINGERDOWN)
        print("A FINGERDOWN event occurred")
    '''


def sdl_frequent_event(*, priority=DEFAULT_PRIORITY, filter: EventFilter=_accept_any) -> \
        AbstractAsyncContextManager[Callable[[], Awaitable[Event]]]:
    '''
    Returns an async context manager that provides an efficient way to repeat waiting for a SDL event to occur.

    .. code-block::

        async with sdl_frequent_event() as any_event:
            while True:
                e = await any_event()
                print(f"A {pygame.event.event_name(e.type)} event occurred.")

    This API is designed to handle SDL events that may frequently occur, such as ``MOUSEMOTION`` or ``FINGERMOTION``:

    .. code-block::

        def filter(event, allowed_list=(MOUSEMOTION, MOUSEBUTTONUP)):
            return event.type in allowed_list

        async with sdl_frequent_event(filter=filter) as mouse_event:
            while True:
                e = await mouse_event()
                if e.type == MOUSEBUTTONUP:
                    break
                print(f"The mouse cursor moved to ({e.x}, {e.y}).")

    **Restriction**

    You are not allowed to perform any kind of async operations inside the with-block except the one in the as-clause.

    .. code-block::

        async with sdl_frequent_event() as any_event:
            await any_event()  # OK
            await something_else  # NOT ALLOWED
            async with async_context_manager:  # NOT ALLOWED
                ...
            async for __ in async_iterator:  # NOT ALLOWED
                ...
    '''


class DrawingRequest:
    '''
    画面に何か表示したい時に用いるクラス。
    このクラスの意義は ``zorder`` による順番を考慮した描画にあります。
    そのような機能が要らないのであれば特に使う必要はありません。

    .. code-block::

        def draw(draw_target: Surface):
            ...

        req = DrawingRequest(draw, zorder=200)

    ``active`` は勿論 ``zorder`` と ``draw_func`` も後からいつでも変更可です。

    .. code-block::

        req.zorder = 100
        req.draw_func = another_func
        req.active = False

    またwith文にも利用でき、withブロックを抜ける時に自動で ``active`` が偽になります。

    .. code-block::

        with DrawingRequest(draw_func, zorder=200):
            ...
    '''

    def __init__(self, draw_func: DrawFunc, /, *, zorder=DEFAULT_ZORDER, active=True):
        ...

    @property
    def zorder(self) -> int:
        '''
        描画順。この値が小さい者ほど先に描画を行う。値が同じ者同士の順は未定義。
        '''

    @property
    def draw_func(self) -> DrawFunc:
        '''
        実際に描画を行う関数。
        '''

    @property
    def active(self) -> bool:
        '''
        描画を行うか否か。描画させたくない時だけでなくインスタンスが要らなくなった時にもこれを偽にしてください。
        '''


def fade_transition(surface: Surface, *, duration: TimeUnit=1000) -> AbstractAsyncContextManager[None]:
    '''
    Fades-out the ``surface``, excutes the with-block, fades-in the ``surface``.

    .. code-block::

        async with fade_transition(surface):
            # modify surface
    '''
