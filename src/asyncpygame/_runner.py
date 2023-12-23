import functools
from pygame.event import Event
from pygame.surface import Surface
from ._api_impl.timer import TimeUnit


class Runner:
    '''
    You should not directly instantiate this. Use :func:`init` instead.
    '''

    def progress(self, delta_time: TimeUnit):
        '''
        You need to call this every frame for the timer-related APIs to work.

        .. code-block::

            # in your main loop
            dt = clock.tick(fps)
            runner.progress(dt)
        '''

    def dispatch_event(self, event: Event):
        '''
        You need to call this for the event-related APIs to work.

        .. code-block::

            # in your main loop
            for event in pygame.event.get():
                runner.dispatch_event(event)
        '''

    def draw(self, draw_target: Surface):
        '''
        You need to call this for the drawing-related APIs to work.

        .. code-block::

            # in your main loop
            screen.fill(...)
            runner.draw(screen)
            pygame.display.flip()
        '''


@functools.cache
def init() -> Runner:
    '''
    ``asyncpygame`` を使うにはこれを呼び出し、得た :class:`Runnner` インスタンスのメソッドをメインループ内で呼ぶ必要があります。
    以下がその一例。

    .. code-block::

        runner = asyncpygame.init()
        clock = pygame.Clock()
        alive = True

        while alive:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    alive = False
                else:
                    runner.dispatch_event(event)
            dt = clock.tick(fps)
            runner.progress(dt)
            screen.fill(bgcolor)
            runner.draw(screen)
            pygame.display.flip()

    .. warning::

        ``asyncpygame`` の他のいかなるAPIへのアクセスに先立ってこれを呼び出す必要があります。
        例えば以下のコードでは ``init()`` を呼ぶ前に ``sleep()`` を取り出しているため、たとえまだ呼び出していなくとも正しく動きません。

        .. code-block::

            import asyncpygame

            sleep = asyncpygame.sleep  # Doesn't work.
            asyncpygame.init()

        以下のように必ず初期化後にアクセスしてください。

        .. code-block::

            import asyncpygame

            asyncpygame.init()
            sleep = asyncpygame.sleep  # OK
    '''
    import types
    from functools import partial
    from ._api_impl import _all
    import asyncpygame

    # LOAD_FAST
    setattr_ = setattr
    getattr_ = getattr

    timer = _all.Timer()
    timer_apis = (
        'sleep', 'move_on_after',
        'anim_with_dt', 'anim_with_dt_et', 'anim_with_et', 'anim_with_ratio', 'anim_with_dt_et_ratio',
        'fade_transition',
        'run_in_thread', 'run_in_executor',
    )
    for name in timer_apis:
        setattr_(asyncpygame, name, partial(getattr_(_all, name), timer))

    dispatcher = _all.PriorityDispatcher()
    event_apis = (
        'sdl_event', 'sdl_frequent_event',
    )
    for name in event_apis:
        setattr_(asyncpygame, name, partial(getattr_(_all, name), dispatcher.add_subscriber))

    drawer = _all.Drawer()
    drawing_apis = (
        'DrawingRequest',
    )
    for name in drawing_apis:
        setattr_(asyncpygame, name, partial(getattr_(_all, name), drawer.add_request))

    return types.SimpleNamespace(
        progress=timer.progress,
        dispatch_event=dispatcher.dispatch,
        draw=drawer.draw,
    )


def run(main_coro, *, fps=30, draw_target: Surface, bgcolor):
    '''
    メインループの実装の一例。実際の開発では自分で実装した方が良いでしょう。
    '''
    import pygame
    from pygame.constants import QUIT
    import asyncpygame

    pygame.init()
    runner = asyncpygame.init()
    main_task = asyncpygame.start(main_coro)

    # LOAD_FAST
    pygame_event_get = pygame.event.get
    pygame_display_flip = pygame.display.flip
    clock_tick = pygame.Clock().tick
    draw_target_fill = draw_target.fill
    progress = runner.progress
    dispatch_event = runner.dispatch_event
    draw = runner.draw

    alive = True
    while alive:
        for event in pygame_event_get():
            if event.type == QUIT:
                alive = False
            else:
                dispatch_event(event)
        progress(clock_tick(fps))
        draw_target_fill(bgcolor)
        draw(draw_target)
        pygame_display_flip()

    main_task.cancel()
    pygame.quit()
