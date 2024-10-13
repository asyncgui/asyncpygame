from typing import Unpack
from functools import partial
import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg


async def countdown(*, count_from: int, draw_target: pygame.Surface, clock: apg.Clock, executor: apg.PriorityExecutor, priority, **__):
    center = draw_target.get_rect().center
    font = pygame.font.SysFont(None, 400)
    fgcolor = THECOLORS["black"]

    with executor.register(None, priority) as req:
        for i in range(count_from, -1, -1):
            img = font.render(str(i), True, fgcolor).convert_alpha()
            req.callback = partial(draw_target.blit, img, img.get_rect(center=center))
            await clock.sleep(1000)


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Countdown")
    kwargs["draw_target"] = screen = pygame.display.set_mode((400, 400))

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["white"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    await countdown(count_from=3, priority=0x100, **kwargs)


if __name__ == "__main__":
    apg.run(main)
