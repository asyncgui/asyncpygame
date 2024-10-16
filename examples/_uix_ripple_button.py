from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS
from pygame import Rect
import asyncpygame as apg

from _uix.ripple_button import ripple_button


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Ripple Button")
    kwargs["draw_target"] = screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 100)

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    await apg.wait_all(
        ripple_button(
            font.render("PyGame", True, "white"),
            Rect(100, 100, 300, 200),
            on_click=lambda *_: print("PyGame"),
            priority=0x100, **kwargs),
        ripple_button(
            font.render("Python", True, "white"),
            Rect(280, 240, 300, 200),
            on_click=lambda *_: print("Python"),
            bgcolor="darkgreen",
            priority=0x200,
            **kwargs),
    )


if __name__ == "__main__":
    apg.run(main)
