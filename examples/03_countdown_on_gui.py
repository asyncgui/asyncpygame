import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as ap


async def main(*, clock: ap.Clock, **kwargs):
    pygame.init()
    pygame.display.set_caption("Countdown on GUI")
    screen = pygame.display.set_mode((400, 400))
    screen_center = screen.get_rect().center
    font = pygame.font.SysFont(None, 400)
    fgcolor = COLORS["black"]
    bgcolor = COLORS["white"]

    count_from = 3
    for i in range(count_from, -1, -1):
        img = font.render(str(i), True, fgcolor)
        screen.fill(bgcolor)
        screen.blit(img, img.get_rect(center=screen_center))
        pygame.display.flip()
        await clock.sleep(1000)


if __name__ == "__main__":
    ap.run(main)
