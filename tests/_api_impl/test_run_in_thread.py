import pytest
import threading
import time


@pytest.mark.parametrize('daemon', (True, False))
def test_thread_id(daemon):
    from asyncgui import start
    from asyncpygame._api_impl.threads import Timer, run_in_thread

    async def job():
        before = threading.get_ident()
        await run_in_thread(timer, lambda: None, daemon=daemon, polling_interval=0)
        after = threading.get_ident()
        assert before == after

    timer = Timer()
    task = start(job())
    time.sleep(.01)
    timer.progress(0)
    assert task.finished


@pytest.mark.parametrize('daemon', (True, False))
def test_propagate_exception(daemon):
    from asyncgui import start
    from asyncpygame._api_impl.threads import Timer, run_in_thread

    async def job():
        with pytest.raises(ZeroDivisionError):
            await run_in_thread(timer, lambda: 1 / 0, daemon=daemon, polling_interval=0)

    timer = Timer()
    task = start(job())
    time.sleep(.01)
    timer.progress(0)
    assert task.finished


@pytest.mark.parametrize('daemon', (True, False))
def test_no_exception(daemon):
    from asyncgui import start
    from asyncpygame._api_impl.threads import Timer, run_in_thread

    async def job():
        assert 'A' == await run_in_thread(timer, lambda: 'A', daemon=daemon, polling_interval=0)

    timer = Timer()
    task = start(job())
    time.sleep(.01)
    timer.progress(0)
    assert task.finished
