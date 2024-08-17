'''
Performance comparision between 'SDLEvent.wait()' and 'SDLEvent.wait_freq()'.
'''

import asyncpygame


async def nothing(sdlvent):
    pass


async def repeat_wait(sdlevent):
    while True:
        e = await sdlevent.wait(1)


async def repeat_wait_freq(sdlevent):
    async with sdlevent.wait_freq(1) as event:
        while True:
            e = await event()


async def _measure_one(*, n_events, n_tasks, target):
    from time import perf_counter
    from pygame.event import Event
    sdlevent = asyncpygame.SDLEvent()
    dispatch = sdlevent.dispatch

    async with asyncpygame.open_nursery() as nursery:
        start_time = perf_counter()
        for i in range(n_tasks):
            nursery.start(target(sdlevent))
        for i in range(n_events):
            dispatch(Event(1))
        end_time = perf_counter()
        nursery.close()
    return end_time - start_time


def measure_one(*, n_events, n_tasks, target):
    task = asyncpygame.start(_measure_one(n_events=n_events, n_tasks=n_tasks, target=target))
    return task.result


def measure_and_plot_all():
    import matplotlib.pyplot as plt

    for n_events in (1, 2, 3, 4, 5, 10, 20, 50, 100):
        fig, ax = plt.subplots()
        ax.set_title(f'Number of Events : {n_events}')
        ax.set_xlabel('Number of Tasks')
        ax.set_ylabel('Time')
        n_times = 100

        yvalues = [
            sum(measure_one(n_events=n_events, n_tasks=n_tasks, target=repeat_wait) for __ in range(n_times))
            for n_tasks in range(1, 11)
        ]
        ax.plot(list(range(1, 11)), yvalues, color='green', label='wait')
        yvalues = [
            sum(measure_one(n_events=n_events, n_tasks=n_tasks, target=repeat_wait_freq) for __ in range(n_times))
            for n_tasks in range(1, 11)
        ]
        ax.plot(list(range(1, 11)), yvalues, color='blue', label='wait_freq')

        fig.savefig(__file__ + f'_n_events_{n_events}.png', )


if __name__ == '__main__':
    measure_and_plot_all()
