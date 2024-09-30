from functools import partial

import pygame
from pygame.colordict import THECOLORS as COLORS
import asyncpygame
from _uix.touch_indicator import touch_indicator


async def main(**kwargs):
    pygame.init()
    pygame.display.set_caption("Touch Indicator")
    screen = pygame.display.set_mode((600, 600))

    r = kwargs["executor"].register
    r(partial(screen.fill, COLORS["white"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    await touch_indicator(draw_target=screen, priority=0x100, **kwargs)


if __name__ == "__main__":
    asyncpygame.run(main)
