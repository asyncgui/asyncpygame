from functools import partial

import pygame
from pygame.colordict import THECOLORS as COLORS
import asyncpygame

from _uix.progress_spinner import progress_spinner


async def main(**kwargs):
    pygame.init()
    pygame.display.set_caption("Progress Spinner")
    screen = pygame.display.set_mode((600, 600))

    r = kwargs["executor"].register
    r(partial(screen.fill, COLORS["white"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    await progress_spinner(screen.get_rect().scale_by(0.8), priority=0x100, draw_target=screen, **kwargs)


if __name__ == "__main__":
    asyncpygame.run(main)
