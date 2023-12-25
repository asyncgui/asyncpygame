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
            screen.fill(...)
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
            screen.fill(bgcolor)
            runner.draw(screen)
            pygame.display.flip()
    '''
    import types
    from asyncpygame._timer import Timer
    from asyncpygame._priority_dispatcher import PriorityDispatcher
    from asyncpygame import _sleep, _sdl_event

    timer = Timer()
    _sleep.schedule_once = timer.schedule_once
    _sleep.schedule_interval = timer.schedule_interval

    dispatcher = PriorityDispatcher()
    _sdl_event.add_subscriber = dispatcher.add_subscriber

    return types.SimpleNamespace(
        progress=timer.progress,
        dispatch_event=dispatcher.dispatch,
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
    # draw = runner.draw

    alive = True
    while alive:
        for event in pygame_event_get():
            if event.type == QUIT:
                alive = False
            else:
                dispatch_event(event)
        progress(clock_tick(fps))
        draw_target_fill(bgcolor)
        # draw(draw_target)
        pygame_display_flip()

    main_task.cancel()
    pygame.quit()
