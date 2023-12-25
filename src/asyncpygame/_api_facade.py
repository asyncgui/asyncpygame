from typing import TypeAlias
from collections.abc import Callable

from pygame.surface import Surface


DrawFunc: TypeAlias = Callable[[Surface], None]


class DrawingRequest:
    '''
    画面に何か表示したい時に用いるクラス。
    このクラスの意義は ``zorder`` による順番を考慮した描画にあります。
    そのような機能が要らないのであれば特に使う必要はありません。

    .. code-block::

        def draw(draw_target: Surface):
            ...

        req = DrawingRequest(draw, zorder=200)

    ``active`` は勿論 ``zorder`` と ``draw_func`` も後からいつでも変更可です。

    .. code-block::

        req.zorder = 100
        req.draw_func = another_func
        req.active = False

    またwith文にも利用でき、withブロックを抜ける時に自動で ``active`` が偽になります。

    .. code-block::

        with DrawingRequest(draw_func, zorder=200):
            ...
    '''

    def __init__(self, draw_func: DrawFunc, /, *, zorder=DEFAULT_ZORDER, active=True):
        ...

    @property
    def zorder(self) -> int:
        '''
        描画順。この値が小さい者ほど先に描画を行う。値が同じ者同士の順は未定義。
        '''

    @property
    def draw_func(self) -> DrawFunc:
        '''
        実際に描画を行う関数。
        '''

    @property
    def active(self) -> bool:
        '''
        描画を行うか否か。描画させたくない時だけでなくインスタンスが要らなくなった時にもこれを偽にしてください。
        '''
