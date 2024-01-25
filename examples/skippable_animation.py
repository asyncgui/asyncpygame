from functools import partial
import pygame
import pygame.font
from pygame.colordict import THECOLORS as COLORS
import asyncpygame as ap


async def skippable_animation(
        clock: ap.Clock, dispatcher: ap.SDLEventDispatcher, draw_target: pygame.Surface, group: pygame.sprite.Group,
        **kwargs):
    font = pygame.font.SysFont(None, 200)
    sprite = pygame.sprite.Sprite(group)
    sprite.image = font.render("(-.-)", True, COLORS["white"]).convert_alpha()
    sprite.rect = src_rect = sprite.image.get_rect()
    dst_rect = draw_target.get_rect()

    mouse_button_down = partial(dispatcher.wait_sdl_event, filter=lambda e: e.type == pygame.MOUSEBUTTONDOWN)
    move_sprite = partial(clock.anim_attrs, src_rect, duration=1000)

    while True:
        await ap.wait_any(mouse_button_down(), move_sprite(right=dst_rect.right))
        src_rect.right = dst_rect.right
        await ap.wait_any(mouse_button_down(), move_sprite(bottom=dst_rect.bottom))
        src_rect.bottom = dst_rect.bottom
        await ap.wait_any(mouse_button_down(), move_sprite(x=dst_rect.x))
        src_rect.x = dst_rect.x
        await ap.wait_any(mouse_button_down(), move_sprite(y=dst_rect.y))
        src_rect.y = dst_rect.y


def main():
    pygame.init()
    pygame.display.set_caption("touch the screen")
    screen = pygame.display.set_mode((1280, 720))

    clock = ap.Clock()
    dispatcher = ap.SDLEventDispatcher()
    group = pygame.sprite.Group()
    root_task = ap.start(skippable_animation(clock=clock, dispatcher=dispatcher, draw_target=screen, group=group))

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
            else:
                dispatcher.dispatch(event)
        dt = pygame_clock_tick(60)
        clock.tick(dt)
        screen.fill(bgcolor)
        group.draw(screen)
        pygame_display_flip()

    root_task.cancel()
    pygame.quit()


if __name__ == "__main__":
    main()
