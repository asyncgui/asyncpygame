from heapq import merge as heapq_merge

from pygame.surface import Surface

from .constants import DEFAULT_ZORDER


class Request:
    __slots__ = ('zorder', 'draw_func', 'cancelled', )

    def __init__(self, zorder, draw_func):
        self.zorder = zorder
        self.draw_func = draw_func
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def __eq__(self, other):
        return self.zorder == other.zorder

    def __ne__(self, other):
        return self.zorder != other.zorder

    def __lt__(self, other):
        return self.zorder < other.zorder

    def __le__(self, other):
        return self.zorder <= other.zorder

    def __gt__(self, other):
        return self.zorder > other.zorder

    def __ge__(self, other):
        return self.zorder >= other.zorder


class Drawer:
    __slots__ = ('_reqs', '_reqs_2', '_reqs_to_be_added', '_reqs_to_be_added_2', )

    def __init__(self):
        self._reqs: list[Request] = []
        self._reqs_2: list[Request] = []  # double buffering
        self._reqs_to_be_added: list[Request] = []
        self._reqs_to_be_added_2: list[Request] = []  # double buffering

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

    def add_request(self, draw_func, zorder) -> Request:
        req = Request(zorder, draw_func)
        self._reqs_to_be_added.append(req)
        return req


class DrawingRequest:
    __slots__ = ('_add_request', '_req', )

    def __init__(self, add_request, draw_func, *, zorder=DEFAULT_ZORDER, active=True):
        self._add_request = add_request
        self._req = add_request(draw_func, zorder)
        self.active = active

    @property
    def zorder(self):
        return self._req.zorder

    @zorder.setter
    def zorder(self, zorder):
        req = self._req
        if req.zorder == zorder:
            return
        if req.cancelled:
            req.zorder = zorder
        else:
            req.cancel()
            self._req = self._add_request(req.draw_func, zorder)

    @property
    def draw_func(self):
        return self._req.draw_func

    @draw_func.setter
    def draw_func(self, draw_func):
        self._req.draw_func = draw_func

    @property
    def active(self) -> bool:
        return not self._req.cancelled

    @active.setter
    def active(self, active):
        req = self._req
        if req.cancelled is (not active):
            return
        if req.cancelled:
            self._req = self._add_request(req.draw_func, req.zorder)
        else:
            req.cancel()

    def __enter__(self):
        return self

    def __exit__(self, *__):
        self.active = False
