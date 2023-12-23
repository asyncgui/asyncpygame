def test_same_zorders():
    from asyncpygame._api_impl.priority_drawing import Drawer, DrawingRequest

    d = Drawer()
    value_list = []

    DrawingRequest(d.add_request, value_list.append)
    d.draw('A')
    assert value_list == ['A', ]
    req = DrawingRequest(d.add_request, value_list.append)
    d.draw('B')
    assert value_list == ['A', 'B', 'B',]
    req.active = False
    d.draw('C')
    assert value_list == ['A', 'B', 'B', 'C', ]


def test_various_zorders():
    from asyncpygame._api_impl.priority_drawing import Drawer, DrawingRequest

    d = Drawer()
    value_list = []

    DrawingRequest(d.add_request, value_list.append, zorder=10)
    req = DrawingRequest(d.add_request, lambda v: value_list.append(v.lower()), zorder=9)
    d.draw('A')
    assert value_list == ['a', 'A', ]
    value_list.clear()
    DrawingRequest(d.add_request, lambda v: value_list.append(v + v), zorder=8)
    d.draw('B')
    assert value_list == ['BB', 'b', 'B', ]
    value_list.clear()
    req.active = False
    d.draw('C')
    assert value_list == ['CC', 'C']
    value_list.clear()
    req.zorder = 7
    req.active = True
    d.draw('D')
    assert value_list == ['d', 'DD', 'D', ]
    value_list.clear()
    req.draw_func = lambda v: value_list.append(v + v + v)
    d.draw('E')
    assert value_list == ['EEE', 'EE', 'E', ]


def test_change_zorder_while_inactive():
    from asyncpygame._api_impl.priority_drawing import Drawer, DrawingRequest

    d = Drawer()
    value_list = []

    req = DrawingRequest(d.add_request, value_list.append, zorder=0)
    DrawingRequest(d.add_request, lambda v: value_list.append(v.lower()), zorder=1)
    d.draw('A')
    assert value_list == ['A', 'a']
    req.active = False
    d.draw('B')
    assert value_list == ['A', 'a', 'b']
    req.zorder = 2
    d.draw('C')
    assert value_list == ['A', 'a', 'b', 'c']
    req.active = True
    d.draw('D')
    assert value_list == ['A', 'a', 'b', 'c', 'd', 'D']
