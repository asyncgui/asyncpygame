from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg

from _uix.anchor_layout import anchor_layout


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Anchor Layout")
    kwargs["draw_target"] = screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 30)

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    dest = screen.get_rect().inflate(-20, -20)
    await apg.wait_all(*(
        anchor_layout(font.render(anchor, True, "white"), dest, priority=0x100, anchor_image=anchor, anchor_dest=anchor, **kwargs)
        for anchor in "topleft midtop topright midleft center midright bottomleft midbottom bottomright".split()
    ))


if __name__ == "__main__":
    apg.run(main)
