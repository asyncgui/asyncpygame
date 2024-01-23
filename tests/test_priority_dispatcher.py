import pytest


@pytest.fixture()
def d():
    from asyncpygame._priority_dispatcher import PriorityDispatcher
    return PriorityDispatcher()


def test_same_priorities(d):
    value_list = []
    d.add_subscriber(value_list.append)
    d.dispatch('A')
    assert value_list == ['A', ]
    s = d.add_subscriber(value_list.append)
    d.dispatch('B')
    assert value_list == ['A', 'B', 'B',]
    s.cancel()
    d.dispatch('C')
    assert value_list == ['A', 'B', 'B', 'C', ]


def test_various_priorities(d):
    value_list = []
    d.add_subscriber(value_list.append, priority=0)
    s2 = d.add_subscriber(lambda v: value_list.append(v.lower()), priority=1)
    d.dispatch('A')
    assert value_list == ['a', 'A']
    d.add_subscriber(lambda v: value_list.append(v + v), priority=2)
    d.dispatch('B')
    assert value_list == ['a', 'A', 'BB', 'b', 'B']
    s2.cancel()
    d.dispatch('C')
    assert value_list == ['a', 'A', 'BB', 'b', 'B', 'CC', 'C']


def test_stop_dispatching(d):
    from asyncpygame._priority_dispatcher import STOP_DISPATCHING

    value_list = []
    d.add_subscriber(value_list.append, priority=0)
    d.add_subscriber(value_list.append, priority=2)
    d.dispatch('A')
    assert value_list == ['A', 'A']
    s = d.add_subscriber(lambda v: STOP_DISPATCHING, priority=1)
    d.dispatch('B')
    assert value_list == ['A', 'A', 'B', ]
    s.cancel()
    d.dispatch('C')
    assert value_list == ['A', 'A', 'B', 'C', 'C']
