from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
from pygame import Rect
import asyncpygame as apg

from _uix.ripple_button import RippleButton


async def main(**kwargs):
    pygame.init()
    pygame.display.set_caption("Ripple Button")
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 100)

    r = kwargs["executor"].register
    r(partial(screen.fill, COLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)
    kwargs["draw_target"] = screen

    async with apg.open_nursery() as nursery:
        RippleButton(nursery, font.render("PyGame", True, "white"), Rect(100, 100, 300, 200), priority=0x100, **kwargs)
        RippleButton(nursery, font.render("Python", True, "white"), Rect(280, 240, 300, 200), priority=0x200, bgcolor="darkgreen", **kwargs)
        await apg.sleep_forever()


if __name__ == "__main__":
    apg.run(main)
