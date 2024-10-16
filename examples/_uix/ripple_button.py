__all__ = ('ripple_button', )

from typing import Self, ContextManager
from contextlib import contextmanager
from functools import partial
import math

import asyncgui
from pygame import Surface, Rect, Color
import pygame.constants as C
import pygame.draw


def out_quad(p):
    '''
    https://kivy.org/doc/stable/api-kivy.animation.html#kivy.animation.AnimationTransition.out_quad
    '''
    return -1.0 * p * (p - 2.0)


@contextmanager
def tmp_clip(surface, rect):
    '''
    .. code-block::

        with tmp_clip(surface, rect):
            ...
    '''
    prev = surface.get_clip()
    surface.set_clip(rect)
    try:
        yield
    finally:
        surface.set_clip(prev)


def calc_minimum_enclosing_circle_radius(center_of_circle, rect: Rect, max=max, sqrt=math.sqrt):
    '''
    Calculates the radius of the minimum enclosing circle for a given rectangle.

    .. code-block::

        radius = calc_minimum_enclosing_circle_radius(center_of_circle, rect)

    .. warning::

        The ``center_of_circle`` must be inside the ``rect``; otherwise, the result will be incorrect.
    '''
    x, y = center_of_circle
    return sqrt(max(x - rect.x, rect.right - x) ** 2 + max(y - rect.y, rect.bottom - y) ** 2)


TOUCH_DOWN_EVENTS = (C.MOUSEBUTTONDOWN, C.FINGERDOWN, )


def block_touch_down_events(sdlevent, priority, *, filter=lambda e: True) -> ContextManager:
    '''
    Returns a context manager that blocks ``MOUSEBUTTONDOWN`` and  ``FINGERDOWN`` events.

    .. code-block::

        with block_touch_down_events(sdlevent, priority):
            ...

    .. warning::

        The context manager starts having the effect when it is created, not when its ``__enter__()`` method is called.
    '''
    return sdlevent.subscribe(TOUCH_DOWN_EVENTS, filter, priority)


class RippleEffect:
    __slots__ = ('radius', 'draw', )

    def __init__(self):
        self.draw = do_nothing

    def enable(self, draw_target, pos, radius, color):
        self.radius = radius
        self.draw = partial(self._draw, draw_target, pos, color, self)

    def disable(self):
        self.draw = do_nothing

    def _draw(pygame_draw_circle, draw_target, pos, color, self: Self):
        pygame_draw_circle(draw_target, color, pos, self.radius)

    _draw = partial(_draw, pygame.draw.circle)


def do_nothing(*args, **kwargs):
    pass


async def ripple_button(
        image: Surface, dest: Rect, priority, *, bgcolor="fuchsia", ripple_color=(80, 80, 80, 0),
        on_click=do_nothing, executor, sdlevent, clock, draw_target, **__):
    '''
    .. code-block::

        async with asyncpygame.open_nursery() as nursery:
            image = Surface(...)
            dest = Rect(...)
            click_event = asyncpygame.Event()

            nursery.start(ripple_button(image, dest, priority=..., on_click=click_event.fire, **common_params))

            # Waits for the button to be clicked.
            args, kwargs = await click_event.wait()

            # The events that caused the button to be clicked. These are either a pair of FINGERDOWN
            # and FINGERUP events or a pair of MOUSEBUTTONDOWN and MOUSEBUTTONUP events.
            e_down, e_up = args
    '''
    bgcolor = Color(bgcolor)
    ripple_color = Color(ripple_color) + Color(bgcolor)
    collidepoint = dest.collidepoint
    effect = RippleEffect()

    touch_down = partial(
        sdlevent.wait, C.MOUSEBUTTONDOWN, C.FINGERDOWN, priority=priority + 1, consume=True,
        filter=lambda e: (not getattr(e, 'touch', False)) and collidepoint(e.pos))
    mouse_button_up = partial(
        sdlevent.wait, C.MOUSEBUTTONUP, priority=priority + 1, consume=True,
        filter=lambda e: e.button == e_down.button)
    finger_up = partial(
        sdlevent.wait, C.FINGERUP, priority=priority + 1, consume=True,
        filter=lambda e: e.finger_id == e_down.finger_id)

    with (
        executor.register(partial(_draw, tmp_clip, image, image.get_rect(), bgcolor, draw_target, dest, effect), priority),
        block_touch_down_events(sdlevent, priority, filter=lambda e: collidepoint(e.pos)),
    ):
        while True:
            e_down = await touch_down()
            effect.enable(draw_target, e_down.pos, 0, ripple_color)
            touch_up = mouse_button_up if e_down.type == C.MOUSEBUTTONDOWN else finger_up
            async with asyncgui.run_as_main(touch_up()) as touch_up_tracker:
                await clock.anim_attrs(effect, radius=calc_minimum_enclosing_circle_radius(e_down.pos, dest), duration=600, transition=out_quad)
            e_up = touch_up_tracker.result
            if collidepoint(e_up.pos):
                on_click(e_down, e_up)
            effect.disable()


def _draw(tmp_clip, image, image_rect, bgcolor, draw_target, dest, effect):
    with tmp_clip(draw_target, dest):
        draw_target.fill(bgcolor)
        effect.draw()
        image_rect.center = dest.center
        draw_target.blit(image, image_rect)
