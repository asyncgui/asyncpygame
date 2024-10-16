from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS
from pygame import Rect
import asyncpygame as apg
import requests

from _uix.touch_indicator import touch_indicator
from _uix.progress_spinner import progress_spinner
from _uix.ripple_button import ripple_button
from _uix.anchor_layout import anchor_layout


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Network I/O + Animation")
    kwargs["draw_target"] = screen = pygame.display.set_mode((600, 800))
    font = pygame.font.SysFont(None, 50)
    bgcolor = THECOLORS["black"]
    fgcolor = THECOLORS["white"]

    r = kwargs["executor"].register
    r(partial(screen.fill, bgcolor), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)
    del r

    async with apg.run_as_main(touch_indicator(color=fgcolor, priority=0xFFFFFE00, **kwargs)):
        e_click = apg.Event()
        await apg.wait_any(
            e_click.wait(),
            ripple_button(
                font.render("start", True, fgcolor).convert_alpha(),
                button_dest := Rect(0, 600, 600, 200).inflate(-40, -40),
                priority=0x100, on_click=e_click.fire, **kwargs),
        )

        tasks = await apg.wait_any(
            kwargs["clock"].run_in_thread(
                lambda: requests.get("https://httpbin.org/delay/4"),
                polling_interval=200, daemon=True),
            e_click.wait(),
            progress_spinner(
                Rect(0, 0, 400, 400).move_to(center=screen.get_rect().center),
                color=fgcolor,
                priority=0x100, **kwargs),
            ripple_button(
                font.render("cancel", True, fgcolor).convert_alpha(),
                button_dest,
                on_click=e_click.fire,
                priority=0x100, **kwargs),
            anchor_layout(
                font.render("waiting for the server to respond", True, fgcolor, bgcolor).convert(screen),
                label_dest := Rect(0, 0, 600, 200).inflate(-40, -40),
                priority=0x100, **kwargs)
        )
        if tasks[0].finished:
            text = tasks[0].result.json()['headers']['User-Agent']
        else:
            text = "cancelled"

        await apg.wait_any(
            e_click.wait(),
            ripple_button(
                font.render("Quit the App", True, fgcolor).convert_alpha(),
                button_dest,
                on_click=e_click.fire,
                priority=0x100, **kwargs),
            anchor_layout(
                font.render(text, True, fgcolor, bgcolor).convert(screen),
                label_dest,
                priority=0x100, **kwargs)
        )
        apg.quit()


if __name__ == "__main__":
    apg.run(main)
