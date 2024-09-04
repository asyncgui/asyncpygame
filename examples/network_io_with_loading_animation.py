'''
HTTPリクエストを出しその結果が返ってくるまでぐるぐる回る輪のアニメーションを表示する。
キャンセルボタンを押す事でリクエストをキャンセルできる。

ripple_buttonを用いているので無駄にコード量が増えている上、ボタンをラベル代わりに使っている部分があるので気をつけて下さい。
'''

from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
from pygame import Rect
import asyncpygame as ap
import requests

# other examples
from touch_indicator import touch_indicator
from progress_spinner import progress_spinner
from ripple_button import ripple_button


async def main(*, executor: ap.PriorityExecutor, clock: ap.Clock, **kwargs):
    pygame.init()
    pygame.display.set_caption("Network I/O with Loading Animation")
    screen = pygame.display.set_mode((600, 800))
    screen_rect = screen.get_rect()
    button_font = pygame.font.SysFont(None, 100)
    label_font = pygame.font.SysFont(None, 50)

    executor.register(partial(screen.fill, COLORS["black"]), priority=0)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)
    common_params = {'draw_target': screen, 'executor': executor, 'clock': clock, **kwargs}

    async with ap.open_nursery() as root_nursery:
        root_nursery.start(touch_indicator(color=COLORS['white'], priority=0xFFFFFE00, **common_params))

        button_release = ap.Event()
        async with ap.run_as_daemon(ripple_button(
            text="start", font=button_font, dst=Rect(0, 600, 600, 200).inflate(-40, -40),
            on_release=button_release.fire, priority=0x100, **common_params,
        )):
            await button_release.wait()

        async with ap.open_nursery() as nursery:
            nursery.start(
                progress_spinner(
                    dst=Rect(0, 0, 400, 400).move_to(center=screen_rect.center),
                    color=COLORS["white"], priority=0x100, **common_params,
                ),
                daemon=True,
            )
            nursery.start(
                ripple_button(  # NOTE: using button as a label
                    text="waiting for the server to respond", font=label_font, ripple_color=(0, 0, 0, 0),
                    bgcolor=(0, 0, 0, 0), priority=0x100, dst=Rect(0, 0, 600, 200).inflate(-40, -40), **common_params,
                ),
                daemon=True,
            )
            nursery.start(
                ripple_button(
                    text="cancel", font=button_font, dst=Rect(0, 600, 600, 200).inflate(-40, -40),
                    on_release=button_release.fire, priority=0x100, **common_params,
                ),
                daemon=True,
            )
            tasks = await ap.wait_any(
                clock.run_in_thread(lambda: requests.get("https://httpbin.org/delay/4"), polling_interval=200),
                button_release.wait(),
            )

        if tasks[0].finished:
            text = tasks[0].result.json()['headers']['User-Agent']
        else:
            text = "cancelled"
        root_nursery.start(ripple_button(  # NOTE: using button as a label
            text=text, font=label_font, dst=Rect(0, 0, 600, 200).inflate(-40, -40),
            ripple_color=(0, 0, 0, 0), bgcolor=(0, 0, 0, 0), priority=0x100, **common_params,
        ))


if __name__ == "__main__":
    ap.run(main)
