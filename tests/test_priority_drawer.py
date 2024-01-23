import pytest


@pytest.fixture()
def drawer():
    from asyncpygame.priority_drawer import PriorityDrawer
    return PriorityDrawer()


def test_same_prioritys(drawer):
    from asyncpygame.priority_drawer import GraphicalEntity

    value_list = []
    GraphicalEntity(drawer, draw_func=value_list.append)
    drawer.draw('A')
    assert value_list == ['A', ]
    ent = GraphicalEntity(drawer, draw_func=value_list.append)
    drawer.draw('B')
    assert value_list == ['A', 'B', 'B', ]
    ent.visible = False
    drawer.draw('C')
    assert value_list == ['A', 'B', 'B', 'C', ]


def test_various_prioritys(drawer):
    from asyncpygame.priority_drawer import GraphicalEntity

    value_list = []
    GraphicalEntity(drawer, draw_func=value_list.append, priority=10)
    ent = GraphicalEntity(drawer, draw_func=lambda v: value_list.append(v.lower()), priority=9)
    drawer.draw('A')
    assert value_list == ['a', 'A', ]
    value_list.clear()
    GraphicalEntity(drawer, draw_func=lambda v: value_list.append(v + v), priority=8)
    drawer.draw('B')
    assert value_list == ['BB', 'b', 'B', ]
    value_list.clear()
    ent.visible = False
    drawer.draw('C')
    assert value_list == ['CC', 'C']
    value_list.clear()
    ent.priority = 7
    ent.visible = True
    drawer.draw('D')
    assert value_list == ['d', 'DD', 'D', ]
    value_list.clear()
    ent.draw_func = lambda v: value_list.append(v + v + v)
    drawer.draw('E')
    assert value_list == ['EEE', 'EE', 'E', ]


def test_change_priority_while_inactive(drawer):
    from asyncpygame.priority_drawer import GraphicalEntity

    value_list = []
    ent = GraphicalEntity(drawer, draw_func=value_list.append, priority=0)
    GraphicalEntity(drawer, draw_func=lambda v: value_list.append(v.lower()), priority=1)
    drawer.draw('A')
    assert value_list == ['A', 'a']
    ent.visible = False
    drawer.draw('B')
    assert value_list == ['A', 'a', 'b']
    ent.priority = 2
    drawer.draw('C')
    assert value_list == ['A', 'a', 'b', 'c']
    ent.visible = True
    drawer.draw('D')
    assert value_list == ['A', 'a', 'b', 'c', 'd', 'D']
