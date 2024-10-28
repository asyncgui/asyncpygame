__all__ = ('show_messagebox', 'ask_yes_no_question', )

from typing import Unpack
from collections.abc import Sequence
from contextlib import asynccontextmanager
from functools import partial

import asyncgui
from pygame.colordict import THECOLORS
from pygame import Rect, Surface
from pygame.font import SysFont

from asyncpygame import CommonParams, block_input_events, Clock
from _uix.ripple_button import ripple_button
from _uix.anchor_layout import anchor_layout


@asynccontextmanager
async def darken(*, priority, **kwargs: Unpack[CommonParams]):
    interpolate = kwargs["clock"].interpolate_scalar
    draw_target = kwargs["draw_target"]
    overlay_surface = Surface(draw_target.size)
    set_alpha = overlay_surface.set_alpha
    with kwargs["executor"].register(partial(draw_target.blit, overlay_surface), priority):
        async for v in interpolate(0, 180, duration=200):
            set_alpha(v)
        yield
        async for v in interpolate(180, 0, duration=300):
            set_alpha(v)


async def move_rects_vertically(clock: Clock, rects, movement, duration):
    org_ys = tuple(rect.y for rect in rects)
    async for v in clock.interpolate_scalar(0, movement, duration=duration):
        for rect, org_y in zip(rects, org_ys):
            rect.y = org_y + v


async def show_messagebox(
        message, priority, *, dialog_size: Sequence=None, font=None, text_ok='OK',
        **kwargs: Unpack[CommonParams]) -> bool:
    '''
    .. code-block::

        await show_messagebox("Hello World", priority=0xFFFFFA00, **kwargs)
    '''
    bgcolor = THECOLORS["grey90"]
    clock = kwargs["clock"]
    draw_target = kwargs["draw_target"]
    if font is None:
        font = SysFont(None, 40)

    with block_input_events(kwargs["sdlevent"], priority):
        async with darken(priority=priority, **kwargs), asyncgui.open_nursery() as nursery:
            target_rect = draw_target.get_rect()
            if dialog_size is None:
                w = target_rect.width - 100
                dialog_size = (w, w / 2)
                del w
            dest = Rect(0, 0, *dialog_size).move_to(midbottom=target_rect.midtop)
            e_ok = asyncgui.Event()
            with kwargs["executor"].register(partial(draw_target.fill, bgcolor, dest), priority=priority + 1):
                s = nursery.start
                s(anchor_layout(
                    font.render(message, True, "black", bgcolor).convert(draw_target),
                    label_dest := dest.scale_by(1.0, 0.7).move_to(top=dest.top).inflate(-10, -10),
                    priority + 2,
                    **kwargs), daemon=True)
                s(ripple_button(
                    font.render(text_ok, True, "white").convert_alpha(),
                    button_dest := dest.scale_by(0.5, 0.3).move_to(midbottom=dest.midbottom).inflate(-20, -20),
                    priority + 2,
                    on_click=e_ok.fire,
                    **kwargs), daemon=True)
                rects = (dest, label_dest, button_dest, )
                y_movement = target_rect.centery - dest.centery
                await move_rects_vertically(clock, rects, y_movement, duration=200)
                await e_ok.wait()
                await move_rects_vertically(clock, rects, -y_movement, duration=200)
                return


async def ask_yes_no_question(
        question, priority, *, dialog_size: Sequence=None, font=None, text_yes='Yes', text_no='No',
        **kwargs: Unpack[CommonParams]) -> bool:
    '''
    .. code-block::

        result = await ask_yes_no_question("Do you like PyGame?", priority=0xFFFFFA00, **kwargs)
    '''
    bgcolor = THECOLORS["grey90"]
    clock = kwargs["clock"]
    draw_target = kwargs["draw_target"]
    if font is None:
        font = SysFont(None, 40)

    with block_input_events(kwargs["sdlevent"], priority):
        async with darken(priority=priority, **kwargs), asyncgui.open_nursery() as nursery:
            target_rect = draw_target.get_rect()
            if dialog_size is None:
                w = target_rect.width - 100
                dialog_size = (w, w / 2)
                del w
            dest = Rect(0, 0, *dialog_size).move_to(midbottom=target_rect.midtop)
            e_yes = asyncgui.Event()
            e_no = asyncgui.Event()
            spacing = 20
            h = (dest.height - 3 * spacing) / 2
            w = dest.width - 2 * spacing
            label_size = (w, h)
            button_size = ((w - spacing) / 2, h)
            del w, h
            with kwargs["executor"].register(partial(draw_target.fill, bgcolor, dest), priority=priority + 1):
                s = nursery.start
                s(anchor_layout(
                    font.render(question, True, "black", bgcolor).convert(draw_target),
                    label_dest := Rect(dest.x + spacing, dest.y + spacing, *label_size),
                    priority + 2,
                    **kwargs), daemon=True)
                s(ripple_button(
                    font.render(text_no, True, "white").convert_alpha(),
                    no_button_dest := Rect(label_dest.x, label_dest.bottom + spacing, *button_size),
                    priority + 2,
                    on_click=e_no.fire,
                    **kwargs), daemon=True)
                s(ripple_button(
                    font.render(text_yes, True, "white").convert_alpha(),
                    yes_button_dest := Rect(no_button_dest.right + spacing, no_button_dest.y, *button_size),
                    priority + 2,
                    on_click=e_yes.fire,
                    **kwargs), daemon=True)
                rects = (dest, label_dest, yes_button_dest, no_button_dest, )
                y_movement = target_rect.centery - dest.centery
                await move_rects_vertically(clock, rects, y_movement, duration=200)
                tasks = await asyncgui.wait_any(e_yes.wait(), e_no.wait())
                await move_rects_vertically(clock, rects, -y_movement, duration=200)
                return tasks[0].finished

