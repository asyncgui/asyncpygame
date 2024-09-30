from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as apg

from _uix.touch_indicator import touch_indicator
from _uix.ripple_button import RippleButton
from _uix.modal_dialog import ask_yes_no_question


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Asking Question")
    kwargs["draw_target"] = screen = pygame.display.set_mode((600, 600))
    screen_rect = screen.get_rect()
    button_font = pygame.font.SysFont(None, 50)

    r = kwargs["executor"].register
    r(partial(screen.fill, COLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    async with apg.open_nursery() as nursery:
        nursery.start(touch_indicator(color="darkgreen", priority=0xFFFFFE00, **kwargs))
        button = RippleButton(
            nursery,
            button_image := button_font.render("open dialog", True, COLORS["white"]).convert_alpha(),
            button_image.get_rect(centerx=screen_rect.centerx).inflate(40, 40).move_to(bottom=screen_rect.bottom - 20),
            priority=0x100, **kwargs)

        while True:
            await button.to_be_clicked()
            answer = await ask_yes_no_question("Do you like PyGame?", priority=0xFFFFFA00, **kwargs)
            print("YES" if answer else "NO")


if __name__ == "__main__":
    apg.run(main)
