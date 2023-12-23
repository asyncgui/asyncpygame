import pytest
from concurrent.futures import ThreadPoolExecutor
import threading


def test_thread_id():
    from asyncgui import start
    from asyncpygame._api_impl.threads import Timer, run_in_executor

    async def job():
        before = threading.get_ident()
        await run_in_executor(timer, executor, lambda: None, polling_interval=0)
        after = threading.get_ident()
        assert before == after

    timer = Timer()
    with ThreadPoolExecutor() as executor:
        task = start(job())
    timer.progress(0)
    assert task.finished


def test_propagate_exception():
    from asyncgui import start
    from asyncpygame._api_impl.threads import Timer, run_in_executor

    async def job():
        with pytest.raises(ZeroDivisionError):
            await run_in_executor(timer, executor, lambda: 1 / 0, polling_interval=0)

    timer = Timer()

    with ThreadPoolExecutor() as executor:
        task = start(job())
    timer.progress(0)
    assert task.finished


def test_no_exception():
    from asyncgui import start
    from asyncpygame._api_impl.threads import Timer, run_in_executor

    async def job():
        assert 'A' == await run_in_executor(timer, executor, lambda: 'A', polling_interval=0)

    timer = Timer()
    with ThreadPoolExecutor() as executor:
        task = start(job())
    timer.progress(0)
    assert task.finished


def test_cancel_before_getting_excuted():
    import time
    from asyncgui import Event, start
    from asyncpygame._api_impl.threads import Timer, run_in_executor

    flag = Event()

    async def job():
        await run_in_executor(timer, executor, flag.set, polling_interval=0)

    timer = Timer()
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(time.sleep, .1)
        task = start(job())
        time.sleep(.02)
        assert not task.finished
        assert not flag.is_set
        timer.progress(0)
        task.cancel()
        assert task.cancelled
        assert not flag.is_set
        time.sleep(.2)
        assert not flag.is_set
