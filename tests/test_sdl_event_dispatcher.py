import pytest


@pytest.fixture()
def d():
    from asyncpygame._sdl_event_dispatcher import SDLEventDispatcher
    return SDLEventDispatcher()


def test_wait_sdl_event_no_filter(d):
    from pygame.constants import FINGERDOWN, FINGERUP
    from pygame.event import Event
    from asyncgui import start

    async def async_fn():
        e = await d.wait_sdl_event()
        assert e.type == FINGERDOWN
        e = await d.wait_sdl_event()
        assert e.type == FINGERUP

    task = start(async_fn())
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert task.finished


def test_wait_sdl_event_with_filter(d):
    from pygame.constants import FINGERDOWN, FINGERUP
    from pygame.event import Event
    from asyncgui import start

    task = start(d.wait_sdl_event(filter=lambda e: e.type == FINGERUP))
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert task.finished


def test_wait_sdl_event_repeatedly_no_filter(d):
    from pygame.constants import FINGERDOWN, FINGERUP, QUIT
    from pygame.event import Event
    from asyncgui import start

    async def async_fn():
        async with d.wait_sdl_event_repeatedly() as wait_any_event:
            while True:
                e = await wait_any_event()
                if e.type == QUIT:
                    break

    task = start(async_fn())
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert not task.finished
    d.dispatch(Event(QUIT))
    assert task.finished


def test_wait_sdl_event_repeatedly_with_filter(d):
    from pygame.constants import FINGERDOWN, FINGERUP, QUIT
    from pygame.event import Event
    from asyncgui import start

    async def async_fn():
        async with d.wait_sdl_event_repeatedly(filter=lambda e: e.type in (FINGERDOWN, FINGERUP)) as wait_finger_event:
            while True:
                e = await wait_finger_event()
                if e.type in (QUIT, FINGERUP):
                    break

    task = start(async_fn())
    d.dispatch(Event(FINGERDOWN))
    assert not task.finished
    d.dispatch(Event(QUIT))
    assert not task.finished
    d.dispatch(Event(FINGERUP))
    assert task.finished
