'''
- Press mouse button 1 to draw rectangles.
- Press mouse button 3 to draw ellipses.
'''
import itertools
from functools import partial
from random import choice

import pygame
from pygame import Event
from pygame.colordict import THECOLORS as COLORS
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
import asyncpygame as ap


async def painter(*, draw_target, executor, sdlevent, priority, **kwargs):
    colors = tuple(COLORS.values())

    button2command = {
        1: draw_rect,
        3: draw_ellipse,
    }
    async with ap.open_nursery() as nursery:
        next_priority = itertools.count(priority + 1).__next__
        while True:
            e_down = await sdlevent.wait(MOUSEBUTTONDOWN, priority=priority)
            command = button2command.get(e_down.button)
            if command is None:
                continue
            nursery.start(command(e_down, draw_target=draw_target, color=choice(colors), executor=executor, sdlevent=sdlevent, priority=next_priority()))


async def draw_rect(e_down: Event, *, draw_target, color, executor, sdlevent, priority, line_width=4, **kwargs):
    ox, oy = e_down.pos
    rect = pygame.Rect(ox, oy, 0, 0)
    executor.register(partial(pygame.draw.rect, draw_target, color, rect, line_width), priority=priority)
    async with (
        ap.move_on_when(sdlevent.wait(MOUSEBUTTONUP, filter=lambda e: e.button == e_down.button, priority=priority)),
        sdlevent.wait_freq(MOUSEMOTION, priority=priority) as mouse_motion,
    ):
        while True:
            e = await mouse_motion()
            x, y = e.pos
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            rect.update(min_x, min_y, max_x - min_x, max_y - min_y)


async def draw_ellipse(e_down: Event, *, draw_target, color, executor, sdlevent, priority, line_width=4, **kwargs):
    ox, oy = e_down.pos
    rect = pygame.Rect(ox, oy, 0, 0)
    executor.register(partial(pygame.draw.ellipse, draw_target, color, rect, line_width), priority=priority)
    bbox_req = executor.register(partial(pygame.draw.rect, draw_target, COLORS["black"], rect, 1), priority=priority)
    async with (
        ap.move_on_when(sdlevent.wait(MOUSEBUTTONUP, filter=lambda e: e.button == e_down.button, priority=priority)),
        sdlevent.wait_freq(MOUSEMOTION, priority=priority) as mouse_motion,
    ):
        while True:
            e = await mouse_motion()
            x, y = e.pos
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            rect.update(min_x, min_y, max_x - min_x, max_y - min_y)
    bbox_req.cancel()


async def main(*, clock: ap.Clock, executor: ap.PriorityExecutor, sdlevent: ap.SDLEvent, **kwargs):
    pygame.init()
    pygame.display.set_caption("Painter")
    screen = pygame.display.set_mode((800, 600))

    executor.register(partial(screen.fill, COLORS["white"]), priority=0)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)

    await painter(draw_target=screen, executor=executor, sdlevent=sdlevent, clock=clock, priority=0x100)


if __name__ == "__main__":
    ap.run(main)
