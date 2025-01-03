from functools import partial
import pygame
import pygame.font
from pygame.colordict import THECOLORS
import asyncpygame as apg


async def main(*, clock: apg.Clock, executor: apg.PriorityExecutor, **kwargs):
    pygame.init()
    pygame.display.set_caption("Countdown")
    screen = pygame.display.set_mode((400, 400))
    screen_center = screen.get_rect().center
    font = pygame.font.SysFont(None, 400)
    fgcolor = THECOLORS["black"]

    # Functions with a lower priority will be called earlier.
    executor.register(partial(screen.fill, THECOLORS["white"]), priority=0)
    req = executor.register(None, priority=0x100)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)

    count_from = 3
    for i in range(count_from, -1, -1):
        img = font.render(str(i), True, fgcolor).convert_alpha()
        req.callback = partial(screen.blit, img, img.get_rect(center=screen_center))
        await clock.sleep(1000)


if __name__ == "__main__":
    apg.run(main)
