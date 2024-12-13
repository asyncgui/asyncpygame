__all__ = ('touch_indicator', )

from functools import partial
from typing import Unpack

import pygame
from pygame import Color, Event, Surface
import pygame.constants as C
import asyncpygame as apg


def generate_ring_image(color, radius, line_width) -> Surface:
    ring_img = Surface((radius * 2, radius * 2))
    color = Color(color)
    bgcolor = Color("black")
    if color == bgcolor:
        bgcolor = Color("white")
        ring_img.fill(bgcolor)
    pygame.draw.circle(ring_img, color, (radius, radius), radius, line_width)
    ring_img = ring_img.convert()
    ring_img.set_colorkey(bgcolor)
    return ring_img


async def touch_indicator(*, color="white", radius=60, line_width=4, priority, **kwargs: Unpack[apg.CommonParams]):
    ring_img = generate_ring_image(color, radius, line_width)
    async with (
        apg.open_nursery() as nursery,
        kwargs["sdlevent"].wait_freq(
            C.MOUSEBUTTONDOWN, C.FINGERDOWN, priority=priority,
            filter=lambda e: not getattr(e, 'touch', False)
        ) as touch_down,
    ):
        funcs = (draw_ring_under_finger, draw_ring_under_mouse_cursor, )
        while True:
            e_down = await touch_down()
            nursery.start(funcs[e_down.type == C.MOUSEBUTTONDOWN](ring_img, e_down, priority=priority, **kwargs))


def on_mouse_motion(dest, e: Event):
    dest.center = e.pos


async def draw_ring_under_mouse_cursor(
        ring_img: Surface, e_down: Event, *, priority, executor, sdlevent, draw_target, **__):
    dest = ring_img.get_rect(center=e_down.pos)
    with (
        executor.register(partial(draw_target.blit, ring_img, dest), priority),
        sdlevent.subscribe((C.MOUSEMOTION, ), partial(on_mouse_motion, dest), priority),

    ):
        await sdlevent.wait(C.MOUSEBUTTONUP, filter=lambda e: e.button == e_down.button, priority=priority)


def on_finger_motion(finger_id, dest, e: Event):
    if finger_id == e.finger_id:
        dest.center = e.pos


async def draw_ring_under_finger(
        ring_img: Surface, e_down: Event, *, priority, executor, sdlevent, draw_target, **__):
    dest = ring_img.get_rect(center=e_down.pos)
    with (
        executor.register(partial(draw_target.blit, ring_img, dest), priority),
        sdlevent.subscribe((C.FINGERMOTION, ), partial(on_finger_motion, e_down.finger_id, dest), priority),
    ):
        await sdlevent.wait(C.FINGERUP, filter=lambda e: e.finger_id == e_down.finger_id, priority=priority)
