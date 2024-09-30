__all__ = ('RippleButton', )

from typing import Self, ContextManager
from contextlib import contextmanager
from functools import partial
from collections.abc import Awaitable
import math

from asyncgui import Nursery, Event, run_as_main
from pygame import Surface, Rect, Color
from pygame import constants as C
import pygame.draw


def out_quad(p):
    '''
    https://kivy.org/doc/stable/api-kivy.animation.html#kivy.animation.AnimationTransition.out_quad
    '''
    return -1.0 * p * (p - 2.0)


@contextmanager
def clip(surface, rect):
    '''
    .. code-block::

        with clip(surface, rect):
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

    def __init__(self, pos, radius, color):
        self.radius = radius
        self.draw = partial(self._draw, color, pos, self)

    def _draw(pygame_draw_circle, color, pos, self: Self, draw_target):
        pygame_draw_circle(draw_target, color, pos, self.radius)

    _draw = partial(_draw, pygame.draw.circle)


class RippleButton:
    '''
    .. code-block::

        async with asyncpygame.open_nursery() as nursery:
            image = Surface(...)
            dest = Rect(...)
            button = RippleButton(nursery, image, dest, **common_params)

            # Waits for the button to be clicked.
            await button.to_be_clicked()

            # You can change its image anytime.
            button.image = another_image

            # You can move or resize the button by updating the ``dest``.
            dest.width = ...
            dest.right = ...

            # but you cannot assign another Rect instance to the button.
            button.dest = another_rect  # NOT ALLOWED

    '''
    def __init__(self, owner: Nursery, image: Surface, dest: Rect,
                 *, bgcolor="fuchsia", ripple_color=(80, 80, 80, 0), **common_params):
        '''
        :param owner: RippleButton cannot outlive its owner. When the owner is closed, the button is destroyed.
        '''
        self._click_event = Event()
        self._draw_ripple_effect = None
        self._dest = dest
        self.image = image
        self._main_task = owner.start(self._main(bgcolor, ripple_color, **common_params), daemon=True)

    def kill(self):
        self._main_task.cancel()

    @property
    def dest(self) -> Rect:
        return self._dest

    async def to_be_clicked(self) -> Awaitable[tuple[Event, Event]]:
        '''
        Waits for the button to be clicked.

        .. code-block::

            e_down, e_up = await button.to_be_clicked()

        The ``e_down`` and ``e_up`` above are :class:`pygame.event.Event` instances that caused the click, and
        they are either a pair of ``MOUSEBUTTONDOWN`` and ``MOUSEBUTTONUP`` or a pair of ``FINGERDOWN`` and ``FINGERUP``.
        '''
        return (await self._click_event.wait())[0]

    async def _main(self, bgcolor, ripple_color, *, priority, draw_target, executor, clock, sdlevent, **unused):
        bgcolor = Color(bgcolor)
        ripple_color = Color(ripple_color) + Color(bgcolor)
        dest = self._dest
        click_event = self._click_event

        touch_down = partial(
            sdlevent.wait, C.MOUSEBUTTONDOWN, C.FINGERDOWN, priority=priority + 1, consume=True,
            filter=lambda e, getattr=getattr, dest=dest: (not getattr(e, 'touch', False)) and dest.collidepoint(e.pos))
        mouse_button_up = partial(
            sdlevent.wait, C.MOUSEBUTTONUP, priority=priority + 1, consume=True,
            filter=lambda e: e.button == e_down.button)
        finger_up = partial(
            sdlevent.wait, C.FINGERUP, priority=priority + 1, consume=True,
            filter=lambda e: e.finger_id == e_down.finger_id)

        with (
            executor.register(partial(self._draw, bgcolor, draw_target, dest, self), priority=priority),
            block_touch_down_events(sdlevent, priority, filter=lambda e, dest=dest: dest.collidepoint(e.pos)),
        ):
            while True:
                e_down = await touch_down()
                effect = RippleEffect(e_down.pos, 0, ripple_color)
                self._draw_ripple_effect = effect.draw
                touch_up = mouse_button_up if e_down.type == C.MOUSEBUTTONDOWN else finger_up
                async with run_as_main(touch_up()) as touch_up_tracker:
                    await clock.anim_attrs(effect, radius=calc_minimum_enclosing_circle_radius(e_down.pos, dest), duration=600, transition=out_quad)
                e_up = touch_up_tracker.result
                if dest.collidepoint(e_up.pos):
                    click_event.fire(e_down, e_up)
                self._draw_ripple_effect = None

    def _draw(clip, bgcolor, draw_target, dest, self: Self):
        image = self.image
        with clip(draw_target, dest):
            draw_target.fill(bgcolor)
            if (draw := self._draw_ripple_effect) is not None:
                draw(draw_target)
            draw_target.blit(image, image.get_rect(center=dest.center))

    _draw = partial(_draw, clip)
