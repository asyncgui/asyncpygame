from functools import partial
from dataclasses import dataclass

import pygame
from pygame import Surface, Color, Event, Vector2
from pygame.colordict import THECOLORS as COLORS
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, FINGERDOWN, FINGERUP, FINGERMOTION
import asyncpygame as ap


@dataclass(kw_only=True)
class Ring:
    draw_target: Surface
    color: Color
    pos: tuple | Vector2 = (0, 0, )
    radius: int = 60
    line_width: int = 4

    def draw(self):
        pygame.draw.circle(self.draw_target, self.color, self.pos, self.radius, self.line_width)


async def touch_indicator(*, draw_target: Surface, color: Color=COLORS["black"], executor: ap.PriorityExecutor, sdlevent: ap.SDLEvent, priority, **kwargs):
    async with (
        ap.open_nursery() as nursery,
        sdlevent.wait_freq(MOUSEBUTTONDOWN, FINGERDOWN, priority=priority, filter=lambda e: not getattr(e, 'touch', False)) as touch_down,
    ):
        while True:
            e_down = await touch_down()
            if e_down.type == MOUSEBUTTONDOWN:
                f = draw_ring_under_mouse_cursor
            else:
                f = draw_ring_under_finger
            nursery.start(f(e_down, draw_target=draw_target, color=color, executor=executor, sdlevent=sdlevent, priority=priority))


async def draw_ring_under_mouse_cursor(e_down: Event, *, draw_target, color, executor, sdlevent, priority, **kwargs):
    ring = Ring(draw_target=draw_target, color=color, pos=e_down.pos)
    with executor.register(ring.draw, priority=priority):
        async with (
            ap.move_on_when(sdlevent.wait(MOUSEBUTTONUP, filter=lambda e: e.button == e_down.button, priority=priority)),
            sdlevent.wait_freq(MOUSEMOTION, priority=priority) as mouse_motion,
        ):
            while True:
                e = await mouse_motion()
                ring.pos = e.pos


async def draw_ring_under_finger(e_down: Event, *, draw_target, color, executor, sdlevent, priority, **kwargs):
    ring = Ring(draw_target=draw_target, color=color, pos=e_down.pos)
    with executor.register(ring.draw, priority=priority):
        async with (
            ap.move_on_when(sdlevent.wait(FINGERUP, filter=lambda e: e.finger_id == e_down.finger_id, priority=priority)),
            sdlevent.wait_freq(FINGERMOTION, filter=lambda e: e.finger_id == e_down.finger_id, priority=priority) as finger_motion,
        ):
            while True:
                e = await finger_motion()
                ring.pos = e.pos


async def main(*, clock: ap.Clock, executor: ap.PriorityExecutor, sdlevent: ap.SDLEvent, **kwargs):
    pygame.init()
    pygame.display.set_caption("Touch Indicator")
    screen = pygame.display.set_mode((1280, 720))

    executor.register(partial(screen.fill, COLORS["white"]), priority=0)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)

    await touch_indicator(draw_target=screen, executor=executor, sdlevent=sdlevent, clock=clock, priority=0x100)


if __name__ == "__main__":
    ap.run(main)
