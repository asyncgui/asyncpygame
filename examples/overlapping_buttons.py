'''
ボタンが重なっている部分をクリックした時に上にある物のみを反応させる例。

二つのボタンそれぞれに異なる

'''
from functools import partial
import pygame
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP
import pygame.font
import asyncpygame as ap


def button_press_filter(collision_rect, event):
    return event.type == MOUSEBUTTONDOWN and collision_rect.collidepoint(event.pos) and ap.STOP_DISPATCHING


def button_release_filter(button, event):
    return event.type == MOUSEBUTTONUP and button == event.button


async def button(*, text, font, bgcolor, fgcolor, zorder, dst):
    final_img = pygame.Surface(dst.size)
    final_img.fill(bgcolor)
    img = font.render(text, True, fgcolor)
    img_rect = img.get_rect()
    img_rect.center = final_img.get_rect().center
    final_img.blit(img, img_rect)
    del img, img_rect

    def draw(draw_target: pygame.Surface):
        draw_target.blit(final_img, dst)

    with ap.GraphicalEntity(draw):
        while True:
            button_press_event = await ap.sdl_event(priority=zorder, filter=partial(button_press_filter, dst))
            final_img.set_alpha(150)
            print(f"'{text}' pressed")
            await ap.sdl_event(priority=zorder, filter=partial(button_release_filter, button_press_event.button))
            final_img.set_alpha(255)
            print(f"'{text}' released")


async def main(draw_target):
    Color = pygame.Color
    font = pygame.font.SysFont(None, 100)
    await ap.wait_all(
        button(
            text='Orange', font=font, zorder=0,
            bgcolor=Color("orange"), fgcolor=Color("black"),
            dst=pygame.Rect(20, 100, 400, 150),
        ),
        button(
            text='Blue', font=font, zorder=1,
            bgcolor=Color("blue"), fgcolor=Color("black"),
            dst=pygame.Rect(300, 200, 400, 150),
        ),
    )

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("overlappng buttons")
    screen = pygame.display.set_mode((800, 600))
    ap.run(main(screen), fps=30, draw_target=screen, bgcolor=pygame.Color("black"))
