'''
This file allows you to run swell and play the game using the keyboard
'''
from functools import partial
import pygame
from pygame.locals import K_ESCAPE

from swell.envs.surf import Swell, SurfBreak, angled_sea_floor
from swell.envs.surfer import Surfer
from swell.envs.viz import SurfBreakViz, SurferViz
from swell.envs.player import KeyboardPlayer


def run_game(viz, player, fps=100):
    # Pygame implementation
    successes, failures = pygame.init()
    screen = pygame.display.set_mode((viz.surfbreak.width,
                                      viz.surfbreak.height))
    clock = pygame.time.Clock()
    pygame.time.set_timer(STEPALL, fps)

    my_font = pygame.font.SysFont("monospace", 16)
    score_text = my_font.render("Stoke: " + str(player.surfer_viz.surfer.total_stoke),
                                1, (0, 0, 0))
    screen.blit(score_text, (5, 5))

    running = True
    while running:
        clock.tick(fps)
        # Did the user click the window close button?
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pressed_keys[K_ESCAPE]:
                running = False
            if event.type == STEPALL:
                viz.step()
                player.step(pressed_keys)
                screen.blit(viz.surface, (0, 0))
                screen.blit(player.surfer_viz.surface,
                            ((player.surfer_viz.surfer.x - player.surfer_viz.sprite_width / 2),
                             (player.surfer_viz.surfer.y - player.surfer_viz.sprite_height / 2)))
                score_text = my_font.render("Stoke: " + str(player.surfer_viz.surfer.total_stoke),
                                            1, (0, 0, 0))
                screen.blit(score_text, (5, 5))
                pygame.display.flip()

    pygame.quit()


STEPALL = pygame.USEREVENT + 1
FPS = 100

if __name__ == '__main__':
    # Generate Break and Swell
    floor = partial(angled_sea_floor,
                    parallel_coef=0.03,
                    perp_coef=.25,
                    low_depth=50)

    swell = Swell(period=100, height=8, width=16, angle=2, speed=4)
    sb = SurfBreak(height=250,
                   width=200,
                   sea_floor_func=floor,
                   tide_init=1,
                   swell=swell,
                   water_friction_coef=0.85)
    sb_viz = SurfBreakViz(surfbreak=sb)
    surfer = Surfer(surfbreak=sb,
                    init_x=0,
                    init_y=0,
                    paddle_speed=1,
                    turn_speed=1)
    surfer_viz = SurferViz(surfer=surfer)
    player1 = KeyboardPlayer(surfer_viz=surfer_viz)

    run_game(sb_viz, player1, fps=FPS)
