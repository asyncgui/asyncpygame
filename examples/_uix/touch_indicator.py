__all__ = ('touch_indicator', )

from functools import partial
from typing import Unpack

import pygame
from pygame import Color, Event
import pygame.constants as C
import asyncpygame as apg


class Ring:
    __slots__ = ('draw', 'pos', )

    def __init__(self, draw_target: pygame.Surface, color, initial_pos, radius, line_width):
        ring_img = pygame.Surface((radius * 2, radius * 2)).convert(draw_target)
        color = Color(color)
        bgcolor = Color("black")
        if color == bgcolor:
            bgcolor = Color("white")
            ring_img.fill(bgcolor)
        ring_img.set_colorkey(bgcolor)
        pygame.draw.circle(ring_img, color, (radius, radius), radius, line_width)

        self.draw = partial(self.__class__._draw, self, draw_target.blit, ring_img, ring_img.get_rect())
        self.pos = initial_pos

    def _draw(self, blit, ring_img, ring_dest):
        ring_dest.center = self.pos
        blit(ring_img, ring_dest)


async def touch_indicator(*, color="white", radius=60, line_width=4, priority, **kwargs: Unpack[apg.CommonParams]):
    color = Color(color)
    draw_target = kwargs["draw_target"]
    async with (
        apg.open_nursery() as nursery,
        kwargs["sdlevent"].wait_freq(
            C.MOUSEBUTTONDOWN, C.FINGERDOWN, priority=priority,
            filter=lambda e: not getattr(e, 'touch', False)
        ) as touch_down,
    ):
        while True:
            e_down = await touch_down()
            if e_down.type == C.MOUSEBUTTONDOWN:
                f = draw_ring_under_mouse_cursor
            else:
                f = draw_ring_under_finger
            nursery.start(f(e_down, priority=priority, ring=Ring(draw_target, color, e_down.pos, radius, line_width), **kwargs))


async def draw_ring_under_mouse_cursor(e_down: Event, *, priority, executor, sdlevent, ring, **__):
    with executor.register(ring.draw, priority):
        async with (
            apg.move_on_when(sdlevent.wait(C.MOUSEBUTTONUP, filter=lambda e: e.button == e_down.button, priority=priority)),
            sdlevent.wait_freq(C.MOUSEMOTION, priority=priority) as mouse_motion,
        ):
            while True:
                e = await mouse_motion()
                ring.pos = e.pos


async def draw_ring_under_finger(e_down: Event, *, priority, executor, sdlevent, ring, **__):
    with executor.register(ring.draw, priority):
        async with (
            apg.move_on_when(sdlevent.wait(C.FINGERUP, filter=lambda e: e.finger_id == e_down.finger_id, priority=priority)),
            sdlevent.wait_freq(C.FINGERMOTION, filter=lambda e: e.finger_id == e_down.finger_id, priority=priority) as finger_motion,
        ):
            while True:
                e = await finger_motion()
                ring.pos = e.pos
