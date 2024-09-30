from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
from pygame import Rect
import asyncpygame as apg
import requests

from _uix.touch_indicator import touch_indicator
from _uix.ripple_button import RippleButton
from _uix.anchor_layout import AnchorLayout


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Network I/O")
    kwargs["draw_target"] = screen = pygame.display.set_mode((600, 800))
    font = pygame.font.SysFont(None, 50)
    bgcolor = COLORS["black"]
    fgcolor = COLORS["white"]

    r = kwargs["executor"].register
    r(partial(screen.fill, bgcolor), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    async with apg.open_nursery() as nursery:
        nursery.start(touch_indicator(color=fgcolor, priority=0xFFFFFE00, **kwargs))
        button = RippleButton(
            nursery,
            font.render("start", True, fgcolor).convert_alpha(),
            Rect(0, 600, 600, 200).inflate(-40, -40),
            priority=0x100, **kwargs)
        await button.to_be_clicked()

        label = AnchorLayout(
            nursery,
            font.render("waiting for the server to respond", True, fgcolor, bgcolor).convert(screen),
            Rect(0, 0, 600, 200).inflate(-40, -40),
            priority=0x100, **kwargs)
        button.image = font.render("cancel", True, fgcolor).convert_alpha()
        tasks = await apg.wait_any(
            kwargs["clock"].run_in_thread(lambda: requests.get("https://httpbin.org/delay/4"), polling_interval=200),
            button.to_be_clicked(),
        )

        if tasks[0].finished:
            text = tasks[0].result.json()['headers']['User-Agent']
        else:
            text = "cancelled"
        label.image = font.render(text, True, fgcolor, bgcolor).convert(screen)
        button.image = font.render("Quit the App", True, fgcolor).convert_alpha()
        await button.to_be_clicked()
        apg.quit()


if __name__ == "__main__":
    apg.run(main)
