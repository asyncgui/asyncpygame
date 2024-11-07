__all__ = ("run", "quit", "run_and_record", )

from collections.abc import Iterator
import pygame
import asyncpygame as ap


class AppQuit(Exception):
    pass


def quit(*args):
    raise AppQuit()


def run(main_func, *, fps=30, auto_quit=True):
    from ._common_params import CommonParams

    pygame_clock = pygame.Clock()
    clock = ap.Clock()
    sdlevent = ap.SDLEvent()
    executor = ap.PriorityExecutor()
    main_task = ap.start(main_func(CommonParams(
        executor=executor, sdlevent=sdlevent, clock=clock, pygame_clock=pygame_clock)))

    if auto_quit:
        sdlevent.subscribe((pygame.QUIT, ), quit, priority=0)
        sdlevent.subscribe((pygame.KEYDOWN, ), lambda e, K=pygame.K_ESCAPE: e.key == K and quit(), priority=0)

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


def run_and_record(main_func, *, fps=30, auto_quit=True, outfile="./output.mkv", overwrite=False,
                   outfile_options: Iterator[str]=r"-codec:v libx265 -qscale:v 0".split()):
    '''
    Runs the program while recording the screen to a video file using ffmpeg.
    Requires numpy.

    .. code-block::

        # H.265/HEVC, maximum quality (default)
        run_and_record(..., outfile_options=r"-codec:v libx265 -qscale:v 0".split())

        # H.265/HEVC, lossless compression
        run_and_record(..., outfile_options=r"-codec:v libx265 -x265-params lossless=1".split())

        # WebP, lossless compression, infinite loop
        run_and_record(..., outfile_options=r"-codec:v libwebp -lossless 1 -loop 0".split(), outfile="./output.webp")
    '''
    import subprocess
    from numpy import copyto as numpy_copyto
    from pygame.surfarray import pixels3d
    from ._common_params import CommonParams

    clock = ap.Clock()
    sdlevent = ap.SDLEvent()
    executor = ap.PriorityExecutor()
    main_task = ap.start(main_func(CommonParams(executor=executor, sdlevent=sdlevent, clock=clock)))
    screen = pygame.display.get_surface()

    if auto_quit:
        sdlevent.subscribe((pygame.QUIT, ), quit, priority=0)
        sdlevent.subscribe((pygame.KEYDOWN, ), lambda e, K=pygame.K_ESCAPE: e.key == K and quit(), priority=0)

    ffmpeg_cmd = (
        'ffmpeg',
        '-y' if overwrite else '-n',
        '-f', 'rawvideo',
        '-codec:v', 'rawvideo',
        '-pixel_format', 'rgb24',
        '-video_size', f'{screen.width}x{screen.height}',
        '-framerate', str(fps),
        '-i', '-',  # stdin as the input source
        '-an',  # no audio
        *outfile_options,
        outfile,
    )
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, bufsize=0)
    output_buffer = _create_output_buffer_for_surface(screen)
    output_axis_order = (1, 0, 2)  # 高さ 幅 画素 の順

    # LOAD_FAST
    pygame_event_get = pygame.event.get
    clock_tick = clock.tick
    sdlevent_dispatch = sdlevent.dispatch
    process_stdin_write = process.stdin.write
    screen_lock = screen.lock
    screen_unlock = screen.unlock

    try:
        dt = 1000.0 / fps
        while True:
            for event in pygame_event_get():
                sdlevent_dispatch(event)
            clock_tick(dt)
            executor()

            screen_lock()
            frame = pixels3d(screen).transpose(output_axis_order)
            numpy_copyto(output_buffer, frame)
            process_stdin_write(output_buffer)
            del frame
            screen_unlock()
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


def _create_output_buffer_for_surface(surface: pygame.Surface):
    from pygame.surfarray import pixels3d
    import numpy
    s = pixels3d(surface).shape
    return numpy.empty((s[1], s[0], s[2], ), dtype='uint8')  # 高さ 幅 画素 の順にする
