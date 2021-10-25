import numpy as np
import gym
from gym import spaces
from viz import WAVE_MAX_HEIGHT


class SurfSesh(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, surfer, max_timesteps=1000):
        super(SurfSesh, self).__init__()

        self.surfer = surfer
        self.max_timesteps = max_timesteps

        # For now observation space will be water height and whether or not the
        # wave is crashing at each point
        self.observation_space = spaces.Box(low=surfer.surfbreak.base_water_level,
                                            high=WAVE_MAX_HEIGHT,
                                            shape=(surfer.surfbreak.height,
                                                   surfer.surfbreak.width,
                                                   2))
        self.action_space = spaces.MultiBinary(n=len(surfer.action_space))

    def step(self, action):
        self.surfer.step(action)

        obs = 
        reward = self.surfer.stoke()
        done = self.surfer.surfbreak.counter > self.max_timesteps

        return obs, reward, done, {}

    def reset(self):
        # Reset the state of the environment to an initial state
        self.surfer.surfbreak.counter = 0
        self.surfer.y = int(np.random.rand() * self.surfer.surfbreak.height)
        self.surfer.x = int(np.random.rand() * self.surfer.surfbreak.width)

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        ...
