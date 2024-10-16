__all__ = ('progress_spinner', )

from typing import Self
import math
import itertools
from functools import partial

import pygame
from pygame import Color, Rect


class Arc:
    __slots__ = ('draw', 'start_angle', 'stop_angle', )

    def __init__(self, draw_target, color, rect, start_angle, stop_angle, line_width):
        self.draw = partial(self._draw, draw_target, color, rect, line_width, self)
        self.start_angle = start_angle
        self.stop_angle = stop_angle

    def _draw(pygame_draw_arc, draw_target, color, rect, line_width, self: Self):
        pygame_draw_arc(draw_target, color, rect, self.start_angle, self.stop_angle, line_width)

    _draw = partial(_draw, pygame.draw.arc)


async def progress_spinner(dest: Rect, priority, *, color="white", line_width=20, min_arc_angle=0.3, speed=1.0, **kwargs):
    R1 = 0.4
    R2 = math.tau - min_arc_angle * 2
    next_start = itertools.accumulate(itertools.cycle((R1, R1, R1 + R2, R1, )), initial=0).__next__
    next_stop = itertools.accumulate(itertools.cycle((R1 + R2, R1, R1, R1, )), initial=min_arc_angle).__next__
    d = speed * 400

    anim_attrs = kwargs["clock"].anim_attrs
    arc = Arc(kwargs["draw_target"], Color(color), dest, next_start(), next_stop(), line_width)
    with kwargs["executor"].register(arc.draw, priority):
        while True:
            await anim_attrs(arc, start_angle=next_start(), stop_angle=next_stop(), duration=d)
