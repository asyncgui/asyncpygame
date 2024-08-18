'''
波紋アニメーションを持つボタン。生成後はボタンの文字列やフォントのような設定値を変えられないのであまり本格的ではない。
そうした理由としては本格的な物にしようとするとexampleの域に収まらないコード量になるから。
'''

from functools import partial
from dataclasses import dataclass

import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
from pygame import Surface, Color, Rect
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP
import asyncpygame as ap


def do_nothing(*args):
    pass


def out_quad(p):
    '''
    https://kivy.org/doc/stable/api-kivy.animation.html#kivy.animation.AnimationTransition.out_quad
    '''
    return -1.0 * p * (p - 2.0)


def calc_minimum_enclosing_circle_radius(center_of_circle, rect: Rect):
    '''
    Calculates the radius of the minimum enclosing circle for a given rectangle.

    .. warning::

        The ``center_of_circle`` point must be within the ``rect``.
    '''
    x, y = center_of_circle
    return (max(x - rect.x, rect.right - x) ** 2 + max(y - rect.y, rect.bottom - y) ** 2) ** 0.5


@dataclass(kw_only=True)
class RippleEffect:
    draw_target: Surface
    color: Color
    pos: tuple | pygame.Vector2
    radius: int
    clip: Rect

    def draw(self):
        self.draw_target.set_clip(self.clip)
        pygame.draw.circle(self.draw_target, self.color, self.pos, self.radius)
        self.draw_target.set_clip(None)


async def ripple_button(
    *, draw_target: Surface, text='', font, dst: Rect,
    fgcolor=COLORS["white"], bgcolor=COLORS["darkgreen"], ripple_color=(80, 80, 80, 0),
    on_press=do_nothing, on_release=do_nothing,
    clock: ap.Clock, sdlevent: ap.SDLEvent, executor: ap.PriorityExecutor, priority, **kwargs
):
    text_img = font.render(text, True, fgcolor).convert_alpha()
    text_dst = text_img.get_rect(center=dst.center)

    button_down = partial(sdlevent.wait, MOUSEBUTTONDOWN, filter=lambda e: dst.collidepoint(e.pos), priority=priority, consume=True)
    button_up = partial(sdlevent.wait, MOUSEBUTTONUP, filter=lambda e: e_down.button == e.button, priority=priority, consume=True)
    with (
        executor.register(partial(pygame.draw.rect, draw_target, bgcolor, dst), priority=priority),
        executor.register(partial(draw_target.blit, text_img, text_dst), priority=priority + 2),
    ):
        while True:
            e_down = await button_down()
            on_press(e_down)
            effect = RippleEffect(draw_target=draw_target, color=Color(bgcolor) + Color(ripple_color), pos=e_down.pos, radius=0, clip=dst)
            with executor.register(effect.draw, priority=priority + 1):
                async with ap.run_as_main(button_up()) as button_up_tracker:
                    await clock.anim_attrs(effect, radius=calc_minimum_enclosing_circle_radius(e_down.pos, dst), duration=1000, transition=out_quad)
                e_up = button_up_tracker.result
                on_release(e_up, dst.collidepoint(e_up.pos))


async def main(*, executor: ap.PriorityExecutor, **kwargs):
    pygame.init()
    pygame.display.set_caption("Ripple Button")
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 100)

    executor.register(partial(screen.fill, COLORS["black"]), priority=0)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)

    async with ap.open_nursery() as nursery:
        nursery.start(ripple_button(
            draw_target=screen, text="PyGame", font=font, dst=Rect(100, 100, 300, 200), on_press=print, on_release=print,
            executor=executor, priority=0x100, **kwargs,
        ))
        nursery.start(ripple_button(
            draw_target=screen, text="Python", font=font, dst=Rect(280, 240, 300, 200), on_press=print, on_release=print,
            executor=executor, priority=0x200, bgcolor=COLORS["blue3"], **kwargs,
        ))


if __name__ == "__main__":
    ap.run(main)
