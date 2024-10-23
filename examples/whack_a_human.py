from typing import Unpack
from functools import partial

import io
from os import PathLike
from pathlib import Path
import sqlite3

from PIL import Image
import pygame
import pygame.font
from pygame.colordict import THECOLORS
import pygame.constants as C

import asyncpygame as apg
from asyncpygame.scene_switcher import SceneSwitcher, FadeTransition
from _uix.touch_indicator import touch_indicator
from _uix.anchor_layout import anchor_layout
from _uix.ripple_button import ripple_button
from _uix.modal_dialog import ask_yes_no_question, message_with_spinner


def download_images() -> dict[str, bytes]:
    IMAGE_URLS = (
        ('neutral', 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgh1PA4Bjg2mGnrFcuufNP1WP2kPRqXMRJQSz-fHxBxRYSGjwZQmbkMEe495vP_23LwafvGR2her8vQhM836BMYvJvKCJVkH9NvHTJ5gdoyAz5bFuQIW7SUDX7gTDJC7qIsqyE9vhuU9Wg/s400/figure_standing.png'),
        ('square-off', 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5w726e-ADC9DDJdytCRtdPAHogCk3CLTNF-2N3RglZbTgf_Ad1-2N4rQngxYE8IeDlz0E-fhIJOsOGoisP-O1J66KVTFFs9DJ6b7Vd4YyXGkPWNFpmNn0Kl7IkiPhZcnomsfrnDYur4k/s400/figure_fighting_pose.png'),
        ('attack', 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiuUsvvOwAK4_FlBL5itKyfcgQhzpOhsLZCUFHWbgZZVUl6-Km5hwFIiF8fKCJ2zSdQD5sJpqsBIWEOqThdmc6RUb1FHCtxV7AwyRFX4keVgnm0AN6I-6iDI_yrbWYHLsi2qUUTFLMVySI/s400/figure_fighting_punch.png'),
        ('clap', 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiYu-t8WjYxwde_VFWPsxSSg6ux32QZtPmP6BFlqrlcZmjiP0bCMO_uwcLwliT9YKSY-Pdk7YLWn-d1tEAeJbvfXAchJ-5vl0tYeWa5cFDSbQIGZ0t0dpH8DQPZ000CbHgJkdzxwYKpnf7K/s450/figure_hakusyu.png'),
    )
    import requests
    with requests.Session() as session:
        return {name: session.get(url).content for name, url in IMAGE_URLS}


def crop_image(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data))
    cropped = img.crop(img.getbbox())
    with io.BytesIO() as f:
        cropped.save(f, format="PNG")
        return f.getvalue()
    

def init_database(db_path: PathLike):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE Images(
                name TEXT NOT NULL UNIQUE,
                image BLOB DEFAULT NULL,
                PRIMARY KEY (name)
            )
        """)
        images = download_images()
        conn.executemany(
            "INSERT INTO Images(name, image) VALUES(?, ?)",
            ((name, crop_image(image)) for name, image in images.items()),
        )


def load_images_from_database(db_path: PathLike) ->  dict[str, bytes]:
    with sqlite3.connect(db_path) as conn:
        return dict(conn.execute("SELECT name, image FROM Images"))


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.init()
    pygame.display.set_caption("Whack a Human")
    kwargs["draw_target"] = screen = pygame.display.set_mode((1280, 720))

    bgcolor = THECOLORS["black"]
    r = kwargs["executor"].register
    r(partial(screen.fill, bgcolor), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)
    userdata = {
        'db_path': __file__ + ".sqlite3",
        'font': pygame.font.SysFont(None, 80),
        'bgcolor': bgcolor,
    }
    async with apg.open_nursery() as nursery:
        nursery.start(confirm_before_quitting(priority=0xFFFFFD00, font=userdata["font"], **kwargs))
        nursery.start(touch_indicator(color="grey", priority=0xFFFFFE00, **kwargs))
        nursery.start(SceneSwitcher().run(title_scene, priority=0xFFFFFA00, userdata=userdata, **kwargs))


async def confirm_before_quitting(*, priority, font, **kwargs: Unpack[apg.CommonParams]):
    quit = partial(kwargs["sdlevent"].wait, C.QUIT, priority=priority, consume=True)
    escape_key = partial(kwargs["sdlevent"].wait, C.KEYDOWN, priority=priority, filter=lambda e: e.key == C.K_ESCAPE, consume=True)
    while True:
        await apg.wait_any(quit(), escape_key())
        if await ask_yes_no_question("Quit the game?", priority=priority, font=font, **kwargs):
            apg.quit()


async def title_scene(*, scene_switcher, userdata, **kwargs: Unpack[apg.CommonParams]):
    draw_target = kwargs["draw_target"]
    target_rect = draw_target.get_rect()
    font = userdata['font']
    async with apg.open_nursery() as nursery:
        e_start = apg.Event()
        s = nursery.start
        s(anchor_layout(
            font.render("Whack a Human", True, "white", userdata["bgcolor"]).convert(draw_target),
            target_rect.scale_by(1.0, 0.5).move_to(y=target_rect.y),
            priority=0x100,
            **kwargs))
        s(ripple_button(
            button_image := font.render("Start", True, "white").convert_alpha(),
            button_image.get_rect(center=target_rect.scale_by(1.0, 0.5).move_to(bottom=target_rect.bottom).center).inflate(80, 80),
            on_click=e_start.fire,
            priority=0x100,
            **kwargs))
        while True:
            await e_start.wait()
            if Path(userdata['db_path']).exists():
                scene_switcher.switch_to(menu_scene, FadeTransition())
                await apg.sleep_forever()
            if not await ask_yes_no_question("The game will download images. Proceed?", priority=0xFFFFFB00, font=font, **kwargs):
                continue
            async with message_with_spinner("Downloading images...", priority=0xFFFFFB00, font=font, **kwargs):
                await kwargs["clock"].run_in_thread(lambda: init_database(userdata['db_path']), polling_interval=500)
            scene_switcher.switch_to(menu_scene, FadeTransition())
            await apg.sleep_forever()


async def menu_scene(*, scene_switcher, userdata, **kwargs: Unpack[apg.CommonParams]):
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
        scene_switcher.switch_to(next_scene, FadeTransition())
        await apg.sleep_forever()


async def game_scene(*, scene_switcher, userdata, **kwargs: Unpack[apg.CommonParams]):
    draw_target = kwargs["draw_target"]
    target_rect = draw_target.get_rect()
    font = userdata['font']
    clock = kwargs["clock"]
    images = load_images_from_database(userdata['db_path'])

    image = font.render("Running...", True, "white", userdata["bgcolor"]).convert(draw_target)
    dest = image.get_rect(center=target_rect.center)
    with kwargs["executor"].register(partial(draw_target.blit, image, dest), priority=0x100):
        async with clock.move_on_after(5000):
            await clock.anim_attrs(dest, y=dest.y - 80, duration=400)
            while True:
                await clock.anim_attrs(dest, y=dest.y + 160, duration=800)
                await clock.anim_attrs(dest, y=dest.y - 160, duration=800)
        scene_switcher.switch_to(title_scene, FadeTransition())
        await apg.sleep_forever()




if __name__ == "__main__":
    apg.run(main)
