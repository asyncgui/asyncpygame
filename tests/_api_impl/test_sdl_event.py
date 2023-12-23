def test_sdl_event_no_filter():
    from asyncgui import start
    from pygame.constants import FINGERDOWN, FINGERUP
    from pygame.event import Event
    from asyncpygame._api_impl.priority_dispatcher import PriorityDispatcher
    from asyncpygame._api_impl.sdl_event import sdl_event

    async def async_fn(d):
        e = await sdl_event(d.add_subscriber)
        assert e.type == FINGERDOWN
        e = await sdl_event(d.add_subscriber)
        assert e.type == FINGERUP

    d = PriorityDispatcher()
    task = start(async_fn(d))
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert task.finished


def test_sdl_event_with_filter():
    from asyncgui import start
    from pygame.constants import FINGERDOWN, FINGERUP
    from pygame.event import Event
    from asyncpygame._api_impl.priority_dispatcher import PriorityDispatcher
    from asyncpygame._api_impl.sdl_event import sdl_event

    d = PriorityDispatcher()
    task = start(sdl_event(d.add_subscriber, filter=lambda e: e.type == FINGERUP))
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert task.finished


def test_sdl_frequent_event_no_filter():
    from asyncgui import start
    from pygame.constants import FINGERDOWN, FINGERUP, QUIT
    from pygame.event import Event
    from asyncpygame._api_impl.priority_dispatcher import PriorityDispatcher
    from asyncpygame._api_impl.sdl_event import sdl_frequent_event

    async def async_fn(d):
        async with sdl_frequent_event(d.add_subscriber) as any_event:
            while True:
                e = await any_event()
                if e.type == QUIT:
                    break

    d = PriorityDispatcher()
    task = start(async_fn(d))
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert not task.finished
    d.dispatch(Event(QUIT))
    assert task.finished


def test_sdl_frequent_event_with_filter():
    from asyncgui import start
    from pygame.constants import FINGERDOWN, FINGERUP, QUIT
    from pygame.event import Event
    from asyncpygame._api_impl.priority_dispatcher import PriorityDispatcher
    from asyncpygame._api_impl.sdl_event import sdl_frequent_event

    async def async_fn(d):
        async with sdl_frequent_event(d.add_subscriber, filter=lambda e: e.type in (FINGERDOWN, FINGERUP)) \
                as finger_event:
            while True:
                e = await finger_event()
                if e.type in (QUIT, FINGERUP):
                    break

    d = PriorityDispatcher()
    task = start(async_fn(d))
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(QUIT))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert task.finished
