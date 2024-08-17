import pygame
import asyncpygame as ap


async def main(*, sdlevent: ap.SDLEvent, **kwargs):
    pygame.init()
    pygame.display.set_caption("Event Handling")
    pygame.display.set_mode((400, 400))

    while True:
        e = await sdlevent.wait(pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)
        print(e)


if __name__ == "__main__":
    ap.run(main)
