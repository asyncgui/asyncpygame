import pygame
import asyncpygame as apg


async def main(*, clock: apg.Clock, **kwargs):
    pygame.init()

    count_from = 3
    for i in range(count_from, -1, -1):
        print(i)
        await clock.sleep(1000)
    apg.quit()


if __name__ == "__main__":
    apg.run(main)
