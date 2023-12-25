from collections.abc import Callable
from dataclasses import dataclass
from heapq import merge as heapq_merge


from .constants import DEFAULT_PRIORITY, STOP_DISPATCHING


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
        return self._priority < other._priority

    def __le__(self, other):
        return self._priority <= other._priority

    def __gt__(self, other):
        return self._priority > other._priority

    def __ge__(self, other):
        return self._priority >= other._priority


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

        # The higher the priority, the earlier a callback will be called.
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
            subs_tba.sort(reverse=True)
            sub_iter = heapq_merge(subs, subs_tba, reverse=True)
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
