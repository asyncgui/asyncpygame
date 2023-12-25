def test_schedule_once():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []
    func = dt_list.append

    timer.schedule_once(func, 100)
    assert dt_list == []
    timer.schedule_once(func, 50)
    assert dt_list == []
    timer.progress(20)
    assert dt_list == []
    timer.schedule_once(func, 40)
    assert dt_list == []
    timer.progress(50)
    assert sorted(dt_list) == [50, 70, ]
    timer.progress(50)
    assert sorted(dt_list) == [50, 70, 120, ]


def test_schedule_once_zero_delay():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []

    timer.schedule_once(dt_list.append, 0)
    assert dt_list == []
    timer.progress(0)
    assert dt_list == [0, ]
    timer.progress(0)
    assert dt_list == [0, ]


def test_schedule_once_cancel():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []
    func = dt_list.append

    e = timer.schedule_once(func, 100)
    timer.schedule_once(func, 50)
    e.cancel()
    assert dt_list == []
    timer.progress(60)
    assert dt_list == [60, ]
    timer.progress(60)
    assert dt_list == [60, ]


def test_schedule_once_cancel_from_a_callback():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []

    e = timer.schedule_once(dt_list.append, 100)
    timer.schedule_once(lambda __: e.cancel(), 50)
    assert dt_list == []
    timer.progress(60)
    assert dt_list == []
    timer.progress(60)
    assert dt_list == []


def test_schedule_once_schedule_from_a_callback():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []

    timer.schedule_once(lambda dt: timer.schedule_once(dt_list.append, 50), 50)
    assert dt_list == []
    timer.progress(50)
    assert dt_list == []
    timer.progress(50)
    assert dt_list == [50, ]
    timer.progress(50)
    assert dt_list == [50, ]


def test_schedule_interval():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []

    timer.schedule_interval(dt_list.append, 100)
    assert dt_list == []
    timer.progress(50)
    assert dt_list == []
    timer.progress(50)
    assert dt_list == [100, ]
    timer.progress(50)
    assert dt_list == [100, ]
    timer.progress(100)
    assert dt_list == [100, 150, ]
    timer.progress(100)
    assert dt_list == [100, 150, 100]


def test_schedule_interval_zero_interval():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []

    timer.schedule_interval(dt_list.append, 0)
    assert dt_list == []
    timer.progress(0)
    assert dt_list == [0, ]
    timer.progress(20)
    assert dt_list == [0, 20, ]
    timer.progress(0)
    assert dt_list == [0, 20, 0, ]


def test_schedule_interval_cancel():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []
    func = dt_list.append

    e = timer.schedule_interval(func, 100)
    assert dt_list == []
    timer.progress(100)
    assert dt_list == [100, ]
    e.cancel()
    timer.progress(100)
    assert dt_list == [100, ]


def test_schedule_interval_cancel_from_a_callback():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []

    def func(dt):
        dt_list.append(dt)
        if dt > 80:
            e.cancel()

    e = timer.schedule_interval(func, 30)
    timer.schedule_interval(dt_list.append, 30)
    timer.progress(30)
    assert dt_list == [30, 30, ]
    timer.progress(60)
    assert dt_list == [30, 30, 60, 60, ]
    timer.progress(90)
    assert dt_list == [30, 30, 60, 60, 90, 90, ]
    timer.progress(120)
    assert dt_list == [30, 30, 60, 60, 90, 90, 120, ]


def test_schedule_interval_schedule_from_a_callback():
    from asyncpygame._timer import Timer

    timer = Timer()
    dt_list = []

    def func(dt):
        dt_list.append(dt)
        timer.schedule_interval(dt_list.append, 10)

    timer.schedule_interval(func, 10)
    assert dt_list == []
    timer.progress(10)
    assert dt_list == [10, ]
    timer.progress(20)
    assert dt_list == [10, 20, 20, ]
    timer.progress(30)
    assert dt_list == [10, 20, 20, 30, 30, 30, ]
