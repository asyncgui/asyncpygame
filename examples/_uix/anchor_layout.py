__all__ = ('AnchorLayout', )

from typing import Self
from functools import partial

from asyncgui import Nursery, sleep_forever
from pygame import Surface, Rect


class AnchorLayout:
    '''
    .. code-block::

        async with asyncpygame.open_nursery() as nursery:
            image = Surface(...)
            dest = Rect(...)
            layout = AnchorLayout(nursery, image, dest, **common_params)

            # Aligns the right edge of the image with the right edge of the layout.
            layout.anchor_src = "right"
            layout.anchor_dest = "right"

            # Aligns the center of the image with the midtop of the layout.
            layout.anchor_src = "center"
            layout.anchor_dest = "midtop"

            # You can change its image anytime.
            layout.image = another_image

            # You can move or resize the layout by updating the ``dest``.
            dest.right = ...
            dest.width = ...

            # but you cannot assign another Rect instance to the layout.
            layout.dest = another_rect  # NOT ALLOWED
    '''
    def __init__(self, owner: Nursery, image: Surface, dest: Rect,
                 *, anchor_src="center", anchor_dest="center", **common_params):
        '''
        :param owner: AnchorLayout cannot outlive its owner. When the owner is closed, the sprite is destroyed.
        :param anchor_src: This must be any of the ``Rect``s positional attribute names. (e.g. "topleft", "bottomleft", ...)
        :param anchor_dest: Same as ``anchor_src``.
        '''
        self._dest = dest
        self.image = image
        self.anchor_src = anchor_src
        self.anchor_dest = anchor_dest
        self._main_task = owner.start(self._main(**common_params), daemon=True)

    def kill(self):
        self._main_task.cancel()

    @property
    def dest(self) -> Rect:
        return self._dest

    async def _main(self, *, priority, draw_target, executor, **unused):
        with executor.register(partial(self._draw, draw_target.blit, self._dest, self), priority=priority):
            await sleep_forever()

    def _draw(getattr, blit, dest, self: Self):
        image = self.image
        blit(image, image.get_rect(**{self.anchor_src: getattr(dest, self.anchor_dest)}))

    _draw = partial(_draw, getattr)
