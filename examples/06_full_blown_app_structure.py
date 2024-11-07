from typing import Unpack
from functools import partial

import pygame
import pygame.font
from pygame.colordict import THECOLORS
import pygame.constants as C

import asyncpygame as apg
from asyncpygame.scene_switcher import SceneSwitcher, FadeTransition
from _uix.touch_indicator import touch_indicator
from _uix.anchor_layout import anchor_layout
from _uix.ripple_button import ripple_button
from _uix.modal_dialog import ask_yes_no_question


async def main(cp: apg.CommonParams):
    pygame.init()
    pygame.display.set_caption("<Your App Title>")
    cp.draw_target = screen = pygame.display.set_mode((800, 600))

    bgcolor = THECOLORS["black"]
    r = cp.executor.register
    r(partial(screen.fill, bgcolor), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)
    userdata = {
        'font': pygame.font.SysFont(None, 60),
        'bgcolor': bgcolor,
    }
    async with apg.open_nursery() as nursery:
        nursery.start(confirm_before_quitting(cp, priority=0xFFFFFD00))
        nursery.start(touch_indicator(cp, color="grey", priority=0xFFFFFE00))
        nursery.start(SceneSwitcher().run(title_scene, priority=0xFFFFFC00, userdata=userdata))


async def confirm_before_quitting(cp: apg.CommonParams, priority):
    wait = cp.sdlevent.wait
    quit = partial(wait, C.QUIT, priority=priority, consume=True)
    escape_key = partial(wait, C.KEYDOWN, priority=priority, filter=lambda e: e.key == C.K_ESCAPE, consume=True)
    while True:
        await apg.wait_any(quit(), escape_key())
        if await ask_yes_no_question("Quit the app?", priority=priority):
            apg.quit()


async def title_scene(*, switcher, userdata, **kwargs: Unpack[apg.CommonParams]):
    draw_target = kwargs["draw_target"]
    target_rect = draw_target.get_rect()
    font = userdata['font']
    async with apg.open_nursery() as nursery:
        e_start = apg.Event()
        s = nursery.start
        s(anchor_layout(
            font.render("<Your App Title>", True, "white", userdata["bgcolor"]).convert(draw_target),
            target_rect.scale_by(1.0, 0.5).move_to(y=target_rect.y),
            priority=0x100,
            **kwargs))
        s(ripple_button(
            button_image := font.render("Start", True, "white").convert_alpha(),
            button_image.get_rect(center=target_rect.scale_by(1.0, 0.5).move_to(bottom=target_rect.bottom).center).inflate(80, 80),
            on_click=e_start.fire,
            priority=0x100,
            **kwargs))
        await e_start.wait()
        switcher.switch_to(menu_scene, FadeTransition())
        await apg.sleep_forever()


async def menu_scene(*, switcher, userdata, **kwargs: Unpack[apg.CommonParams]):
    draw_target = kwargs["draw_target"]
    target_rect = draw_target.get_rect()
    font = userdata['font']
    async with apg.open_nursery() as nursery:
        e_play = apg.Event()
        e_back = apg.Event()
        s = nursery.start
        s(ripple_button(
            button_image := font.render("Play Game", True, "white").convert_alpha(),
            button_image.get_rect(center=target_rect.scale_by(1.0, 0.5).move_to(y=target_rect.y).center).inflate(80, 80),
            on_click=e_play.fire,
            priority=0x100, **kwargs))
        s(ripple_button(
            button_image := font.render("Back to Title", True, "white").convert_alpha(),
            button_image.get_rect(center=target_rect.scale_by(1.0, 0.5).move_to(bottom=target_rect.bottom).center).inflate(80, 80),
            on_click=e_back.fire,
            priority=0x100, **kwargs))
        tasks = await apg.wait_any(e_play.wait(), e_back.wait())
        next_scene = title_scene if tasks[1].finished else game_scene
        switcher.switch_to(next_scene, FadeTransition())
        await apg.sleep_forever()


async def game_scene(*, switcher, userdata, **kwargs: Unpack[apg.CommonParams]):
    draw_target = kwargs["draw_target"]
    target_rect = draw_target.get_rect()
    font = userdata['font']
    clock = kwargs["clock"]

    image = font.render("Running...", True, "white", userdata["bgcolor"]).convert(draw_target)
    dest = image.get_rect(center=target_rect.center)
    with kwargs["executor"].register(partial(draw_target.blit, image, dest), priority=0x100):
        async with clock.move_on_after(5000):
            await clock.anim_attrs(dest, y=dest.y - 80, duration=400)
            while True:
                await clock.anim_attrs(dest, y=dest.y + 160, duration=800)
                await clock.anim_attrs(dest, y=dest.y - 160, duration=800)
        switcher.switch_to(title_scene, FadeTransition())
        await apg.sleep_forever()


if __name__ == "__main__":
    apg.run(main)
