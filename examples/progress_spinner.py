import math
import itertools
from functools import partial
from dataclasses import dataclass

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
from pygame import Surface, Color, Rect
import asyncpygame as ap


@dataclass(kw_only=True)
class Arc:
    draw_target: Surface
    color: Color
    rect: Rect
    start_angle: float
    stop_angle: float
    width: int

    def draw(self):
        pygame.draw.arc(self.draw_target, self.color, self.rect, self.start_angle, self.stop_angle, self.width)


async def progress_spinner(
    *, draw_target: Surface, dst: Rect, color=COLORS["black"], line_width=20,
    min_arc_angle=0.3, speed=1.0,
    clock: ap.Clock, executor: ap.PriorityExecutor, priority, **kwargs
):
    R1 = 0.4
    R2 = math.tau - min_arc_angle * 2
    next_start = itertools.accumulate(itertools.cycle((R1, R1, R1 + R2, R1, )), initial=0).__next__
    next_stop = itertools.accumulate(itertools.cycle((R1 + R2, R1, R1, R1, )), initial=min_arc_angle).__next__
    d = speed * 400

    arc = Arc(draw_target=draw_target, color=color, rect=dst, start_angle=next_start(), stop_angle=next_stop(), width=line_width)
    with executor.register(arc.draw, priority=priority):
        while True:
            await clock.anim_attrs(arc, start_angle=next_start(), stop_angle=next_stop(), duration=d)


async def main(*, executor: ap.PriorityExecutor, **kwargs):
    pygame.init()
    pygame.display.set_caption("Progress Spinner")
    screen = pygame.display.set_mode((600, 600))

    executor.register(partial(screen.fill, COLORS["white"]), priority=0)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)

    await progress_spinner(
        draw_target=screen, dst=screen.get_rect().scale_by(0.8),
        executor=executor, priority=0x100, **kwargs,
    )


if __name__ == "__main__":
    ap.run(main)
