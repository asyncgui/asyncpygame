def test_sdl_event_no_filter():
    from pygame.constants import FINGERDOWN, FINGERUP
    from pygame.event import Event
    import asyncpygame as ap

    async def async_fn():
        e = await ap.sdl_event()
        assert e.type == FINGERDOWN
        e = await ap.sdl_event()
        assert e.type == FINGERUP

    runner = ap.init()
    task = ap.start(async_fn())
    runner.dispatch_event(Event(FINGERDOWN))
    assert not task.finished
    runner.dispatch_event(Event(FINGERUP))
    assert task.finished


def test_sdl_event_with_filter():
    from pygame.constants import FINGERDOWN, FINGERUP
    from pygame.event import Event
    import asyncpygame as ap

    runner = ap.init()
    task = ap.start(ap.sdl_event(filter=lambda e: e.type == FINGERUP))
    runner.dispatch_event(Event(FINGERDOWN))
    assert not task.finished
    runner.dispatch_event(Event(FINGERUP))
    assert task.finished


def test_sdl_frequent_event_no_filter():
    from pygame.constants import FINGERDOWN, FINGERUP, QUIT
    from pygame.event import Event
    import asyncpygame as ap

    async def async_fn():
        async with ap.sdl_frequent_event() as any_event:
            while True:
                e = await any_event()
                if e.type == QUIT:
                    break

    runner = ap.init()
    task = ap.start(async_fn())
    runner.dispatch_event(Event(FINGERDOWN))
    assert not task.finished
    runner.dispatch_event(Event(FINGERUP))
    assert not task.finished
    runner.dispatch_event(Event(QUIT))
    assert task.finished


def test_sdl_frequent_event_with_filter():
    from pygame.constants import FINGERDOWN, FINGERUP, QUIT
    from pygame.event import Event
    import asyncpygame as ap

    async def async_fn():
        async with ap.sdl_frequent_event(filter=lambda e: e.type in (FINGERDOWN, FINGERUP)) \
                as finger_event:
            while True:
                e = await finger_event()
                if e.type in (QUIT, FINGERUP):
                    break

    runner = ap.init()
    task = ap.start(async_fn())
    runner.dispatch_event(Event(FINGERDOWN))
    assert not task.finished
    runner.dispatch_event(Event(QUIT))
    assert not task.finished
    runner.dispatch_event(Event(FINGERUP))
    assert task.finished
