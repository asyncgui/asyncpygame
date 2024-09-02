import pygame
import asyncpygame as ap


async def main(*, clock: ap.Clock, **kwargs):
    pygame.init()

    count_from = 3
    for i in range(count_from, -1, -1):
        print(i)
        await clock.sleep(1000)
    ap.quit()


if __name__ == "__main__":
    ap.run(main)
