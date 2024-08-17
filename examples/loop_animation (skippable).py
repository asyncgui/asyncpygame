from functools import partial
import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as ap


async def main(*, clock: ap.Clock, executor: ap.PriorityExecutor, sdlevent: ap.SDLEvent, **kwargs):
    pygame.init()
    pygame.display.set_caption("Touching the screen will skip the animation")

    screen = pygame.display.set_mode((1280, 720))
    font = pygame.font.SysFont(None, 200)
    img = font.render("(^.^)", True, COLORS["white"]).convert_alpha()
    img_rect = img.get_rect()
    screen_rect = screen.get_rect()

    r = executor.register
    r(partial(screen.fill, COLORS["black"]), priority=0)
    r(partial(screen.blit, img, img_rect), priority=0x100)
    r(pygame.display.flip, priority=0xFFFFFF00)
    del r

    mouse_button_down = partial(sdlevent.wait, pygame.MOUSEBUTTONDOWN)
    move_sprite = partial(clock.anim_attrs, img_rect, duration=1000)

    while True:
        await ap.wait_any(mouse_button_down(), move_sprite(right=screen_rect.right))
        img_rect.right = screen_rect.right
        await ap.wait_any(mouse_button_down(), move_sprite(bottom=screen_rect.bottom))
        img_rect.bottom = screen_rect.bottom
        await ap.wait_any(mouse_button_down(), move_sprite(x=screen_rect.x))
        img_rect.x = screen_rect.x
        await ap.wait_any(mouse_button_down(), move_sprite(y=screen_rect.y))
        img_rect.y = screen_rect.y


if __name__ == "__main__":
    ap.run(main, fps=60)