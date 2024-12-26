__all__ = (
    'Transition', 'SceneSwitcher',
    'no_transition', 'FadeTransition', 'SlideTransition',
)

from typing import TypeAlias, Any
from collections.abc import AsyncGenerator, Callable
from functools import partial

import asyncgui as ag
from pygame.math import Vector2

from ._utils import capture_current_frame, block_input_events


Transition: TypeAlias = Callable[..., AsyncGenerator[None, None]]
'''
``Transition`` is a :any:`collections.abc.Callable` that returns an async generator that yields twice.
It defines a transition between two scenes.

.. code-block::

    async def my_transition(**common_params):
        # 1st part
        yield
        # 2nd part
        yield
        # 3rd part

    switcher.switch_to(next_scene, my_transition)

When your app switches from one scene to another, the transition between them will proceed as follows:

* The 1st part of the transition and the current scene run concurrently.
* The current scene gets cancelled.
* The 2nd part of the transition runs.
* The next scene starts.
* The 3rd part of the transition and the next scene run concurrently.

::

    time ------------------------------------------------------>

    ----------------------|          |------------------------
        current scene     |          |      next scene
    ----------------------|          |------------------------

               |----------|----------|----------|
               | 1st part | 2nd part | 3rd part |
               |----------|----------|----------|
'''


async def no_transition(**common_params):
    '''
    .. code-block::

        switcher.switch_to(next_scene, no_transition)
    '''
    yield
    yield


class SceneSwitcher:
    def __init__(self):
        self._next_scene_request = ag.ExclusiveEvent()

    def switch_to(self, next_scene, transition: Transition=no_transition):
        '''
        Instructs the scene switcher to transition to another scene.
        Calling this method during an ongoing transition will have no effect.
        '''
        self._next_scene_request.fire(next_scene, transition)

    async def run(self, first_scene, *, userdata: Any=None, priority, sdlevent, **kwargs):
        '''
        :param userdata: Use this to share data between scenes without relying on global variables.
        '''
        common_params = {
            'switcher': self,
            'sdlevent': sdlevent,
            'userdata': userdata,
            **kwargs}
        async with ag.open_nursery() as nursery:
            task = nursery.start(first_scene(**common_params))
            while True:
                next_scene, transition = (await self._next_scene_request.wait())[0]
                agen = transition(priority=priority, **common_params)
                try:
                    with block_input_events(sdlevent, priority):
                        await agen.asend(None)
                        task.cancel()
                        await agen.asend(None)
                        task = nursery.start(next_scene(**common_params))
                        try:
                            await agen.asend(None)
                        except StopAsyncIteration:
                            pass
                        else:
                            await agen.aclose()
                finally:
                    await agen.aclose()


class FadeTransition:
    '''
    .. code-block::

        switcher.switch_to(next_scene, FadeTransition())
    '''
    def __init__(self, *, overlay_color='black', out_duration=300, in_duration=300, interval=100):
        '''
        :param out_duration: The duration of the fadeout animation.
        :param in_duration: The duration of the fadein animation.
        :param interval: The interval between the fadeout animation and the fadein animation.
        '''
        self.overlay_color = overlay_color
        self.out_duration = out_duration
        self.in_duration = in_duration
        self.interval = interval

    async def __call__(self, *, priority, draw_target, clock, executor, **kwargs):
        overlay_surface = draw_target.copy()
        overlay_surface.fill(self.overlay_color)
        set_alpha = overlay_surface.set_alpha
        with executor.register(partial(draw_target.blit, overlay_surface), priority=priority):
            async for v in clock.interpolate(0, 255, duration=self.out_duration):
                set_alpha(v)
            yield
            await clock.sleep(self.interval)
            yield
            async for v in clock.interpolate(255, 0, duration=self.in_duration):
                set_alpha(v)


class _ScrollInst:
    def __init__(self, surface, dx, dy):
        self.surface = surface
        self.dx = dx
        self.dy = dy

    def __call__(self):
        self.surface.scroll(self.dx, self.dy)


class SlideTransition:
    '''
    .. code-block::

        switcher.switch_to(next_scene, SlideTransition())
    '''
    _valid_directions = ('right', 'left', 'up', 'down', )

    def __init__(self, *, direction='right', duration=800):
        '''
        :param direction: 'right', 'left', 'up' or 'down'.
        :param duration: The duration of the sliding animation.
        '''
        if direction not in self._valid_directions:
            raise ValueError(f"Direction must be one of {self.valid_directions}. : (was {direction})")
        self.direction = direction
        self.duration = duration

    async def __call__(self, *, priority, draw_target, clock, executor, **kwargs):
        # Naming rules:
        #   xxx1 ... something for the current scene
        #   xxx2 ... something for the next scene
        frame1 = await capture_current_frame(executor, priority, draw_target)
        yield
        yield

        # LOAD_FAST
        int_ = int
        direction = self.direction

        is_backward = direction in ('left', 'up', )
        is_vertical = direction in ('up', 'down', )
        base_distance = draw_target.height if is_vertical else draw_target.width
        base_distance = -base_distance if is_backward else base_distance
        end_pos1 = base_distance
        start_pos2 = -base_distance

        dest1 = Vector2(0, 0)
        scroll_inst = _ScrollInst(draw_target, 0, 0)
        if is_vertical:
            scroll_inst.dy = start_pos2
        else:
            scroll_inst.dx = start_pos2

        with (
            executor.register(scroll_inst, priority),
            executor.register(partial(draw_target.blit, frame1, dest1), priority + 1),
        ):
            async for v in clock.interpolate(0, end_pos1, duration=self.duration):
                v = int_(v)
                if is_vertical:
                    dest1.y = v
                    scroll_inst.dy = start_pos2 + v
                else:
                    dest1.x = v
                    scroll_inst.dx = start_pos2 + v
