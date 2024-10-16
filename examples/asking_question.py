from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg

from _uix.touch_indicator import touch_indicator
from _uix.ripple_button import ripple_button
from _uix.modal_dialog import ask_yes_no_question, show_messagebox


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Asking Question")
    kwargs["draw_target"] = screen = pygame.display.set_mode((600, 600))
    screen_rect = screen.get_rect()
    button_font = pygame.font.SysFont(None, 50)

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    async with apg.open_nursery() as nursery:
        e_open = apg.Event()
        s = nursery.start
        s(touch_indicator(color="darkgreen", priority=0xFFFFFE00, **kwargs))
        s(ripple_button(
            image := button_font.render("open dialog", True, THECOLORS["white"]).convert_alpha(),
            image.get_rect(centerx=screen_rect.centerx).inflate(40, 40).move_to(bottom=screen_rect.bottom - 20),
            priority=0x100,
            on_click=e_open.fire,
            **kwargs))

        while True:
            await e_open.wait()
            answer = await ask_yes_no_question("Do you like PyGame?", priority=0xFFFFFA00, **kwargs)
            await show_messagebox(f"You answered '{'Yes' if answer else 'No'}'.", priority=0xFFFFFA00, **kwargs)


if __name__ == "__main__":
    apg.run(main)
