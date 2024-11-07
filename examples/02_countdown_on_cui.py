import pygame
import asyncpygame as apg


async def main(cp: apg.CommonParams):
    pygame.init()

    count_from = 3
    for i in range(count_from, -1, -1):
        print(i)
        await cp.clock.sleep(1000)
    apg.quit()


if __name__ == "__main__":
    apg.run(main)
