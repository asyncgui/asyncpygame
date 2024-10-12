import pytest


@pytest.fixture()
def executor():
    from asyncpygame._priority_executor import PriorityExecutor
    return PriorityExecutor()


def test_basis(executor):
    values = []
    req = executor.register(lambda: values.append('A'), priority=0)
    assert values == []
    executor()
    assert values == ['A', ]
    executor()
    assert values == ['A', 'A', ]
    req.cancel()
    executor()
    assert values == ['A', 'A', ]


def test_same_priority(executor):
    values = []
    req = executor.register(lambda: values.append('A'), priority=0)
    executor.register(lambda: values.append('B'), priority=0)
    assert values == []
    executor()
    assert sorted(values) == ['A', 'B', ]
    executor()
    assert sorted(values) == ['A', 'A', 'B', 'B', ]
    req.cancel()
    executor()
    assert sorted(values) == ['A', 'A', 'B', 'B', 'B', ]


def test_different_priorities(executor):
    values = []
    req = executor.register(lambda: values.append('A'), priority=2)
    executor.register(lambda: values.append('B'), priority=0)
    assert values == []
    executor()
    assert values == ['B', 'A', ]
    executor.register(lambda: values.append('C'), priority=1)
    executor()
    assert values == ['B', 'A', 'B', 'C', 'A', ]
    req.cancel()
    executor()
    assert values == ['B', 'A', 'B', 'C', 'A', 'B', 'C', ]
