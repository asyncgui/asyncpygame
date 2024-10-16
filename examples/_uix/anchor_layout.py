__all__ = ('anchor_layout', )

from functools import partial

import asyncgui
from pygame import Surface, Rect


async def anchor_layout(
        image: Surface, dest: Rect, priority, *, anchor_image="center", anchor_dest="center",
        executor, draw_target, **__):
    '''
    .. code-block::

        async with asyncpygame.open_nursery() as nursery:
            image = Surface(...)
            dest = Rect(...)

            nursery.start(anchor_layout(image, dest, priority=..., **common_params))
    '''
    with executor.register(partial(_draw, draw_target.blit, image, image.get_rect(), dest, anchor_image, anchor_dest), priority):
        await asyncgui.sleep_forever()


def _draw(getattr, setattr, blit, image, src: Rect, dest: Rect, anchor_image, anchor_dest):
    setattr(src, anchor_image, getattr(dest, anchor_dest))
    blit(image, src)


_draw = partial(_draw, getattr, setattr)
