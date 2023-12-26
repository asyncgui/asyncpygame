from pygame.event import Event
from pygame.surface import Surface


class Runner:
    '''
    You should not directly instantiate this. Use :func:`init` instead.
    '''

    def progress(self, delta_time):
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
            runner.draw(screen)
            pygame.display.flip()
        '''


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
            runner.draw(screen)
            pygame.display.flip()
    '''
    import types
    import asyncpygame
    from asyncpygame._timer import Timer
    from asyncpygame._priority_dispatcher import PriorityDispatcher
    from asyncpygame import _sleep, _sdl_event, _drawing_system

    timer = Timer()
    _sleep.g_schedule_once = asyncpygame.schedule_once = timer.schedule_once
    _sleep.g_schedule_interval = asyncpygame.schedule_interval = timer.schedule_interval

    dispatcher = PriorityDispatcher()
    _sdl_event.g_add_subscriber = dispatcher.add_subscriber

    drawer = _drawing_system.Drawer()
    _drawing_system.g_add_request = drawer.add_request

    return types.SimpleNamespace(
        progress=timer.progress,
        dispatch_event=dispatcher.dispatch,
        draw=drawer.draw,
    )


def run(main_coro, *, fps=30, draw_target: Surface=None):
    '''
    メインループの実装例。実際の開発では自分で実装してください。
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
    progress = runner.progress
    dispatch_event = runner.dispatch_event
    draw = runner.draw

    if draw_target is None:
        from pygame.display import get_surface
        draw_target = get_surface()
        assert draw_target is not None

    alive = True
    while alive:
        for event in pygame_event_get():
            if event.type == QUIT:
                alive = False
            else:
                dispatch_event(event)
        progress(clock_tick(fps))
        draw(draw_target)
        pygame_display_flip()

    main_task.cancel()
    pygame.quit()
