from heapq import merge as heapq_merge
from .constants import DEFAULT_PRIORITY


class ExecutionRequest:
    __slots__ = ('_priority', 'callback', '_cancelled', )

    def __init__(self, priority, callback):
        self._priority = priority
        self.callback = callback
        self._cancelled = False

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

    def __enter__(self):
        return self

    def __exit__(self, *__):
        self._cancelled = True


class PriorityExecutor:
    '''
    Calls registered functions in the order of their priorities.

    .. code-block::

        executor = PriorityExecutor()

        values = []
        executor.register(lambda: values.append('A'), priority=2)
        executor.register(lambda: values.append('B'), priority=0)
        executor()
        assert values == ['B', 'A', ]
        values.clear()

        executor.register(lambda: values.append('C'), priority=1)
        executor()
        assert values == ['B', 'C', 'A', ]

    The :func:`asyncpygame.run` creates an instance of this class and calls its :meth:`__call__` every frame.
    '''
    __slots__ = ('_reqs', '_reqs_2', '_reqs_to_be_added', '_reqs_to_be_added_2', )

    def __init__(self):
        self._reqs: list[ExecutionRequest] = []
        self._reqs_2: list[ExecutionRequest] = []  # double buffering
        self._reqs_to_be_added: list[ExecutionRequest] = []
        self._reqs_to_be_added_2: list[ExecutionRequest] = []  # double buffering

    def __call__(self, *args):
        reqs = self._reqs
        reqs_tba = self._reqs_to_be_added
        if reqs_tba:
            reqs_tba.sort()
            req_iter = heapq_merge(reqs, reqs_tba)
            reqs_tba2 = self._reqs_to_be_added_2
            reqs_tba2.clear()
            self._reqs_to_be_added = reqs_tba2
            self._reqs_to_be_added_2 = reqs_tba
            del reqs_tba2
        else:
            req_iter = iter(reqs)
        del reqs_tba

        reqs2 = self._reqs_2
        reqs2_append = reqs2.append
        try:
            for req in req_iter:
                if req._cancelled:
                    continue
                reqs2_append(req)
                req.callback(*args)
        finally:
            reqs.clear()
            self._reqs = reqs2
            self._reqs_2 = reqs

    def register(self, func, priority=DEFAULT_PRIORITY) -> ExecutionRequest:
        req = ExecutionRequest(priority, func)
        self._reqs_to_be_added.append(req)
        return req
