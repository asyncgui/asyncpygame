from typing import Unpack
from functools import partial
import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Touching the screen will skip the animation")

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

    mouse_button_down = partial(kwargs["sdlevent"].wait, pygame.MOUSEBUTTONDOWN, priority=0x100)
    move_sprite = partial(kwargs["clock"].anim_attrs, img_rect, duration=1000)
    wait_any = apg.wait_any

    while True:
        await wait_any(mouse_button_down(), move_sprite(right=screen_rect.right))
        img_rect.right = screen_rect.right
        await wait_any(mouse_button_down(), move_sprite(bottom=screen_rect.bottom))
        img_rect.bottom = screen_rect.bottom
        await wait_any(mouse_button_down(), move_sprite(x=screen_rect.x))
        img_rect.x = screen_rect.x
        await wait_any(mouse_button_down(), move_sprite(y=screen_rect.y))
        img_rect.y = screen_rect.y


if __name__ == "__main__":
    apg.run(main, fps=60)
