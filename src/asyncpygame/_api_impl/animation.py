from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from .timer import TimeUnit, repeat_sleeping


async def anim_with_dt(timer, *, step=0) -> AsyncIterator[TimeUnit]:
    async with repeat_sleeping(timer, interval=step) as sleep:
        while True:
            yield await sleep()


async def anim_with_et(timer, *, step=0) -> AsyncIterator[TimeUnit]:
    et = 0.
    async with repeat_sleeping(timer, interval=step) as sleep:
        while True:
            et += await sleep()
            yield et


async def anim_with_dt_et(timer, *, step=0) -> AsyncIterator[tuple[TimeUnit, TimeUnit]]:
    et = 0.
    async with repeat_sleeping(timer, interval=step) as sleep:
        while True:
            dt = await sleep()
            et += dt
            yield dt, et


async def anim_with_ratio(timer, *, duration=1000, step=0) -> AsyncIterator[float]:
    et = 0.
    async with repeat_sleeping(timer, interval=step) as sleep:
        while et < duration:
            et += await sleep()
            yield et / duration


async def anim_with_dt_et_ratio(timer, *, duration=1000, step=0) -> AsyncIterator[tuple[TimeUnit, TimeUnit, float]]:
    et = 0.
    async with repeat_sleeping(timer, interval=step) as sleep:
        while et < duration:
            dt = await sleep()
            et += dt
            yield dt, et, et / duration


@asynccontextmanager
async def fade_transition(timer, surface, *, duration=1000):
    half_duration = duration // 2
    org_alpha = surface.get_alpha()
    base_alpha = 255 if org_alpha is None else org_alpha
    set_alpha = surface.set_alpha
    async for p in anim_with_ratio(timer, duration=half_duration):
        p = 1.0 - p
        set_alpha(int(p * base_alpha))
    try:
        yield
        async for p in anim_with_ratio(timer, duration=half_duration):
            set_alpha(int(p * base_alpha))
    finally:
        set_alpha(org_alpha)
