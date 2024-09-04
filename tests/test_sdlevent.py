import pytest
from pygame.event import Event as E


@pytest.fixture()
def se():
    from asyncpygame._sdlevent import SDLEvent
    return SDLEvent()


def test_subscribe(se):
    received = []
    sub = se.subscribe((1, 2), received.append)
    se.dispatch(E(1))
    assert len(received) == 1
    se.dispatch(E(0))
    assert len(received) == 1
    se.dispatch(E(2))
    assert len(received) == 2
    sub.cancel()
    se.dispatch(E(2))
    assert len(received) == 2
    se.dispatch(E(0))
    assert len(received) == 2


def test_two_subscribers_with_the_same_priority(se):
    value_list = []

    def store_value(e):
        value_list.append(e.value)

    sub = se.subscribe((1, ), store_value)
    se.dispatch(E(1, value='A'))
    assert value_list == ['A', ]
    se.subscribe((1, ), store_value)
    se.dispatch(E(1, value='B'))
    assert value_list == ['A', 'B', 'B',]
    sub.cancel()
    se.dispatch(E(1, value='C'))
    assert value_list == ['A', 'B', 'B', 'C', ]


def test_two_subscribers_with_different_priorities(se):
    value_list = []

    def store_value(e):
        value_list.append(e.value)

    def store_value2x(e):
        value_list.append(e.value * 2)

    sub = se.subscribe((1, ), store_value, priority=0)
    se.dispatch(E(1, value='A'))
    assert value_list == ['A', ]
    se.subscribe((1, ), store_value2x, priority=1)
    se.dispatch(E(1, value='B'))
    assert value_list == ['A', 'BB', 'B',]
    sub.cancel()
    se.dispatch(E(1, value='C'))
    assert value_list == ['A', 'BB', 'B', 'CC', ]


def test_stop_dispatching(se):
    received = []
    se.subscribe((1, ), received.append, priority=0)
    se.dispatch(E(1))
    assert len(received) == 1
    sub = se.subscribe((1, ), lambda e: True, priority=1)
    se.dispatch(E(1))
    assert len(received) == 1
    sub.cancel()
    se.dispatch(E(1))
    assert len(received) == 2


def test_wait(se):
    from asyncgui import start

    task = start(se.wait(1, 2))
    se.dispatch(E(0))
    assert not task.finished
    se.dispatch(E(1))
    assert task.result.type == 1


def test_wait_with_filter(se):
    from asyncgui import start

    task = start(se.wait(1, 2, filter=lambda e: e.value == 'A'))
    se.dispatch(E(0, value='B'))
    assert not task.finished
    se.dispatch(E(0, value='A'))
    assert not task.finished
    se.dispatch(E(1, value='B'))
    assert not task.finished
    se.dispatch(E(1, value='A'))
    assert task.result.type == 1
    assert task.result.value == 'A'


@pytest.mark.parametrize('event_type, task1_finished', [(1, True), (2, False), ])
def test_wait_with_consume(se, event_type, task1_finished):
    from asyncgui import start

    task1 = start(se.wait(1, 2, priority=0))
    task2 = start(se.wait(2, priority=1, consume=True))
    se.dispatch(E(event_type))
    assert task1.finished is task1_finished
    task1.cancel()
    task2.cancel()


def test_wait_freq(se):
    from asyncgui import start

    async def async_fn():
        async with se.wait_freq(1, 2) as event:
            return await event()

    task = start(async_fn())
    se.dispatch(E(0))
    assert not task.finished
    se.dispatch(E(1))
    assert task.result.type == 1


def test_wait_freq_with_filter(se):
    from asyncgui import start

    async def async_fn():
        async with se.wait_freq(1, 2, filter=lambda e: e.value == 'A') as event:
            return await event()

    task = start(async_fn())
    se.dispatch(E(0, value='B'))
    assert not task.finished
    se.dispatch(E(0, value='A'))
    assert not task.finished
    se.dispatch(E(1, value='B'))
    assert not task.finished
    se.dispatch(E(1, value='A'))
    assert task.result.type == 1
    assert task.result.value == 'A'


@pytest.mark.parametrize('event_type, task1_finished', [(1, True), (2, False), ])
def test_wait_freq_with_consume(se, event_type, task1_finished):
    from asyncgui import start

    async def async_fn1():
        async with se.wait_freq(1, 2, priority=0) as event:
            return await event()

    async def async_fn2():
        async with se.wait_freq(2, priority=1, consume=True) as event:
            return await event()

    task1 = start(async_fn1())
    task2 = start(async_fn2())
    se.dispatch(E(event_type))
    assert task1.finished is task1_finished
    task1.cancel()
    task2.cancel()


def test_wait_freq_mixed_with_another_type_of_awaitable(se):
    from asyncgui import start, Event

    async def async_fn():
        async with se.wait_freq(1, 2) as event:
            await event()
            await ae.wait()
            await event()

    ae = Event()
    task = start(async_fn())
    for __ in range(3):
        se.dispatch(E(1))
    assert not task.finished
    ae.fire()
    assert not task.finished
    se.dispatch(E(1))
    assert task.finished
