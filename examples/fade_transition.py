import string
import pygame
from pygame import freetype
import asyncpygame as ap


async def main(screen):
    font = freetype.SysFont(None, 400)
    fg_color = pygame.Color("white")
    bg_color = (0, 0, 0, 0)
    screen_rect = screen.get_rect()
    img = pygame.Surface(screen.get_size())

    def draw(draw_target: pygame.Surface):
        draw_target.blit(img, (0, 0, ))

    with ap.GraphicalEntity(draw):
        for c in string.ascii_uppercase:
            rect = font.get_rect(c)
            rect.center = screen_rect.center
            async with ap.fade_transition(img):
                img.fill(bg_color)
                font.render_to(img, rect, c, fg_color)
            await ap.sdl_event(filter=lambda e: e.type == pygame.MOUSEBUTTONDOWN)
        await ap.sleep_forever()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("fade transition")
    screen = pygame.display.set_mode((400, 400))
    ap.run(main(screen), fps=30, draw_target=screen, bgcolor=pygame.Color("black"))
