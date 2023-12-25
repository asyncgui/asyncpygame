import pytest
import threading
import time


@pytest.mark.parametrize('daemon', (True, False))
def test_thread_id(daemon):
    import asyncpygame as ap

    async def job():
        before = threading.get_ident()
        await ap.run_in_thread(lambda: None, daemon=daemon, polling_interval=0)
        after = threading.get_ident()
        assert before == after

    runner = ap.init()
    task = ap.start(job())
    time.sleep(.01)
    runner.progress(0)
    assert task.finished


@pytest.mark.parametrize('daemon', (True, False))
def test_propagate_exception(daemon):
    import asyncpygame as ap

    async def job():
        with pytest.raises(ZeroDivisionError):
            await ap.run_in_thread(lambda: 1 / 0, daemon=daemon, polling_interval=0)

    runner = ap.init()
    task = ap.start(job())
    time.sleep(.01)
    runner.progress(0)
    assert task.finished


@pytest.mark.parametrize('daemon', (True, False))
def test_no_exception(daemon):
    import asyncpygame as ap

    async def job():
        assert 'A' == await ap.run_in_thread(lambda: 'A', daemon=daemon, polling_interval=0)

    runner = ap.init()
    task = ap.start(job())
    time.sleep(.01)
    runner.progress(0)
    assert task.finished
