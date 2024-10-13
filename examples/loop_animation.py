from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Loop Animation")

    screen = pygame.display.set_mode((1280, 720))
    font = pygame.font.SysFont(None, 200)
    img = font.render("(^.^)", True, THECOLORS["white"]).convert_alpha()
    img_rect = img.get_rect()
    screen_rect = screen.get_rect()

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["black"]), priority=0)
    r(partial(screen.blit, img, img_rect), priority=0x100)
    r(pygame.display.flip, priority=0xFFFFFF00)
    del r

    anim_attrs = kwargs["clock"].anim_attrs
    while True:
        await anim_attrs(img_rect, right=screen_rect.right, duration=1000)
        await anim_attrs(img_rect, bottom=screen_rect.bottom, duration=1000)
        await anim_attrs(img_rect, left=screen_rect.left, duration=1000)
        await anim_attrs(img_rect, top=screen_rect.top, duration=1000)


if __name__ == "__main__":
    apg.run(main, fps=60)
