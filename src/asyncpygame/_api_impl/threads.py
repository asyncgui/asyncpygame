from collections.abc import Awaitable
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from asyncgui import Cancelled

from .timer import Timer, repeat_sleeping


async def run_in_thread(timer: Timer, func, *, daemon=None, polling_interval=2000) -> Awaitable:
    return_value = None
    exception = None
    done = False

    def wrapper():
        nonlocal return_value, done, exception
        try:
            return_value = func()
        except Exception as e:
            exception = e
        finally:
            done = True

    Thread(target=wrapper, daemon=daemon).start()
    async with repeat_sleeping(timer, interval=polling_interval) as sleep:
        while not done:
            await sleep()
    if exception is not None:
        raise exception
    return return_value


async def run_in_executor(timer: Timer, executer: ThreadPoolExecutor, func, *, polling_interval=2000) -> Awaitable:
    return_value = None
    exception = None
    done = False

    def wrapper():
        nonlocal return_value, done, exception
        try:
            return_value = func()
        except Exception as e:
            exception = e
        finally:
            done = True

    future = executer.submit(wrapper)
    try:
        async with repeat_sleeping(timer, interval=polling_interval) as sleep:
            while not done:
                await sleep()
    except Cancelled:
        future.cancel()
        raise
    if exception is not None:
        raise exception
    return return_value
