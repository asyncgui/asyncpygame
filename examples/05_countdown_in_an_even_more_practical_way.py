from typing import Unpack
from functools import partial
import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg


async def countdown(cp: apg.CommonParams, priority, *, count_from: int):
    center = cp.draw_target.get_rect().center
    font = pygame.font.SysFont(None, 400)
    fgcolor = THECOLORS["black"]

    with cp.executor.register(None, priority) as req:
        for i in range(count_from, -1, -1):
            img = font.render(str(i), True, fgcolor).convert_alpha()
            req.callback = partial(cp.draw_target.blit, img, img.get_rect(center=center))
            await cp.clock.sleep(1000)


async def main(cp: apg.CommonParams):
    pygame.init()
    pygame.display.set_caption("Countdown")
    cp.draw_target = screen = pygame.display.set_mode((400, 400))

    r = cp.executor.register
    r(partial(screen.fill, THECOLORS["white"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    await countdown(cp, priority=0x100, count_from=3)


if __name__ == "__main__":
    apg.run(main)
