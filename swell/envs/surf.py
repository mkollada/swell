import numpy as np
'''
To-do:
- ride-mode
    - check if turning works right
- duck dive
- crashing
    - what happens if wave crashes on you
- implement OpenAI gym env
- implement an agent in open 
- Refactor
    - main loop
'''


def flat_sea_floor(height, width, depth):
    return np.zeros((height, width)) + depth


def angled_sea_floor(height, width, parallel_coef, perp_coef, low_depth):
    floor = np.zeros((height, width))
    for x in range(width):
        for y in range(height):
            floor[y, x] = y * parallel_coef + x * perp_coef - low_depth

    return floor


class SurfBreak:
    def __init__(self, height, width, sea_floor_func, tide_init, swell,
                 water_friction_coef=1):
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
        if water_friction_coef > 1 or water_friction_coef < 0:
            raise ValueError('water_friction_coef should be between 0 and 1.')
        self.water_friction_coef = water_friction_coef

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
                    if (_y < self.height) and (_y >= 0):
                        self.active_water_level[_y, x] += wave.height
                        if self.base_water_level > self.sea_floor[_y, x]:
                            self.crashing[_y, x] = \
                                np.log(
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

