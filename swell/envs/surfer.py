import os
import numpy as np
from swell.envs.surf import SurfBreak


class Surfer:
    def __init__(self, surfbreak=None,
                 init_x=0,
                 init_y=0,
                 paddle_speed=1,
                 turn_speed=1,
                 speed_init=np.array([0, 0]),
                 wave_speed_const=10,
                 max_speed=10,
                 image_dir='/Users/mattkollada/PycharmProjects/swell/envs/resource/images/',
                 image_name_dict={0: 'paddling_surfer.png',
                                  1: 'standing_surfer.png'}):
        """
        Class that defines a surfer and how the surfer behaves in the surfbreak
        """
        if surfbreak is None:
            self.surfbreak = SurfBreak()
        else:
            self.surfbreak = surfbreak
        self.x = init_x
        self.y = init_y
        self.speed = speed_init
        self.paddle_speed = paddle_speed
        self.turn_speed = turn_speed
        self.wave_speed_const = wave_speed_const
        self.max_speed = max_speed

        self.action_space = ['up', 'down', 'left', 'right', 'change_mode']

        # 0 for paddle mode, 1 for standing up
        self.mode = 0

        # Surfer image related info. Should move this out of surfer eventually
        self.image_dir = image_dir
        self.image_name_dict = image_name_dict
        self.current_image_path = self.get_image_path()

    def get_image_path(self):
        return os.path.join(self.image_dir, self.image_name_dict[self.mode])

    def step(self, actions):
        """
        Receives an action and moves the agent forward one step
        :param actions: a dict with action types as entries,
            and bool values for whether or not they are pressed
        :return: None
        Potential surfer actions:
        - paddle mode
           - paddle
               - up, down, left, right
           - stand-up
           - duck-dive
        - ride mode
           - turn
               - right, left
           - stand-up
        """
        assert set(actions.keys()) == set(self.action_space)
        if actions['change_mode']:
            self.mode = 1 - self.mode
            self.current_image_path = self.get_image_path()
        self.update_speed(actions)
        self.y = int(self.y + self.speed[0])
        self.x = int(self.x + self.speed[1])
        self.check_edges()

    def apply_water_friction(self, func=None):
        if func is not None:
            self.speed = func(self.speed)
        else:
            self.speed = self.speed * self.surfbreak.water_friction_coef

    def update_speed(self, actions):
        # Can eventually add turtle-tuck
        if self.mode == 0:
            delta_speed = self.paddle(up=actions['up'],
                                      down=actions['down'],
                                      left=actions['left'],
                                      right=actions['right'])
            self.speed = self.speed + delta_speed
        elif self.mode == 1:
            # right = turn clockwise, left = turn counterclockwise
            if actions['right'] or actions['left']:
                self.speed = self.turn(self.speed,
                                       right=actions['right'],
                                       left=actions['left'])

        self.speed = self.speed + self.get_wave_speed()
        self.apply_water_friction()

    def paddle(self, up=False, down=False, left=False, right=False):
        paddle = np.array([0, 0])
        if up:
            paddle += np.array([-1, 0])
        elif right:
            paddle += np.array([0, 1])
        elif down:
            paddle += np.array([1, 0])
        elif left:
            paddle += np.array([0, -1])

        return paddle * self.paddle_speed

    def turn(self, speed, right=False, left=False):

        direction = 0
        if right:
            direction += 1
        elif left:
            direction += -1

        const1 = np.square(speed[0]) + np.square(speed[1])
        const2 = np.arctan(
            direction * self.turn_speed + np.tan(speed[0] / speed[1])
        )
        const3 = np.sqrt(const1 / (np.square(const2) + 1))

        speed[0] = const2 * const3
        speed[1] = const3

        return speed

    def get_wave_speed(self):
        """
        Gets additive wave speed based on position on wave
        :return: speed
        """
        wave_speed = np.array([0.0, 0.0])
        if self.y == 0 or self.y == (self.surfbreak.height - 1):
            wave_speed[0] = 0
        else:
            wave_speed[0] = self.surfbreak.crashing[self.y - 1, self.x] - \
                            self.surfbreak.crashing[self.y + 1, self.x]
        if self.x == 0 or self.x == (self.surfbreak.width - 1):
            wave_speed[1] = 0
        else:
            wave_speed[1] = self.surfbreak.crashing[self.y, self.x - 1] - \
                            self.surfbreak.crashing[self.y, self.x + 1]

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

    def get_stoke(self):
        '''
        This function calculates the per step reward for a given surfer. This
        function can be overidden when extending the surfer class.

        :return: This simple reward function returns either zero, if the surfer
        is paddling, or the magnitude of the speed vector of the surfer, if the
        surfer is standing up, at each step.
        '''

        return np.sqrt(np.sum(np.square(self.speed))) * self.mode
