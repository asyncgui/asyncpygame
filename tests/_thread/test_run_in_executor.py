import pytest
from concurrent.futures import ThreadPoolExecutor
import threading


def test_thread_id():
    import asyncpygame as ap

    async def job():
        before = threading.get_ident()
        await ap.run_in_executor(executor, lambda: None, polling_interval=0)
        after = threading.get_ident()
        assert before == after

    runner = ap.init()
    with ThreadPoolExecutor() as executor:
        task = ap.start(job())
    runner.progress(0)
    assert task.finished


def test_propagate_exception():
    import asyncpygame as ap

    async def job():
        with pytest.raises(ZeroDivisionError):
            await ap.run_in_executor(executor, lambda: 1 / 0, polling_interval=0)

    runner = ap.init()

    with ThreadPoolExecutor() as executor:
        task = ap.start(job())
    runner.progress(0)
    assert task.finished


def test_no_exception():
    import asyncpygame as ap

    async def job():
        assert 'A' == await ap.run_in_executor(executor, lambda: 'A', polling_interval=0)

    runner = ap.init()
    with ThreadPoolExecutor() as executor:
        task = ap.start(job())
    runner.progress(0)
    assert task.finished


def test_cancel_before_getting_excuted():
    import time
    import asyncpygame as ap

    flag = ap.Event()

    async def job():
        await ap.run_in_executor(executor, flag.set, polling_interval=0)

    runner = ap.init()
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(time.sleep, .1)
        task = ap.start(job())
        time.sleep(.02)
        assert not task.finished
        assert not flag.is_set
        runner.progress(0)
        task.cancel()
        assert task.cancelled
        assert not flag.is_set
        time.sleep(.2)
        assert not flag.is_set
