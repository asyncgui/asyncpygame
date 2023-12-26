import pygame
import pygame.font
import asyncpygame as ap


async def countdown(screen, *, count_from=3):
    font = pygame.font.SysFont(None, 400)
    fg_color = pygame.Color("white")
    img = pygame.Surface((0, 0))

    def draw(draw_target: pygame.Surface):
        rect = img.get_rect()
        rect.center = draw_target.get_rect().center
        draw_target.blit(img, rect)

    with ap.GraphicalEntity(draw):
        for i in range(count_from, -1, -1):
            img = font.render(str(i), True, fg_color).convert_alpha()
            await ap.sleep(1000)
        await ap.sleep_forever()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Countdown")
    screen = pygame.display.set_mode((400, 400))
    ap.run(countdown(screen, count_from=5), fps=20)
