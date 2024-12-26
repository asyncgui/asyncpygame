import types
from collections.abc import Awaitable, Callable, Container
from dataclasses import dataclass
from heapq import merge as heapq_merge
from functools import partial
from contextlib import asynccontextmanager

from pygame.event import Event
from asyncgui import _current_task, _sleep_forever, current_task


def _callback(filter, consume, task_step, event: Event):
    if filter(event):
        task_step(event)
        return consume


def _accept_any(event: Event):
    '''default filter'''
    return True


def _do_nothing(event: Event):
    pass


@dataclass(slots=True)
class Subscriber:
    '''
    :meta exclude:
    '''

    _priority: int

    callback: Callable
    '''
    The callback function registered using the :meth:`SDLEvent.subscribe` call that returned this instance.
    You can replace it with another one by simply assigning to this attribute.

    .. code-block::

        sub = sdl_event.subscribe(...)
        sub.callback = another_function
    '''

    topics: Container = None
    '''
    The types of :class:`pygame.event.Event` that the subscriber is interested in.
    You can change it by simply assigning to this attribute.

    .. code-block::

        sub = sdl_event.subscribe(...)
        sub.topics = (FINGERMOTION, FINGERUP, )
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

    def __enter__(self):
        return self

    def __exit__(self, *__):
        self._cancelled = True


class SDLEvent:
    '''
    .. code-block::

        # Waits for any mouse button to be pressed.
        e = await sdlevent.wait(MOUSEBUTTONDOWN)

        # Waits for any mouse button to be pressed or released.
        e = await sdlevent.wait(MOUSEBUTTONDOWN, MOUSEBUTTONUP)

        # Waits for the left mouse button to be pressed.
        e = await sdlevent.wait(MOUSEBUTTONDOWN, filter=lambda e: e.button == 1)

    .. note::

        ``priority`` 引数は ``PriorityExecutor`` の物とは逆に働きます。すなわち大きい値で ``wait()`` しているタスクほと早く再開します。
    '''

    def __init__(self):
        self._subs: list[Subscriber] = []
        self._subs_2: list[Subscriber] = []  # double buffering
        self._subs_to_be_added: list[Subscriber] = []
        self._subs_to_be_added_2: list[Subscriber] = []  # double buffering

    def dispatch(self, event: Event):
        '''
        イベントの発生を待っているタスクにイベントを通知する。
        :func:`asyncpygame.run` のみがこれを呼ぶべきでありアプリ側からは呼ぶべきではない。
        '''
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

        subs2 = self._subs_2
        subs2_append = subs2.append
        event_type = event.type
        try:
            for sub in sub_iter:
                if sub._cancelled:
                    continue
                subs2_append(sub)
                if event_type in sub.topics and sub.callback(event):
                    subs2.extend(sub_iter)
                    return
        finally:
            subs.clear()
            self._subs = subs2
            self._subs_2 = subs

    def subscribe(self, topics, callback, priority) -> Subscriber:
        '''
        async型APIの礎となっているコールバック型API。直接触るべきではない。
        '''
        sub = Subscriber(priority, callback, topics)
        self._subs_to_be_added.append(sub)
        return sub

    @types.coroutine
    def wait(self, *event_types, filter=_accept_any, priority, consume=False) -> Awaitable[Event]:
        '''
        Waits for any of the specified types of events to occur.
        '''
        task = (yield _current_task)[0][0]
        sub = self.subscribe(event_types, partial(_callback, filter, consume, task._step), priority)
        try:
            return (yield _sleep_forever)[0][0]
        finally:
            sub.cancel()

    @asynccontextmanager
    async def wait_freq(self, *event_types, filter=_accept_any, priority, consume=False):
        '''
        ``MOUSEMOTION`` や ``FINGERMOTION`` などの頻りに起こりうるイベントを効率良く捌けるかもしれない機能。
        以下のようなコードは

        .. code-block::

            while True:
                e = await sdlevent.wait(FINGERMOTION)
                ...

        以下のように書き換える事で効率が良くなるかもしれません。

        .. code-block::

            async with sdlevent.wait_freq(FINGERMOTION) as finger_motion:
                while True:
                    e = await finger_motion()
                    ...

        ただ代償としてコードが読みにくくなるうえ逆に効率が悪くなる可能性すらあるので人間が感知できる程の改善がみられない限りは使用を控えてください。
        また多くの状況では ``FINGERUP`` が起きた時にループを抜けたいでしょうから典型的な用例は以下のようになります。

        .. code-block::

            async with (
                asyncpygame.move_on_when(sdlevent.wait(FINGERUP)),
                sdlevent.wait_freq(FINGERMOTION) as finger_motion,
            ):
                while True:
                    e = await finger_motion()
                    ...

        注意点としてas節で得た関数(上のコードでいう ``finger_motion``)は必ずそのwithブロック内で直に用いるようにしてください。
        以下の様に別の関数に渡したり、戻り値を別の関数に渡してはいけません。

        .. code-block::

            async with sdlevent.wait_freq(FINGERMOTION) as finger_motion:
                another_func(finger_motion)  # NOT ALLOWED
                another_func(finger_motion())   # NOT ALLOWED
        '''
        callback = partial(_callback, filter, consume, (await current_task())._step)
        sub = self.subscribe(event_types, _do_nothing, priority)
        try:
            yield partial(self._wait_freq, callback, sub)
        finally:
            sub.cancel()

    @types.coroutine
    def _wait_freq(_sleep_forever, _do_nothing, callback, sub):
        try:
            sub.callback = callback
            return (yield _sleep_forever)[0][0]
        finally:
            sub.callback = _do_nothing
    _wait_freq = partial(_wait_freq, _sleep_forever, _do_nothing)
