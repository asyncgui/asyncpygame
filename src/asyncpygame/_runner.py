__all__ = ("run", "quit", "run_and_record", )

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
    except ap.ExceptionGroup as group:
        unignorable_excs = tuple(e for e in group.exceptions if not isinstance(e, AppQuit))
        if unignorable_excs:
            raise ap.ExceptionGroup(group.message, unignorable_excs)
    finally:
        main_task.cancel()


def run_and_record(main_func, *, fps=30, auto_quit=True, output_file="./output.mp4", overwrite=False, codec='mpeg4'):
    '''
    Runs the program while recording the screen to a video file using ffmpeg.
    Requires numpy.
    '''
    import subprocess
    from pygame.surfarray import array3d
    from numpy import transpose as numpy_transpose

    clock = ap.Clock()
    sdlevent = ap.SDLEvent()
    executor = ap.PriorityExecutor()
    main_task = ap.start(main_func(clock=clock, sdlevent=sdlevent, executor=executor))
    screen = pygame.display.get_surface()

    if auto_quit:
        sdlevent.subscribe((pygame.QUIT, ), quit)
        sdlevent.subscribe((pygame.KEYDOWN, ), lambda e, K=pygame.K_ESCAPE: e.key == K and quit())

    ffmpeg_cmd = (
        'ffmpeg',
        '-y' if overwrite else '-n',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pixel_format', 'rgb24',
        '-video_size', f'{screen.width}x{screen.height}',
        '-framerate', str(fps),
        '-i', '-',  # stdin as the input source
        '-an',  # no audio
        '-vcodec', codec,
        output_file,
    )
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    # LOAD_FAST
    pygame_event_get = pygame.event.get
    clock_tick = clock.tick
    sdlevent_dispatch = sdlevent.dispatch
    process_stdin_write = process.stdin.write

    try:
        dt = 1000.0 / fps
        while True:
            for event in pygame_event_get():
                sdlevent_dispatch(event)
            clock_tick(dt)
            executor()
            frame = array3d(screen)
            frame = numpy_transpose(frame, (1, 0, 2))  # 転置して(幅, 高さ, 色)の順にする
            process_stdin_write(frame.tobytes())
    except AppQuit:
        pass
    except ap.ExceptionGroup as group:
        unignorable_excs = tuple(e for e in group.exceptions if not isinstance(e, AppQuit))
        if unignorable_excs:
            raise ap.ExceptionGroup(group.message, unignorable_excs)
    finally:
        main_task.cancel()
        process.stdin.close()
        process.wait()
