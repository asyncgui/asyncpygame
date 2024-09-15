from functools import partial
import itertools

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as ap
from asyncpygame.scene_switcher import SceneSwitcher, FadeTransition, SlideTransition, no_transition


async def main(*, executor: ap.PriorityExecutor, **kwargs):
    pygame.init()
    pygame.display.set_caption("Click the screen")
    screen = pygame.display.set_mode((800, 600))

    executor.register(partial(screen.fill, COLORS["black"]), priority=0)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)
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

    await SceneSwitcher().run(
        show_transition, draw_target=screen, executor=executor, priority=0xFFFFFE00,
        userdata=userdata, **kwargs)


async def show_transition(*, draw_target, executor, sdlevent, scene_switcher, userdata, **kwargs):
    font = userdata['font']
    text, transition = next(userdata['transitions'])
    img = font.render(text, True, COLORS["white"]).convert_alpha()
    with executor.register(partial(draw_target.blit, img, img.get_rect(center=draw_target.get_rect().center)), priority=0x100):
        await sdlevent.wait(pygame.MOUSEBUTTONDOWN)
        scene_switcher.switch_to(show_transition, transition)
        await ap.sleep_forever()


if __name__ == "__main__":
    ap.run(main, fps=60)
