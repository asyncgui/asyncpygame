from typing import Unpack
from functools import partial

import pygame
from pygame.colordict import THECOLORS
from pygame import Rect, Vector2, Color, Surface

import asyncpygame as apg


BLACK = Color("black")
WHITE = Color("white")


def generate_ball_image(*, color, size) -> Surface:
    img = Surface((size, size))
    bgcolor = WHITE if color == BLACK else BLACK
    img.fill(bgcolor)
    pygame.draw.ellipse(img, color, img.get_rect())
    img = img.convert()
    img.set_colorkey(bgcolor)
    return img


async def bouncing_ball(*, initial_pos, size: tuple, space: Rect, color, velocity: Vector2, **kwargs: Unpack[apg.CommonParams]):
    ball_img = generate_ball_image(color=color, size=size)
    dest = ball_img.get_rect(center=initial_pos)
    draw_func = partial(kwargs["draw_target"].blit, ball_img, dest)
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
            nursery.start(bouncing_ball(
                initial_pos=screen_rect.center,
                size=randint(20, 150),
                space=screen_rect,
                color=Color(randint(0, 255), randint(0, 255), randint(0, 255)),
                velocity=Vector2(randint(-150, 150), randint(-150, 150)),
                priority=priority,
                **kwargs
            ))
            priority += 1


if __name__ == "__main__":
    apg.run(main)
