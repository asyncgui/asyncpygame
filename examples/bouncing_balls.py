from typing import Unpack
from functools import partial

import pygame
from pygame.colordict import THECOLORS
from pygame import Rect, Vector2, Color

import asyncpygame as apg


async def bouncing_ball(*, dest: Rect, space: Rect, color, velocity: Vector2, **kwargs: Unpack[apg.CommonParams]):
    draw_func = partial(pygame.draw.ellipse, kwargs["draw_target"], color, dest)
    with kwargs["executor"].register(draw_func, kwargs["priority"]):
        async for dt in kwargs["clock"].anim_with_dt():
            dest.move_ip(velocity * (dt / 1000.0))
            if not dest.colliderect(space):
                return
            if dest.left < space.left or dest.right > space.right:
                velocity.x = -velocity.x
            if dest.top < space.top or dest.bottom > space.bottom:
                velocity.y = -velocity.y


async def main(**kwargs: Unpack[apg.CommonParams]):
    from random import randint
    pygame.init()
    pygame.display.set_caption("Bouncing Balls")

    kwargs["draw_target"] = screen = pygame.display.set_mode((1280, 720))

    r = kwargs["executor"].register
    r(partial(screen.fill, THECOLORS["black"]), priority=0)
    r(pygame.display.flip, priority=0xFFFFFF00)

    async with apg.open_nursery() as nursery:
        clock = kwargs["clock"]
        priority = 0x100
        screen_rect = screen.get_rect()
        while True:
            await clock.sleep(randint(1000, 2000))
            ball_size = randint(20, 150)
            nursery.start(bouncing_ball(
                dest=Rect(0, 0, ball_size, ball_size).move_to(center=screen_rect.center),
                space=screen_rect,
                color=Color(randint(0, 255), randint(0, 255), randint(0, 255)),
                velocity=Vector2(randint(-150, 150), randint(-150, 150)),
                priority=priority,
                **kwargs
            ))
            priority += 1


if __name__ == "__main__":
    apg.run(main)
