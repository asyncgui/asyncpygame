'''
In-app mouse cursor.
'''

__all__ = ('inapp_mouse_cursor', )

from functools import partial
from typing import Unpack

import pygame
from pygame.math import Vector2
from pygame import Color
import pygame.constants as C
import asyncpygame as apg


def generate_cursor_image(size: int, color) -> pygame.Surface:
    cursor_img = pygame.Surface((size, size))
    bgcolor = Color("black")
    color = Color(color)
    if color == bgcolor:
        bgcolor = Color("white")
        cursor_img.fill(bgcolor)
    hs = size // 2
    v = size // 10
    points = (
        (0, 0),
        (hs, size),
        (hs + v, hs + v),
        (size, hs),
    )
    pygame.draw.polygon(cursor_img, color, points)
    cursor_img = cursor_img.convert()
    cursor_img.set_colorkey(bgcolor)
    return cursor_img


async def inapp_mouse_cursor(*, color="white", size=60, initial_pos=(-0xFFFF, -0xFFFF), priority, **kwargs: Unpack[apg.CommonParams]):
    img = generate_cursor_image(size, color)
    pos = Vector2(initial_pos)

    with (
        kwargs["executor"].register(partial(kwargs["draw_target"].blit, img, pos), priority),
        kwargs["sdlevent"].subscribe((C.MOUSEMOTION, ), lambda e, update=pos.update: update(e.pos), priority),
    ):
        await apg.sleep_forever()
