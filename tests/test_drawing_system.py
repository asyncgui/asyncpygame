def test_same_zorders():
    import asyncpygame as ap

    runner = ap.init()
    value_list = []

    ap.GraphicalEntity(draw_func=value_list.append)
    runner.draw('A')
    assert value_list == ['A', ]
    ent = ap.GraphicalEntity(draw_func=value_list.append)
    runner.draw('B')
    assert value_list == ['A', 'B', 'B', ]
    ent.visible = False
    runner.draw('C')
    assert value_list == ['A', 'B', 'B', 'C', ]


def test_various_zorders():
    import asyncpygame as ap

    runner = ap.init()
    value_list = []

    ap.GraphicalEntity(draw_func=value_list.append, zorder=10)
    ent = ap.GraphicalEntity(draw_func=lambda v: value_list.append(v.lower()), zorder=9)
    runner.draw('A')
    assert value_list == ['a', 'A', ]
    value_list.clear()
    ap.GraphicalEntity(draw_func=lambda v: value_list.append(v + v), zorder=8)
    runner.draw('B')
    assert value_list == ['BB', 'b', 'B', ]
    value_list.clear()
    ent.visible = False
    runner.draw('C')
    assert value_list == ['CC', 'C']
    value_list.clear()
    ent.zorder = 7
    ent.visible = True
    runner.draw('D')
    assert value_list == ['d', 'DD', 'D', ]
    value_list.clear()
    ent.draw_func = lambda v: value_list.append(v + v + v)
    runner.draw('E')
    assert value_list == ['EEE', 'EE', 'E', ]


def test_change_zorder_while_inactive():
    import asyncpygame as ap

    runner = ap.init()
    value_list = []

    ent = ap.GraphicalEntity(draw_func=value_list.append, zorder=0)
    ap.GraphicalEntity(draw_func=lambda v: value_list.append(v.lower()), zorder=1)
    runner.draw('A')
    assert value_list == ['A', 'a']
    ent.visible = False
    runner.draw('B')
    assert value_list == ['A', 'a', 'b']
    ent.zorder = 2
    runner.draw('C')
    assert value_list == ['A', 'a', 'b', 'c']
    ent.visible = True
    runner.draw('D')
    assert value_list == ['A', 'a', 'b', 'c', 'd', 'D']
