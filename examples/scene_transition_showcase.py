from typing import Unpack
from functools import partial
import itertools

import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg
from asyncpygame.scene_switcher import SceneSwitcher, FadeTransition, SlideTransition, no_transition


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Click the screen")
    kwargs["draw_target"] = screen = pygame.display.set_mode((800, 600))

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)
    userdata = {
        'font': pygame.font.SysFont(None, 50),
        'transitions': itertools.cycle((
            ("FadeTransition()", FadeTransition(), ),
            ("SlideTransition(direction='left')", SlideTransition(direction='left'), ),
            ("SlideTransition(direction='up')", SlideTransition(direction='up'), ),
            ("SlideTransition(direction='right')", SlideTransition(direction='right'), ),
            ("SlideTransition(direction='down')", SlideTransition(direction='down'), ),
            ("no_transition", no_transition, ),
        ))
    }
    await SceneSwitcher().run(show_transition, priority=0xFFFFFD00, userdata=userdata, **kwargs)


async def show_transition(*, scene_switcher, userdata, executor, sdlevent, draw_target, **__):
    font = userdata['font']
    text, transition = next(userdata['transitions'])
    img = font.render(text, True, "white").convert_alpha()
    with executor.register(partial(draw_target.blit, img, img.get_rect(center=draw_target.get_rect().center)), priority=0x100):
        await sdlevent.wait(pygame.MOUSEBUTTONDOWN, priority=0)
        scene_switcher.switch_to(show_transition, transition)
        await apg.sleep_forever()


if __name__ == "__main__":
    apg.run(main, fps=60)
