def test_once():
    from asyncpygame._api_impl.timer import Timer
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


def test_once_zero_delay():
    from asyncpygame._api_impl.timer import Timer
    timer = Timer()
    dt_list = []

    timer.schedule_once(dt_list.append, 0)
    assert dt_list == []
    timer.progress(0)
    assert dt_list == [0, ]
    timer.progress(0)
    assert dt_list == [0, ]


def test_once_cancel():
    from asyncpygame._api_impl.timer import Timer
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


def test_once_cancel_from_a_callback():
    from asyncpygame._api_impl.timer import Timer
    timer = Timer()
    dt_list = []

    e = timer.schedule_once(dt_list.append, 100)
    timer.schedule_once(lambda __: e.cancel(), 50)
    assert dt_list == []
    timer.progress(60)
    assert dt_list == []
    timer.progress(60)
    assert dt_list == []


def test_once_schedule_from_a_callback():
    from asyncpygame._api_impl.timer import Timer
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


def test_interval():
    from asyncpygame._api_impl.timer import Timer
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


def test_interval_zero_interval():
    from asyncpygame._api_impl.timer import Timer
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


def test_interval_cancel():
    from asyncpygame._api_impl.timer import Timer
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


def test_interval_cancel_from_a_callback():
    from asyncpygame._api_impl.timer import Timer
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


def test_interval_schedule_from_a_callback():
    from asyncpygame._api_impl.timer import Timer
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


def test_sleep():
    from asyncgui import start
    from asyncpygame._api_impl.timer import Timer, sleep
    timer = Timer()
    task_state = None

    async def async_fn():
        nonlocal task_state
        task_state = 'A'
        await sleep(timer, 10)
        task_state = 'B'
        await sleep(timer, 10)
        task_state = 'C'

    task = start(async_fn())
    assert task_state == 'A'
    timer.progress(10)
    assert task_state == 'B'
    timer.progress(10)
    assert task_state == 'C'
    assert task.finished


def test_repeat_sleeping():
    from asyncgui import start
    from asyncpygame._api_impl.timer import Timer, repeat_sleeping

    timer = Timer()
    task_state = None

    async def async_fn():
        nonlocal task_state
        async with repeat_sleeping(timer, interval=10) as sleep:
            task_state = 'A'
            await sleep()
            task_state = 'B'
            await sleep()
            task_state = 'C'

    task = start(async_fn())
    assert task_state == 'A'
    timer.progress(10)
    assert task_state == 'B'
    timer.progress(10)
    assert task_state == 'C'
    assert task.finished
