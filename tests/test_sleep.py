def test_sleep():
    import asyncpygame as ap

    runner = ap.init()
    task_state = None

    async def async_fn():
        nonlocal task_state
        task_state = 'A'
        await ap.sleep(10)
        task_state = 'B'
        await ap.sleep(10)
        task_state = 'C'

    task = ap.start(async_fn())
    assert task_state == 'A'
    runner.progress(10)
    assert task_state == 'B'
    runner.progress(10)
    assert task_state == 'C'
    assert task.finished


def test_repeat_sleeping():
    import asyncpygame as ap

    runner = ap.init()
    task_state = None

    async def async_fn():
        nonlocal task_state
        async with ap.repeat_sleeping(interval=10) as sleep:
            task_state = 'A'
            await sleep()
            task_state = 'B'
            await sleep()
            task_state = 'C'

    task = ap.start(async_fn())
    assert task_state == 'A'
    runner.progress(10)
    assert task_state == 'B'
    runner.progress(10)
    assert task_state == 'C'
    assert task.finished
