from collections.abc import Awaitable
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from asyncgui import Cancelled

from ._sleep import repeat_sleeping


async def run_in_thread(func, *, daemon=None, polling_interval=2000) -> Awaitable:
    '''
    Creates a new thread, runs a function within it, then waits for the completion of that function.

    .. code-block::

        return_value_of_func = await run_in_thread(func)
    '''
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
    async with repeat_sleeping(polling_interval) as sleep:
        while not done:
            await sleep()
    if exception is not None:
        raise exception
    return return_value


async def run_in_executor(executer: ThreadPoolExecutor, func, *, polling_interval=2000) -> Awaitable:
    '''
    Runs a function within a :class:`concurrent.futures.ThreadPoolExecutor` instance, and waits for the completion of
    the function.

    .. code-block::

        executor = ThreadPoolExecutor()
        ...
        return_value_of_func = await run_in_executor(executor, func)
    '''
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
        async with repeat_sleeping(polling_interval) as sleep:
            while not done:
                await sleep()
    except Cancelled:
        future.cancel()
        raise
    if exception is not None:
        raise exception
    return return_value
