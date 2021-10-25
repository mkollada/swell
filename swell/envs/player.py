from pygame import sprite, image, transform
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
)


class KeyboardPlayer:
    def __init__(self, surfer_viz):
        self.surfer_viz = surfer_viz

    def step(self, pressed_keys):
        key_map = {
            K_UP: 'up',
            K_DOWN: 'down',
            K_LEFT: 'left',
            K_RIGHT: 'right',
            K_SPACE: 'change_mode',
        }

        actions = {}
        for key in key_map:
            actions[key_map[key]] = pressed_keys[key]

        self.surfer_viz.step(actions)