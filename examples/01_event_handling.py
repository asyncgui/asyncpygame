import pygame
import asyncpygame as apg


async def main(*, sdlevent: apg.SDLEvent, **kwargs):
    pygame.init()
    pygame.display.set_caption("Event Handling")
    pygame.display.set_mode((400, 400))

    while True:
        e = await sdlevent.wait(pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, priority=0x100)
        print(e)


if __name__ == "__main__":
    apg.run(main)
