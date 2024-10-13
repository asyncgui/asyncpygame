from typing import Unpack
from functools import partial

import pygame
from pygame.colordict import THECOLORS
import asyncpygame as apg
from _uix.touch_indicator import touch_indicator


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Touch Indicator")
    kwargs["draw_target"] = screen = pygame.display.set_mode((600, 600))

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    await touch_indicator(priority=0x100, **kwargs)


if __name__ == "__main__":
    apg.run(main)
