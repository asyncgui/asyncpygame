'''
- Press mouse button 1 to draw rectangles.
- Press mouse button 3 to draw ellipses.
'''
from typing import Unpack
import itertools
from functools import partial
from random import choice

import pygame
from pygame import Event
from pygame.colordict import THECOLORS as COLORS
import pygame.constants as C
import asyncpygame as apg
from _uix.touch_indicator import touch_indicator


async def painter(*, priority, **kwargs: Unpack[apg.CommonParams]):
    colors = tuple(COLORS.values())

    button2command = {
        1: draw_rect,
        3: draw_ellipse,
    }
    async with apg.open_nursery() as nursery:
        next_priority = itertools.count(priority + 1).__next__
        mouse_button_down = partial(kwargs["sdlevent"].wait, C.MOUSEBUTTONDOWN, priority=priority)
        while True:
            e_down = await mouse_button_down()
            command = button2command.get(e_down.button)
            if command is None:
                continue
            nursery.start(command(e_down, color=choice(colors), priority=next_priority(), **kwargs))


async def draw_rect(e_down: Event, *, draw_target, color, executor, sdlevent, priority, line_width=4, **unused):
    ox, oy = e_down.pos
    rect = pygame.Rect(ox, oy, 0, 0)
    executor.register(partial(pygame.draw.rect, draw_target, color, rect, line_width), priority=priority)
    async with (
        apg.move_on_when(sdlevent.wait(C.MOUSEBUTTONUP, filter=lambda e: e.button == e_down.button, priority=priority)),
        sdlevent.wait_freq(C.MOUSEMOTION, priority=priority) as mouse_motion,
    ):
        while True:
            e = await mouse_motion()
            x, y = e.pos
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            rect.update(min_x, min_y, max_x - min_x, max_y - min_y)


async def draw_ellipse(e_down: Event, *, draw_target, color, executor, sdlevent, priority, line_width=4, **unused):
    ox, oy = e_down.pos
    rect = pygame.Rect(ox, oy, 0, 0)
    executor.register(partial(pygame.draw.ellipse, draw_target, color, rect, line_width), priority)
    bbox_req = executor.register(partial(pygame.draw.rect, draw_target, COLORS["black"], rect, 1), priority)
    async with (
        apg.move_on_when(sdlevent.wait(C.MOUSEBUTTONUP, filter=lambda e: e.button == e_down.button, priority=priority)),
        sdlevent.wait_freq(C.MOUSEMOTION, priority=priority) as mouse_motion,
    ):
        while True:
            e = await mouse_motion()
            x, y = e.pos
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            rect.update(min_x, min_y, max_x - min_x, max_y - min_y)
    bbox_req.cancel()


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Painter")
    kwargs["draw_target"] = screen = pygame.display.set_mode((800, 600))

    r = kwargs["executor"].register
    r(partial(screen.fill, COLORS["white"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    async with apg.open_nursery() as nursery:
        nursery.start(touch_indicator(color="black", priority=0xFFFFFE00, **kwargs))
        nursery.start(painter(priority=0x100, **kwargs))


if __name__ == "__main__":
    apg.run(main)
