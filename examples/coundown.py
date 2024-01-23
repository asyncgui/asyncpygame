import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as ap


async def countdown(*, clock: ap.Clock, draw_target: pygame.Surface, count_from=3):
    pygame_display_flip = pygame.display.flip
    font = pygame.font.SysFont(None, 400)
    bgcolor = COLORS["black"]
    fgcolor = COLORS["white"]
    center = draw_target.get_rect().center

    for i in range(count_from, -1, -1):
        draw_target.fill(bgcolor)
        img = font.render(str(i), True, fgcolor)
        img_rect = img.get_rect()
        img_rect.center = center
        draw_target.blit(img, img_rect)
        pygame_display_flip()
        await clock.sleep(1000)


def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))

    clock = ap.Clock()
    root_task = ap.start(countdown(clock=clock, draw_target=screen, count_from=5))

    # LOAD_FAST
    QUIT = pygame.QUIT
    pygame_event_get = pygame.event.get
    pygame_clock_tick = pygame.Clock().tick

    alive = True
    while alive:
        for event in pygame_event_get():
            if event.type == QUIT:
                alive = False
        dt = pygame_clock_tick(30)
        clock.tick(dt)

    root_task.cancel()
    pygame.quit()


if __name__ == "__main__":
    main()
