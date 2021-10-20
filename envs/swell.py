import numpy as np
import seaborn as sns
import math
from functools import partial
import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


'''
To-do:
- Implement paddle vs ride mode
    - paddle mode is as currently is
    = ride mode should activate when the player presses a specified key
        - in ride mode
            - you can only redirect speed, you can no longer "paddle"
                - keys are used to turn instead of paddle
            - agents will only get points when in ride mode
- work on best wave dynamics
    - adjust "crashing" calculation
- implement an agent
    - generate state vectors from surfbreak
'''

WAVE_MAX_HEIGHT = 20
SEAFLOOR_MIN_HEIGHT = -20
SEA_COLOR_PALETTE = sns.color_palette('Blues', n_colors=80)[40:]
for ix, color in enumerate(SEA_COLOR_PALETTE):
    r, g, b = int(255 * color[0]), int(255 * color[1]), int(255 * color[2])
    SEA_COLOR_PALETTE[ix] = (r, g, b)
CRASH_COLOR = (255, 255, 255)
BEACH_COLOR = (230, 207, 138)
WAVE_BREAK_RATIO = 2


def flat_sea_floor(height, width, depth):
    return np.zeros((height, width)) + depth


def angled_sea_floor(height, width, parallel_coef, perp_coef, low_depth):
    floor = np.zeros((height, width))
    for x in range(width):
        for y in range(height):
            floor[y, x] = y * parallel_coef + x * perp_coef - low_depth

    return floor


class SurfBreakViz:
    def __init__(self, surfbreak):
        self.surfbreak = surfbreak

        self.surface = pygame.Surface((surfbreak.width, surfbreak.height))
        self.init_image()

    def step(self):
        self.surfbreak.step()
        self.get_image()

    def init_image(self):
        """
        Transforms from a Surfbreak object to the rgb pixel color space
        :param surfbreak: the image that will be transformed
        :return: image - the image transformed into the rgb pixel space
        """
        # image = list(self.image)
        pixel_array = pygame.PixelArray(self.surface)
        for y in range(self.surfbreak.height):
            for x in range(self.surfbreak.width):
                if self.surfbreak.base_water_level <= self.surfbreak.sea_floor[y, x]:
                    rgb = BEACH_COLOR
                elif self.surfbreak.crashing[y, x] > WAVE_BREAK_RATIO:
                    rgb = CRASH_COLOR
                else:
                    rgb = SEA_COLOR_PALETTE[int(self.surfbreak.active_water_level[y, x])
                                            - SEAFLOOR_MIN_HEIGHT]

                # pixel_array[y, x] = pygame.Color(rgb)
                pixel_array[x, y] = pygame.Color(rgb)

        self.surface = pixel_array.make_surface()
        pixel_array.close()

        return self.surface

    def get_image(self):
        # image = list(self.image)
        # We update where the wave was and where it is now
        pixel_array = pygame.PixelArray(self.surface)
        for wave in self.surfbreak.swell.waves:
            for (y, x) in wave.coordinates:
                rgb = self.map_to_rgb(y, x)
                # pixel_array[y, x] = pygame.Color(rgb)
                pixel_array[x, y] = pygame.Color(rgb)
            for (y, x) in wave.last_coordinates:
                rgb = self.map_to_rgb(y, x)
                # pixel_array[y, x] = pygame.Color(rgb)
                pixel_array[x, y] = pygame.Color(rgb)

        self.surface = pixel_array.make_surface()
        pixel_array.close()

        return self.surface

    def map_to_rgb(self, y, x):
        if self.surfbreak.base_water_level <= \
                self.surfbreak.sea_floor[y, x]:
            return BEACH_COLOR
        elif self.surfbreak.crashing[y, x] > WAVE_BREAK_RATIO:
            return CRASH_COLOR
        else:
            ix = int(self.surfbreak.active_water_level[y, x]) \
                 - SEAFLOOR_MIN_HEIGHT

            if ix >= len(SEA_COLOR_PALETTE):
                ix = len(SEA_COLOR_PALETTE) - 1
            elif ix < 0:
                ix = 0
            return SEA_COLOR_PALETTE[ix]


class SurfBreak:
    def __init__(self, height, width, sea_floor_func, tide_init, swell):
        """
        Defines a break environment

        Defines a surf break environment that is a 2D grid with characteristics
        at each coordinate including, seafloor height, water height, and
        whether or not the water is crashing
        """

        self.height = height
        self.width = width
        self.sea_floor = sea_floor_func(height, width)  # TO-DO define sea floor func
        self.base_water_level = tide_init
        self.active_water_level = np.zeros((height, width)) + tide_init
        self.crashing = np.zeros((height, width))
        self.swell = swell

        self.counter = 0

    def step(self):
        """
        Moves break one time step forward
        :return: None
        """
        self.active_water_level = np.zeros((self.height, self.width)) + \
                                  self.base_water_level
        self.crashing = np.zeros((self.height, self.width))
        for wave in self.swell.waves:
            wave.last_coordinates = wave.coordinates
            wave.coordinates = []
            for x in range(self.width):
                y = int(wave.angle * x - wave.counter * wave.speed)
                for i in range(wave.width):
                    _y = y + i
                    if (_y < sb.height) and (_y >= 0):
                        self.active_water_level[_y, x] += wave.height
                        if self.base_water_level > self.sea_floor[_y, x]:
                            self.crashing[_y, x] = \
                            math.log(
                                (-1 * ((2 * wave.height / wave.width) * np.abs((wave.width / 2) - i)
                                       - wave.height) /
                                 (self.base_water_level - self.sea_floor[_y, x])) + 1
                            )
                            # self.check_crashing()
                            wave.coordinates.append((_y, x))
            wave.step()

        self.swell.step()

        self.counter += 1

    def add_wave(self, wave):
        self.swell.append(wave)


class Wave:
    def __init__(self, height, width, angle, speed):
        """
        Defines a wave within a break

        Defines a wave within a surf break as a function of the time its been
        moving
        """
        self.height = height
        self.width = width
        self.angle = angle
        self.speed = speed
        self.counter = 0
        self.coordinates = []
        self.last_coordinates = []

    def step(self):
        self.counter += 1

        return self


class Swell:
    def __init__(self, period, height, width, angle, speed):
        """
        Defines a function that creates waves

        To-do: make a wave generator instead of just inputting waves
        """
        self.height = height
        self.width = width
        self.angle = angle
        self.speed = speed
        self.period = period
        self.waves = []
        self.counter = 0

    def step(self):
        if (self.counter % self.period) == 0:
            self.generate_wave()
        self.counter += 1

    def generate_wave(self):
        new_wave = Wave(self.height, self.width, self.angle, self.speed)
        self.waves.append(new_wave)


class Surfer:
    def __init__(self, surfbreak, init_x, init_y, paddle_speed,
                 speed_init=np.array([0, 0]),
                 surf_png_name='surfer.png',
                 wave_speed_const=10):
        """
        Class that defines a surfer and how the surfer behaves in the surfbreak
        """
        self.surfbreak = surfbreak
        self.x = init_x
        self.y = init_y
        self.speed = speed_init
        self.paddle_speed = paddle_speed
        self.surfer_png_name = surf_png_name
        self.wave_speed_const = wave_speed_const

    def step(self, actions):
        """
        Receives an action and moves the agent forward one step
        :param action: a dict with arrow keys (movement directions) as entries,
            and bool values for whether or not they are pressed
        :return: None
        """
        self.update_speed(actions)
        self.y = int(self.y + self.speed[0])
        self.x = int(self.x + self.speed[1])
        self.check_edges()

    def update_speed(self, actions):
        # Can eventually add turtle-tuck
        speed = np.array([0, 0])
        if actions[K_UP]:
            speed += np.array([-1, 0])
        elif actions[K_RIGHT]:  # Right
            speed += np.array([0, 1])
        elif actions[K_DOWN]:  # Down
            speed += np.array([1, 0])
        elif actions[K_LEFT]:  # Left
            speed += np.array([0, -1])

        # if (speed[0] != 0) or (speed[1] != 0):
        #     speed = speed / np.sqrt(np.square(speed[0]) + np.square(speed[1]))

        speed = speed * self.paddle_speed
        speed = speed + self.get_wave_speed()
        self.speed = speed

    # To-do
    def get_wave_speed(self):
        """
        Gets additive wave speed based on position on wave
        :return: speed
        """
        wave_speed = np.array([0.0, 0.0])
        try:
            wave_speed[0] = self.surfbreak.crashing[self.y - 1, self.x] - \
                            self.surfbreak.crashing[self.y + 1, self.x]
            wave_speed[1] = self.surfbreak.crashing[self.y, self.x - 1] - \
                            self.surfbreak.crashing[self.y, self.x + 1]
        except IndexError:
            pass

        if wave_speed[0] != 0 and wave_speed[1] != 0:
            print(wave_speed)
        # elif wave_speed[0] != 0:
        #     print(wave_speed)
        # elif wave_speed[1] != 0:
        #     print(wave_speed)

        return wave_speed * self.wave_speed_const

    def check_edges(self):
        if self.x < 0:
            self.x = 0
        elif self.x >= self.surfbreak.width:
            self.x = self.surfbreak.width - 2

        if self.y < 0:
            self.y = 0
        elif self.y >= self.surfbreak.height:
            self.y = self.surfbreak.height - 2


class Player(pygame.sprite.Sprite):
    def __init__(self, surfer, sprite_height=20, sprite_width=20,
                 img_path='/Users/mattkollada/PycharmProjects/swell/envs/resource/images/surfer.png'):
        self.surfer = surfer
        # self.key_handler = key.KeyStateHandler()
        self.sprite_height = sprite_height
        self.sprite_width = sprite_width

        self.surface = pygame.image.load(img_path)
        self.surface = pygame.transform.scale(self.surface,
                                              (self.sprite_height,
                                               self.sprite_width))

    def step(self, actions):
        self.surfer.step(actions)


if __name__ == '__main__':

    # Generate Break and Swell
    floor = partial(angled_sea_floor,
                    parallel_coef=0.03,
                    perp_coef=.25,
                    low_depth=50)

    swell = Swell(period=100, height=16, width=16, angle=2, speed=4)
    sb = SurfBreak(height=250,
                   width=200,
                   sea_floor_func=floor,
                   tide_init=1,
                   swell=swell)

    # Pygame implementation
    successes, failures = pygame.init()

    screen = pygame.display.set_mode((sb.width, sb.height))
    clock = pygame.time.Clock()
    FPS = 60

    sb_viz = SurfBreakViz(surfbreak=sb)

    screen.blit(sb_viz.surface, (0,0))
    pygame.display.flip()

    surfer = Surfer(surfbreak=sb, init_x=0, init_y=0, paddle_speed=5)
    player1 = Player(surfer=surfer)

    STEPALL = pygame.USEREVENT + 1
    pygame.time.set_timer(STEPALL, 100)

    running = True
    while running:
        clock.tick(60)
        # Did the user click the window close button?
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pressed_keys[K_ESCAPE]:
                running = False
            if event.type == STEPALL:
                sb_viz.step()
                player1.step(pressed_keys)
                screen.blit(sb_viz.surface, (0, 0))
                screen.blit(player1.surface,
                            ((player1.surfer.x - player1.sprite_width / 2),
                             (player1.surfer.y - player1.sprite_height / 2)))
                pygame.display.flip()

    pygame.quit()