'''
Shows how :func:`asyncpygame.move_on_after` works.
'''

import pygame
import pygame.font
import asyncpygame as ap


async def main(draw_target):
    font = pygame.font.SysFont(None, 40)
    img = font.render("This animation will be interrupted in 6 seconds", True, pygame.Color("white")).convert_alpha()
    dst_rect = draw_target.get_rect()
    img_rect = img.get_rect()
    img_rect.centerx = dst_rect.centerx
    velocity_y = 0.4  # pixels per milli seconds

    def draw(draw_target: pygame.Surface):
        draw_target.blit(img, img_rect)

    with ap.GraphicalEntity(draw):
        async with ap.move_on_after(6000):
            while True:
                async for dt in ap.anim_with_dt():
                    img_rect.move_ip(0, dt * velocity_y)
                    if img_rect.bottom > dst_rect.bottom:
                        break
                async for dt in ap.anim_with_dt():
                    img_rect.move_ip(0, -dt * velocity_y)
                    if img_rect.top < dst_rect.top:
                        break

        await ap.sleep(500)
        async for ratio in ap.anim_with_ratio(duration=1000):
            new_alpha = (1. - ratio) * 255
            img.set_alpha(new_alpha)


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("move_on_after")
    screen = pygame.display.set_mode((800, 600))
    ap.run(main(screen), fps=60, draw_target=screen, bgcolor=pygame.Color("black"))
