import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as ap


async def loop_animation(clock: ap.Clock, draw_target: pygame.Surface, group: pygame.sprite.Group, **kwargs):
    font = pygame.font.SysFont(None, 200)
    sprite = pygame.sprite.Sprite(group)
    sprite.image = font.render("(-.-)", True, COLORS["white"]).convert_alpha()
    sprite.rect = src_rect = sprite.image.get_rect()
    dst_rect = draw_target.get_rect()

    while True:
        await clock.anim_attrs(src_rect, duration=1000, right=dst_rect.right)
        await clock.anim_attrs(src_rect, duration=1000, bottom=dst_rect.bottom)
        await clock.anim_attrs(src_rect, duration=1000, x=dst_rect.x)
        await clock.anim_attrs(src_rect, duration=1000, y=dst_rect.y)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    clock = ap.Clock()
    group = pygame.sprite.Group()
    root_task = ap.start(loop_animation(clock=clock, draw_target=screen, group=group))

    # LOAD_FAST
    QUIT = pygame.QUIT
    pygame_display_flip = pygame.display.flip
    pygame_event_get = pygame.event.get
    pygame_clock_tick = pygame.Clock().tick
    bgcolor = COLORS["black"]

    alive = True
    while alive:
        for event in pygame_event_get():
            if event.type == QUIT:
                alive = False
        dt = pygame_clock_tick(30)
        clock.tick(dt)
        screen.fill(bgcolor)
        group.draw(screen)
        pygame_display_flip()

    root_task.cancel()
    pygame.quit()


if __name__ == "__main__":
    main()
