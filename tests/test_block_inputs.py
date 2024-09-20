from pygame.event import Event
from pygame.constants import KEYDOWN


def test_lower_priority():
    import asyncpygame as ap
    sdlevent = ap.SDLEvent()

    received = []
    sdlevent.subscribe((KEYDOWN, ), received.append, priority=20)
    with ap.block_inputs(sdlevent=sdlevent, priority=10):
        sdlevent.dispatch(Event(KEYDOWN))
        assert len(received) == 1
    sdlevent.dispatch(Event(KEYDOWN))
    assert len(received) == 2


def test_higher_priority():
    import asyncpygame as ap
    sdlevent = ap.SDLEvent()

    received = []
    sdlevent.subscribe((KEYDOWN, ), received.append, priority=0)
    with ap.block_inputs(sdlevent=sdlevent, priority=10):
        sdlevent.dispatch(Event(KEYDOWN))
        assert len(received) == 0
    sdlevent.dispatch(Event(KEYDOWN))
    assert len(received) == 1
