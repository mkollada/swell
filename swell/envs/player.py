from pygame import sprite, image, transform
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
)


class Player(sprite.Sprite):
    def __init__(self, surfer, sprite_height=20, sprite_width=20):
        self.surfer = surfer
        self.sprite_height = sprite_height
        self.sprite_width = sprite_width

        self.surface = self.load_surface()

    def step(self, actions):
        self.surfer.step(actions)

    def load_surface(self):
        surface = image.load(self.surfer.current_image_path)
        surface = transform.scale(surface,
                                  (self.sprite_height,
                                   self.sprite_width))

        return surface


class KeyboardPlayer(Player):
    def __init__(self, surfer, sprite_height=20, sprite_width=20):
        super().__init__(surfer=surfer,
                         sprite_height=sprite_height,
                         sprite_width=sprite_width)

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

        self.surfer.step(actions)

        if actions['change_mode']:
            self.surface = self.load_surface()


