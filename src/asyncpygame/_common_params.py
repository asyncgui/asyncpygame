__all__ = ('CommonParams', )

from dataclasses import dataclass
from asyncgui_ext.clock import Clock
import pygame.surface
import pygame.time

from ._priority_executor import PriorityExecutor
from ._sdlevent import SDLEvent
from .scene_switcher import SceneSwitcher


@dataclass(slots=True, kw_only=True)
class CommonParams:
    executor: PriorityExecutor
    sdlevent: SDLEvent
    clock: Clock
    pygame_clock: pygame.time.Clock = None
    draw_target: pygame.surface.Surface = None
    switcher: SceneSwitcher = None
