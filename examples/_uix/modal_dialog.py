__all__ = ('ask_yes_no_question', )

from typing import Unpack
from contextlib import asynccontextmanager
from functools import partial

import asyncgui
from pygame import Rect
from pygame.font import SysFont

from asyncpygame import CommonParams, block_input_events, Clock
from _uix.ripple_button import RippleButton
from _uix.anchor_layout import AnchorLayout


@asynccontextmanager
async def darken(**kwargs: Unpack[CommonParams]):
    interpolate = kwargs["clock"].interpolate_scalar
    draw_target = kwargs["draw_target"]
    overlay_surface = draw_target.copy()
    overlay_surface.fill("black")
    set_alpha = overlay_surface.set_alpha
    with kwargs["executor"].register(partial(draw_target.blit, overlay_surface), kwargs["priority"]):
        async for v in interpolate(0, 180, duration=200):
            set_alpha(v)
        yield
        async for v in interpolate(180, 0, duration=300):
            set_alpha(v)


async def translate_rects_vertically(clock: Clock, rects, movement, duration):
    org_ys = tuple(rect.y for rect in rects)
    async for v in clock.interpolate_scalar(0, movement, duration=duration):
        for rect, org_y in zip(rects, org_ys):
            rect.y = org_y + v


async def ask_yes_no_question(
        question, *, dialog_size: Rect=None, font=None, text_yes='Yes', text_no='No',
        priority, **kwargs: Unpack[CommonParams]) -> bool:
    '''
    .. code-block::

        result = await ask_yes_no_question("Do you like PyGame?", priority=0xFFFFFA00, **kwargs)
    '''
    bgcolor = "grey90"
    executor = kwargs["executor"]
    sdlevent = kwargs["sdlevent"]
    clock = kwargs["clock"]
    draw_target = kwargs["draw_target"]
    if font is None:
        font = SysFont(None, 40)

    with block_input_events(sdlevent, priority):
        async with darken(priority=priority, **kwargs), asyncgui.open_nursery() as nursery:
            target_rect = draw_target.get_rect()
            if dialog_size is None:
                dialog_size = target_rect.inflate(-100, 0)
                dialog_size.height = dialog_size.width // 2
            dialog_dest = dialog_size.move_to(bottom=target_rect.top)
            with executor.register(partial(draw_target.fill, bgcolor, dialog_dest), priority=priority + 1):
                label = AnchorLayout(
                    nursery,
                    font.render(question, True, "black", bgcolor).convert(draw_target),
                    dialog_dest.scale_by(1.0, 0.5).move_to(top=dialog_dest.top).inflate(-10, -10),
                    priority=priority + 2, **kwargs)
                yes_button = RippleButton(
                    nursery,
                    font.render(text_yes, True, "white"),
                    dialog_dest.scale_by(0.5, 0.5).move_to(bottomright=dialog_dest.bottomright).inflate(-20, -20),
                    priority=priority + 2, **kwargs)
                no_button = RippleButton(
                    nursery,
                    font.render(text_no, True, "white"),
                    dialog_dest.scale_by(0.5, 0.5).move_to(bottomleft=dialog_dest.bottomleft).inflate(-20, -20),
                    priority=priority + 2, **kwargs)
                rects = (dialog_dest, label.dest, yes_button.dest, no_button.dest, )
                y_movement = target_rect.centery - dialog_dest.centery
                await translate_rects_vertically(clock, rects, y_movement, duration=200)
                tasks = await asyncgui.wait_any(yes_button.to_be_clicked(), no_button.to_be_clicked())
                await translate_rects_vertically(clock, rects, -y_movement, duration=200)
                return tasks[0].finished
