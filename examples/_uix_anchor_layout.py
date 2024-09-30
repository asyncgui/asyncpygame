from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as apg

from _uix.anchor_layout import AnchorLayout


async def main(**kwargs):
    pygame.init()
    pygame.display.set_caption("Anchor Layout")
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 30)

    r = kwargs["executor"].register
    r(partial(screen.fill, COLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)
    kwargs["draw_target"] = screen

    async with apg.open_nursery() as nursery:
        dest = screen.get_rect().inflate(-20, -20)
        for anchor in "topleft midtop topright midleft center midright bottomleft midbottom bottomright".split():
            AnchorLayout(
                nursery, font.render(anchor, True, "white"), dest,
                anchor_src=anchor, anchor_dest=anchor, priority=0x100, **kwargs)
        await apg.sleep_forever()


if __name__ == "__main__":
    apg.run(main)
