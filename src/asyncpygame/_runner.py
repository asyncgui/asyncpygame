__all__ = ("run", "quit", )

import pygame
import asyncpygame as ap


class AppQuit(Exception):
    pass


def quit(*args):
    raise AppQuit()


def run(main_func, *, fps=30, auto_quit=True):
    pygame_clock = pygame.Clock()
    clock = ap.Clock()
    sdlevent = ap.SDLEvent()
    executor = ap.PriorityExecutor()
    main_task = ap.start(main_func(clock=clock, sdlevent=sdlevent, executor=executor, pygame_clock=pygame_clock))

    if auto_quit:
        sdlevent.subscribe((pygame.QUIT, ), quit)
        sdlevent.subscribe((pygame.KEYDOWN, ), lambda e, K=pygame.K_ESCAPE: e.key == K and quit())

    # LOAD_FAST
    pygame_event_get = pygame.event.get
    pygame_clock_tick = pygame_clock.tick
    clock_tick = clock.tick
    sdlevent_dispatch = sdlevent.dispatch

    try:
        while True:
            for event in pygame_event_get():
                sdlevent_dispatch(event)
            clock_tick(pygame_clock_tick(fps))
            executor()
    except AppQuit:
        pass
    finally:
        main_task.cancel()
        pygame.quit()
