__all__ = ('PriorityDrawer', 'GraphicalEntity', )

from typing import TypeAlias
from collections.abc import Callable
from heapq import merge as heapq_merge

from pygame.surface import Surface

from .constants import DEFAULT_PRIORITY


DrawFunc: TypeAlias = Callable[[Surface], None]


class DrawingRequest:
    __slots__ = ('priority', 'draw_func', 'cancelled', )

    def __init__(self, priority, draw_func):
        self.priority = priority
        self.draw_func = draw_func
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def __eq__(self, other):
        return self.priority == other.priority

    def __ne__(self, other):
        return self.priority != other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __le__(self, other):
        return self.priority <= other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __ge__(self, other):
        return self.priority >= other.priority


class PriorityDrawer:
    '''
    A drawing system with priority support.

    .. code-block::

        class Sprite(GraphicalEntity):
            ...

        drawer = PriorityDrawer()
        sprite1 = Sprite(drawer, priority=0)
        sprite2 = Sprite(drawer, priority=2)

        # The *lower* the priority of a :class:`GraphicalEntity` is, the earlier it will be drawed.
        drawer.draw(screen)
    '''
    __slots__ = ('_reqs', '_reqs_2', '_reqs_to_be_added', '_reqs_to_be_added_2', )

    def __init__(self):
        self._reqs: list[DrawingRequest] = []
        self._reqs_2: list[DrawingRequest] = []  # double buffering
        self._reqs_to_be_added: list[DrawingRequest] = []
        self._reqs_to_be_added_2: list[DrawingRequest] = []  # double buffering

    def draw(self, draw_target: Surface):
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
                if req.cancelled:
                    continue
                reqs2_append(req)
                req.draw_func(draw_target)
        finally:
            reqs.clear()
            self._reqs = reqs2
            self._reqs_2 = reqs

    def add_request(self, draw_func, priority, DrawingRequest=DrawingRequest) -> DrawingRequest:
        req = DrawingRequest(priority, draw_func)
        self._reqs_to_be_added.append(req)
        return req


class GraphicalEntity:
    def __init__(self, drawer: PriorityDrawer, *, draw_func=None, priority=DEFAULT_PRIORITY, visible=True):
        self.__add_request = drawer.add_request
        self.__req = drawer.add_request(self.draw if draw_func is None else draw_func, priority)
        self.visible = visible

    def draw(self, draw_target: Surface):
        raise NotImplementedError

    @property
    def priority(self) -> int:
        '''
        描画順。この値が小さい者ほど先に描画を行う。値が同じ者同士の順は未定義。
        '''
        return self.__req.priority

    @priority.setter
    def priority(self, priority: int):
        req = self.__req
        if req.priority == priority:
            return
        if req.cancelled:
            req.priority = priority
        else:
            req.cancel()
            self.__req = self.__add_request(req.draw_func, priority)

    @property
    def draw_func(self) -> DrawFunc:
        '''
        描画を行う関数で既定値は :meth:`draw` 。このプロパティに別の関数を代入することで何時でも差し替える事が可能。
        '''
        return self.__req.draw_func

    @draw_func.setter
    def draw_func(self, draw_func: DrawFunc):
        self.__req.draw_func = draw_func

    @property
    def visible(self) -> bool:
        '''
        描画を行うか否か。描画させたくない時だけでなくインスタンスが要らなくなった時にもこれを偽にしてください。
        '''
        return not self.__req.cancelled

    @visible.setter
    def visible(self, visible: bool):
        req = self.__req
        if req.cancelled is (not visible):
            return
        if req.cancelled:
            self.__req = self.__add_request(req.draw_func, req.priority)
        else:
            req.cancel()
