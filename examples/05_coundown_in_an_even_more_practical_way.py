from functools import partial
import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as ap


async def countdown(*, count_from: int, screen: pygame.Surface, clock: ap.Clock, executor: ap.PriorityExecutor, priority, **kwargs):
    screen_center = screen.get_rect().center
    font = pygame.font.SysFont(None, 400)
    fgcolor = COLORS["black"]

    with executor.register(None, priority=priority) as req:
        for i in range(count_from, -1, -1):
            img = font.render(str(i), True, fgcolor).convert_alpha()
            img_rect = img.get_rect()
            img_rect.center = screen_center
            req.callback = partial(screen.blit, img, img_rect)
            await clock.sleep(1000)


async def main(*, clock: ap.Clock, executor: ap.PriorityExecutor, **kwargs):
    pygame.init()
    pygame.display.set_caption("Countdown")
    screen = pygame.display.set_mode((400, 400))

    executor.register(partial(screen.fill, COLORS["white"]), priority=0)
    executor.register(pygame.display.flip, priority=0xFFFFFF00)

    await countdown(count_from=3, screen=screen, clock=clock, executor=executor, priority=0x100)


if __name__ == "__main__":
    ap.run(main)
