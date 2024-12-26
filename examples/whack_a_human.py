# Credits:
#    Image: いらすとや (https://www.irasutoya.com/)
#    Sound: 魔王魂 (https://maou.audio/)
#
# Video footage:
#    https://youtu.be/9T16rHCS_6M

from typing import Unpack
from types import SimpleNamespace
from collections.abc import Iterator
from functools import partial
from contextlib import closing, nullcontext
import itertools
from dataclasses import dataclass
import math

import io
from os import PathLike
from pathlib import Path
import sqlite3

import requests
from PIL import Image
import pygame
from pygame.mixer import Sound
from pygame import Rect, Surface
import pygame.font
from pygame.colordict import THECOLORS
import pygame.constants as C

import asyncpygame as apg
from asyncpygame.scene_switcher import SceneSwitcher, FadeTransition
from _uix.touch_indicator import touch_indicator
from _uix.inapp_mouse_cursor import inapp_mouse_cursor
from _uix.anchor_layout import anchor_layout
from _uix.ripple_button import ripple_button
from _uix.modal_dialog import ask_yes_no_question, message_with_spinner
from _utils.convert_sound import convert_sound


def with_isolated_alpha(s: Surface) -> Surface:
    return s.subsurface(s.get_rect())


def download_images() -> dict[str, bytes]:
    URLS = (
        ("neutral", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgh1PA4Bjg2mGnrFcuufNP1WP2kPRqXMRJQSz-fHxBxRYSGjwZQmbkMEe495vP_23LwafvGR2her8vQhM836BMYvJvKCJVkH9NvHTJ5gdoyAz5bFuQIW7SUDX7gTDJC7qIsqyE9vhuU9Wg/s400/figure_standing.png"),
        ("square-off", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5w726e-ADC9DDJdytCRtdPAHogCk3CLTNF-2N3RglZbTgf_Ad1-2N4rQngxYE8IeDlz0E-fhIJOsOGoisP-O1J66KVTFFs9DJ6b7Vd4YyXGkPWNFpmNn0Kl7IkiPhZcnomsfrnDYur4k/s400/figure_fighting_pose.png"),
        ("attack", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiuUsvvOwAK4_FlBL5itKyfcgQhzpOhsLZCUFHWbgZZVUl6-Km5hwFIiF8fKCJ2zSdQD5sJpqsBIWEOqThdmc6RUb1FHCtxV7AwyRFX4keVgnm0AN6I-6iDI_yrbWYHLsi2qUUTFLMVySI/s400/figure_fighting_punch.png"),
        ("carry", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgsErzqpQO9Z87VBwkeb-G_3UrQVHBBAqFR5ONIvwD6DKnjVvCJFFdyqPECypqzKoN1BOqd7e1T9D-L_1-9zYpYIydZZdsq3Cs3bu3p4_7WZUmE9hsP5FQ0gvgQ-wzbG7SoZmmXxMnNtWw/s400/figure_box_carrying.png"),
        ("gift", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh0evgMM9Ax4RyinjeIOCA_6vVsgFmQwyEfuEnm95a3uv6gWN5QSVb3SS9wqYOHB3sAeno92N_vdS_C160UL8ILjIxe4naoHSsey4dbxtAkLcyeGz7c-e3dDY91nB-9JXbSGyGehDgJuRQq/s400/present_box.png"),
        ("clap", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiYu-t8WjYxwde_VFWPsxSSg6ux32QZtPmP6BFlqrlcZmjiP0bCMO_uwcLwliT9YKSY-Pdk7YLWn-d1tEAeJbvfXAchJ-5vl0tYeWa5cFDSbQIGZ0t0dpH8DQPZ000CbHgJkdzxwYKpnf7K/s450/figure_hakusyu.png"),
        ("orz", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgVV4gxY5N__pAU4EYXRD2fNav5FvKlgfZmhBwYHLdBqnj_2rio9GKWvBstAW94lT-Ts63tCOI0ySdm_lfGlxwfCYBjw-J1Pq9V1LjUFUSfnOb4lAMUu6BN07q4Iv-yIZWGVrLw81IAXyE/s400/figure_zasetsu.png"),
        ("robot", r"https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhsQ2aihomoPrWm1WsTN1cbl2e4mOBuUNCsZmjq_KWTHdYjf19Wkw3b8PEWpxC4owjzMypxSP-dNP5kkLQPt9MjrRiKHuFu94o_4kZpi7uDcvCOkT3IbqiiPCDAzzNv2XilT5BjDMxJTWc/s400/omocha_robot.png"),
    )
    with requests.Session() as s:
        s.headers["Referer"] = "https://www.irasutoya.com/"
        return {name: s.get(url).content for name, url in URLS}


def download_sounds() -> dict[str, bytes]:
    URLS = (
        ("hit", r"https://maou.audio/sound/se/maou_se_battle07.wav"),
        ("get-hit", r"https://maou.audio/sound/se/maou_se_battle18.wav"),
        ("gift", r"https://maou.audio/sound/se/maou_se_system46.wav"),
    )
    with requests.Session() as s:
        s.headers["Referer"] = "https://maou.audio/"
        return {name: s.get(url).content for name, url in URLS}


def crop_image(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data))
    cropped = img.crop(img.getbbox())
    with io.BytesIO() as f:
        cropped.save(f, format="PNG")
        return f.getvalue()


def init_database(db_path: PathLike):
    with sqlite3.connect(db_path) as conn, closing(conn.cursor()) as cur:
        cur.executescript("""
            CREATE TABLE Images(
                name TEXT NOT NULL UNIQUE,
                image BLOB NOT NULL,
                PRIMARY KEY (name)
            );
            CREATE TABLE Sounds(
                name TEXT NOT NULL UNIQUE,
                sound BLOB NOT NULL,
                PRIMARY KEY (name)
            );
        """)
        images = download_images()
        cur.executemany(
            "INSERT INTO Images(name, image) VALUES(?, ?)",
            ((name, crop_image(image)) for name, image in images.items()),
        )
        sounds = download_sounds()
        cur.executemany(
            "INSERT INTO Sounds(name, sound) VALUES(?, ?)",
            ((name, convert_sound(sound)) for name, sound in sounds.items()),
        )


def load_images(cur: sqlite3.Cursor) -> dict[str, Surface]:
    return {
        name: (s := pygame.image.load(io.BytesIO(image)).convert(), s.set_colorkey(s.get_at((0, 0)))) and s
        for name, image in cur.execute("SELECT name, image FROM Images")
    }


def load_sounds(cur: sqlite3.Cursor) -> dict[str, Sound]:
    return {
        name: Sound(sound)
        for name, sound in cur.execute("SELECT name, sound FROM Sounds")
    }


@dataclass(kw_only=True, slots=True)
class UserData:
    '''Stuff that are shared between scenes'''
    db_path: Path
    font: pygame.font.Font
    bgcolor: tuple
    score_color: tuple
    game_duration: int = 30_000  # milliseconds
    last_game_score: int = None
    images: dict[str, Surface] = None
    sounds: dict[str, Sound] = None
    displays_hurt_boxes: bool = False


async def main(**kwargs: Unpack[apg.CommonParams]):
    pygame.mixer.init()
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.event.set_blocked(None)
    pygame.event.set_allowed((C.QUIT, C.MOUSEBUTTONDOWN, C.MOUSEBUTTONUP, C.MOUSEMOTION, C.KEYDOWN, ))
    pygame.display.set_caption("Whack a Human")
    kwargs["draw_target"] = screen = pygame.display.set_mode((1280, 720))

    bgcolor = THECOLORS["black"]
    score_color = THECOLORS["lightslateblue"]
    r = kwargs["executor"].register
    r(partial(screen.fill, bgcolor), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    font = pygame.font.SysFont(None, 80)
    images = {}
    for name, text in {"pts": "pts", "plus_one": "+1", "plus_three": "+3", "minus_one": "-1", }.items():
        img = font.render(text, False, score_color, bgcolor).convert(screen)
        img.set_colorkey(bgcolor)
        images[name] = img
    red_surface = Surface(screen.get_size()).convert(screen)
    red_surface.fill("red")
    images["red_surface"] = red_surface
    userdata = UserData(
        db_path=Path(__file__ + ".sqlite3"),
        font=font,
        bgcolor=bgcolor,
        score_color=score_color,
        images=images,
    )
    async with apg.open_nursery() as nursery:
        s = nursery.start
        s(confirm_and_quit(priority=0xFFFFFD00, font=font, **kwargs))
        s(touch_indicator(color="lime", line_width=8, priority=0xFFFFFE00, **kwargs))
        s(inapp_mouse_cursor(color="olive", priority=0xFFFFFE01, **kwargs))
        s(SceneSwitcher().run(title_scene, priority=0xFFFFFA00, userdata=userdata, **kwargs))


async def confirm_and_quit(*, priority, font, **kwargs: Unpack[apg.CommonParams]):
    wait = kwargs["sdlevent"].wait
    quit = partial(wait, C.QUIT, priority=priority, consume=True)
    escape_key = partial(wait, C.KEYDOWN, priority=priority, filter=lambda e: e.key == C.K_ESCAPE, consume=True)
    while True:
        await apg.wait_any(quit(), escape_key())
        if await ask_yes_no_question(
                "Quit the game?", priority=priority, font=font,
                dialog_size=kwargs["draw_target"].get_rect().scale_by(0.4, 0.4).size, **kwargs):
            apg.quit()


async def title_scene(*, switcher, userdata: UserData, **kwargs: Unpack[apg.CommonParams]):
    draw_target = kwargs["draw_target"]
    target_rect = draw_target.get_rect()
    font = userdata.font
    async with apg.open_nursery() as nursery:
        e_start = apg.Event()
        s = nursery.start
        s(anchor_layout(
            font.render("Whack a Human", True, "white", userdata.bgcolor).convert(draw_target),
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
            if not userdata.db_path.exists():
                if await ask_yes_no_question("Needs to download data. Proceed?", priority=0xFFFFFB00, font=font,
                                             dialog_size=target_rect.scale_by(0.8, 0.4).size, **kwargs):
                    async with message_with_spinner("Downloading...", priority=0xFFFFFB00, font=font,
                                                    dialog_size=target_rect.scale_by(0.4, 0.6).size, **kwargs):
                        await kwargs["clock"].run_in_thread(lambda: init_database(userdata.db_path), polling_interval=1000)
                else:
                    continue
            images = userdata.images
            with sqlite3.connect(userdata.db_path) as conn, closing(conn.cursor()) as cur:
                images.update(load_images(cur))
                userdata.sounds = load_sounds(cur)
            images["gift"] = pygame.transform.scale(images["gift"], (200, 200))
            switcher.switch_to(game_scene, FadeTransition())
            await apg.sleep_forever()


def calc_row_positions(base_pos: tuple, hole_size: tuple, spacing: tuple) -> Iterator[tuple]:
    w, h = hole_size
    spacing_x, spacing_y = spacing
    base_x, base_y = base_pos
    return zip(
        itertools.cycle((base_x, base_x + (w + spacing_x) / 2)),
        itertools.accumulate(itertools.repeat(h + spacing_y), initial=base_y),
    )


def test_calc_row_positions():
    pos_iter = calc_row_positions(base_pos=(50, 100), hole_size=(200, 100), spacing=(20, 10))
    assert list(itertools.islice(pos_iter, 4)) == [(50, 100), (160, 210), (50, 320), (160, 430), ]


def calc_hole_positions(*, base_pos: tuple, hole_size: tuple, spacing: tuple, n_rows: int, n_cols: int) -> Iterator[tuple]:
    it = itertools
    for row_x, row_y in it.islice(calc_row_positions(base_pos, hole_size, spacing), n_rows):
        for col_x in it.accumulate(it.repeat(hole_size[0] + spacing[0], n_cols - 1), initial=row_x):
            yield col_x, row_y


def test_calc_hole_positions():
    pos_iter = calc_hole_positions(base_pos=(50, 100), hole_size=(200, 100), spacing=(20, 10), n_rows=3, n_cols=3)
    assert list(pos_iter) == [
        (50, 100), (270, 100), (490, 100),
        (160, 210), (380, 210), (600, 210),
        (50, 320), (270, 320), (490, 320),
    ]


class GameScore:
    def __init__(self, *, value=0, topright, userdata: UserData, **kwargs: Unpack[apg.CommonParams]):
        self.value = value
        self._drawn_value = None
        self._image = None
        self.draw = partial(self.__class__._draw, self, str, kwargs["draw_target"], Rect(*topright, 0, 0), userdata.font, userdata.score_color, userdata.bgcolor)

    def _draw(self, str, draw_target, dest, font, score_color, bgcolor):
        if self._drawn_value != self.value:
            self._image = image = font.render(str(self.value), False, score_color, bgcolor).convert(draw_target)
            image.set_colorkey(bgcolor)
            dest.update(image.get_rect(topright=dest.topright))
            self._drawn_value = self.value
        else:
            image = self._image
        draw_target.blit(image, dest)


@dataclass(kw_only=True, slots=True)
class GameSpeed:
    value: float = 1.0  # smaller == faster


async def pop_out_enemy(
        score: GameScore, speed: GameSpeed, inactive_holes: list, *, pos: tuple, hole_color=THECOLORS["grey10"],
        hole_size: tuple, userdata: UserData, **kwargs: Unpack[apg.CommonParams]):
    speed = speed.value
    images = userdata.images
    sounds = userdata.sounds
    priority = pos[1]  # 下にある物ほど手前に表示させたい。
    draw_target = kwargs["draw_target"]
    clock = kwargs["clock"]
    anim_attrs = clock.anim_attrs
    sleep = clock.sleep
    register = kwargs["executor"].register
    hurt_box = Rect(0, 0, 0, 0)
    user_hits_enemy = partial(
        kwargs["sdlevent"].wait, C.MOUSEBUTTONDOWN, priority=priority, consume=True,
        filter=lambda e, cp=hurt_box.collidepoint: cp(e.pos),
    )
    if userdata.displays_hurt_boxes:
        draw = partial(pygame.draw.rect, draw_target, THECOLORS["red"], hurt_box, width=2)
        display_hurt_box = partial(register, draw, priority + 2)
        del draw
    else:
        display_hurt_box = nullcontext

    hole_dest = Rect(*pos, 0, 0)
    with register(partial(pygame.draw.ellipse, draw_target, hole_color, hole_dest), priority):
        await anim_attrs(hole_dest, size=hole_size, x=pos[0] - hole_size[0] / 2, y=pos[1] - hole_size[1] / 2, duration=500 * speed)
        enemy_img = with_isolated_alpha(images["neutral"])
        enemy_dest = enemy_img.get_rect(midtop=pos)
        enemy_clip = enemy_img.get_rect(height=0)
        hurt_box.update(enemy_dest)
        hurt_box.height = 0
        with register(partial(draw_target.blit, enemy_img, enemy_dest, enemy_clip), priority + 1) as draw_enemy_req:
            with display_hurt_box():
                async with apg.move_on_when(user_hits_enemy()) as hit_tracker:
                    await apg.wait_all(
                        anim_attrs(enemy_dest, bottom=enemy_dest.top, duration=500 * speed),
                        anim_attrs(enemy_clip, height=enemy_dest.height, duration=500 * speed),
                        anim_attrs(hurt_box, height=enemy_dest.height, top=enemy_dest.top - enemy_dest.height, duration=500 * speed),
                    )
                    await sleep(1000 * speed)
                    enemy_img = with_isolated_alpha(images["square-off"])
                    enemy_dest = enemy_img.get_rect(midbottom=enemy_dest.midbottom)
                    hurt_box.update(enemy_dest)
                    draw_enemy_req.callback = partial(draw_target.blit, enemy_img, enemy_dest)
                    await sleep(1000 * speed)
            if hit_tracker.finished:
                score.value += 1
                sounds["hit"].play()
                plus_one = with_isolated_alpha(images["plus_one"])
                with register(partial(draw_target.blit, plus_one, plus_one.get_rect(midtop=enemy_dest.midtop).move(0, 30)), priority + 0xFFFF0000):
                    async for v in clock.interpolate(255, 0, duration=500):
                        enemy_img.set_alpha(v)
                        plus_one.set_alpha(v)
            else:
                score.value -= 1
                sounds["get-hit"].play()
                enemy_img = images["attack"]
                enemy_clip = enemy_img.get_rect()
                enemy_dest = enemy_clip.move_to(midbottom=enemy_dest.midbottom)
                draw_enemy_req.callback = partial(draw_target.blit, enemy_img, enemy_dest, enemy_clip)
                red_surface = with_isolated_alpha(images["red_surface"])
                minus_one = with_isolated_alpha(images["minus_one"])
                with (
                    register(partial(draw_target.blit, red_surface), priority + 0xFFFF0000),
                    register(partial(draw_target.blit, minus_one, minus_one.get_rect(midtop=enemy_dest.midtop).move(30, 30)), priority + 0xFFFF0000),
                ):
                    red_surface.set_alpha(60)
                    async for p in clock.anim_with_ratio(base=500):
                        if p >= 1.0:
                            break
                        p = 1.0 - p
                        red_surface.set_alpha(p * 60)
                        minus_one.set_alpha(p * 255)
                await apg.wait_all(
                    anim_attrs(enemy_dest, top=enemy_dest.bottom, duration=500 * speed),
                    anim_attrs(enemy_clip, height=0, duration=500 * speed),
                )
        await anim_attrs(hole_dest, size=(0, 0), topleft=pos, duration=300 * speed)
    inactive_holes.append(pos)


async def pop_out_ally(
        score: GameScore, speed: GameSpeed, inactive_holes: list, *, pos: tuple, hole_color=THECOLORS["grey10"],
        hole_size: tuple, userdata: UserData, **kwargs: Unpack[apg.CommonParams]):
    speed = speed.value
    images = userdata.images
    sounds = userdata.sounds
    priority = pos[1]  # 下にある物ほど手前に表示させたい。
    draw_target = kwargs["draw_target"]
    clock = kwargs["clock"]
    anim_attrs = clock.anim_attrs
    sleep = clock.sleep
    register = kwargs["executor"].register
    hurt_box = Rect(0, 0, 0, 0)
    user_hits_ally = partial(
        kwargs["sdlevent"].wait, C.MOUSEBUTTONDOWN, priority=priority, consume=True,
        filter=lambda e, cp=hurt_box.collidepoint: cp(e.pos),
    )
    if userdata.displays_hurt_boxes:
        draw = partial(pygame.draw.rect, draw_target, THECOLORS["red"], hurt_box, width=2)
        display_hurt_box = partial(register, draw, priority + 2)
        del draw
    else:
        display_hurt_box = nullcontext

    hole_dest = Rect(*pos, 0, 0)
    with register(partial(pygame.draw.ellipse, draw_target, hole_color, hole_dest), priority):
        await anim_attrs(hole_dest, size=hole_size, x=pos[0] - hole_size[0] / 2, y=pos[1] - hole_size[1] / 2, duration=500 * speed)
        ally_img = with_isolated_alpha(images["neutral"])
        ally_dest = ally_img.get_rect(midtop=pos)
        ally_clip = ally_img.get_rect(height=0)
        hurt_box.update(ally_dest)
        hurt_box.height = 0
        with register(partial(draw_target.blit, ally_img, ally_dest, ally_clip), priority + 1) as draw_ally_req:
            with display_hurt_box():
                async with apg.move_on_when(user_hits_ally()) as hit_tracker:
                    await apg.wait_all(
                        anim_attrs(ally_dest, bottom=ally_dest.top, duration=500 * speed),
                        anim_attrs(ally_clip, height=ally_dest.height, duration=500 * speed),
                        anim_attrs(hurt_box, height=ally_dest.height, top=ally_dest.top - ally_dest.height, duration=500 * speed),
                    )
                    await sleep(1000 * speed)
                    ally_img = with_isolated_alpha(images["carry"])
                    ally_dest = ally_img.get_rect(midbottom=ally_dest.midbottom)
                    hurt_box.update(ally_dest)
                    draw_ally_req.callback = partial(draw_target.blit, ally_img, ally_dest)
                    await sleep(1000 * speed)
            if hit_tracker.finished:
                sounds["hit"].play()
                async for v in clock.interpolate(255, 0, duration=500):
                    ally_img.set_alpha(v)
            else:
                score.value += 3
                sounds["gift"].play()
                ally_img = images["gift"]
                ally_clip = ally_img.get_rect()
                ally_dest = ally_clip.move_to(midbottom=ally_dest.midbottom)
                draw_ally_req.callback = partial(draw_target.blit, ally_img, ally_dest, ally_clip)
                plus_three = with_isolated_alpha(images["plus_three"])
                with register(partial(draw_target.blit, plus_three, plus_three.get_rect(midbottom=ally_dest.midtop)), priority + 0xFFFF0000):
                    async for v in clock.interpolate(255, 0, duration=500):
                        plus_three.set_alpha(v)
                await apg.wait_all(
                    anim_attrs(ally_dest, top=ally_dest.bottom, duration=500 * speed),
                    anim_attrs(ally_clip, height=0, duration=500 * speed),
                )
        await anim_attrs(hole_dest, size=(0, 0), topleft=pos, duration=300 * speed)
    inactive_holes.append(pos)


def _draw_game_timer(ctx, pygame_draw_arc, draw_target, color, dest, start_angle):
    pygame_draw_arc(draw_target, color, dest, start_angle, ctx.stop_angle, 10_000)


async def game_timer(dest: Rect, *, duration, color=THECOLORS["ivory"], priority, **kwargs: Unpack[apg.CommonParams]):
    start_angle = math.tau / 4
    ctx = SimpleNamespace(stop_angle=start_angle + math.tau)
    draw = partial(_draw_game_timer, ctx, pygame.draw.arc, kwargs["draw_target"], color, dest, start_angle)
    with kwargs["executor"].register(draw, priority):
        await kwargs["clock"].anim_attrs(ctx, stop_angle=start_angle, duration=duration)


async def game_scene(*, switcher, userdata: UserData, **kwargs: Unpack[apg.CommonParams]):
    from random import randint, random
    clock = kwargs["clock"]
    draw_target = kwargs["draw_target"]
    register = kwargs["executor"].register
    hole_size = (200, 100)
    inactive_holes = list(calc_hole_positions(base_pos=(160, 400), hole_size=hole_size, spacing=(60, 20), n_rows=3, n_cols=4))
    timer_dest = Rect(0, 0, 64, 64)
    timer_dest.topright = draw_target.get_rect().topright
    timer_dest.move_ip(-10, 10)
    pts = userdata.images["pts"]
    pts_dest = pts.get_rect(topright=timer_dest.topleft)
    pts_dest.move_ip(-10, 0)
    score = GameScore(value=0, userdata=userdata, topright=(pts_dest.x - 10, pts_dest.y), **kwargs)
    speed = GameSpeed(value=1.0)
    hud_priority = 0xFFFF0001
    actions = (pop_out_enemy, pop_out_ally, )

    async with apg.open_nursery() as nursery:
        nursery.start(clock.anim_attrs(speed, value=0.3, duration=userdata.game_duration))  # Increase the pace of the game as time goes by
        with (
            register(partial(draw_target.blit, pts, pts_dest), hud_priority),
            register(score.draw, hud_priority),
        ):
            async with apg.move_on_when(game_timer(timer_dest, duration=userdata.game_duration, priority=hud_priority, **kwargs)):
                while True:
                    await clock.sleep(800 * speed.value)
                    if not inactive_holes:
                        continue
                    hole = inactive_holes.pop(randint(0, len(inactive_holes) - 1))
                    nursery.start(actions[random() > 0.8](score, speed, inactive_holes, hole_size=hole_size, pos=hole, userdata=userdata, **kwargs))
        userdata.last_game_score = score.value
        switcher.switch_to(result_scene, FadeTransition(overlay_color=THECOLORS["white"], out_duration=1000, interval=1000, in_duration=500))
        await apg.sleep_forever()


async def result_scene(*, switcher, userdata: UserData, **kwargs: Unpack[apg.CommonParams]):
    render = userdata.font.render
    draw_target = kwargs["draw_target"]
    target_rect = draw_target.get_rect()
    if userdata.last_game_score > 60:
        message = "You must have cheated!"
        image = userdata.images["robot"]
    elif userdata.last_game_score > 40:
        message = "Awesome"
        image = userdata.images["clap"]
    else:
        message = "Try Harder"
        image = userdata.images["orz"]
    async with apg.open_nursery() as nursery:
        s = nursery.start
        s(anchor_layout(
            render(f"{userdata.last_game_score}pts", True, userdata.score_color, userdata.bgcolor).convert(draw_target),
            dest := target_rect.scale_by(1.0, 0.15).move_to(y=target_rect.y + 20),
            priority=0x100,
            **kwargs))
        s(anchor_layout(
            render(message, True, "white", userdata.bgcolor).convert(draw_target),
            dest := dest.move_to(y=dest.bottom),
            priority=0x100,
            **kwargs))
        s(anchor_layout(
            image,
            target_rect.scale_by(1.0, 0.7).move_to(y=dest.bottom),
            priority=0x100,
            **kwargs))
        await kwargs["sdlevent"].wait(C.MOUSEBUTTONDOWN, priority=0x100)
        switcher.switch_to(title_scene, FadeTransition())
        await apg.sleep_forever()


if __name__ == "__main__":
    test_calc_row_positions()
    test_calc_hole_positions()
    apg.run(main, auto_quit=False)
