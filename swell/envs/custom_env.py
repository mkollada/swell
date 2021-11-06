import numpy as np
import gym
from gym import spaces
from swell.envs.viz import WAVE_MAX_HEIGHT, SurfBreakViz, SurferViz
from swell.envs.surfer import Surfer
import pygame


class SurfSesh(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, surfer=None, max_timesteps=1000, render=False, fps=5):
        super(SurfSesh, self).__init__()

        if surfer is None:
            self.surfer = Surfer()
        else:
            self.surfer = surfer
        self.max_timesteps = max_timesteps

        # For now observation space will be water height, whether or not the
        # wave is crashing at each point, position, and speed
        self.observation_space = spaces.Dict({
            'active_water_level': spaces.Box(
                low=self.surfer.surfbreak.base_water_level,
                high=WAVE_MAX_HEIGHT,
                shape=(self.surfer.surfbreak.height,
                       self.surfer.surfbreak.width)
            ),
            'crashing': spaces.Box(low=0,
                                   high=WAVE_MAX_HEIGHT,
                                   shape=(self.surfer.surfbreak.height,
                                          self.surfer.surfbreak.width)),
            'position': spaces.Box(low=np.array([0, 0]),
                                   high=np.array([
                                       self.surfer.surfbreak.height,
                                       self.surfer.surfbreak.width
                                   ])),
            'speed': spaces.Box(low=-1 * self.surfer.max_speed,
                                high=self.surfer.max_speed,
                                shape=(2,))
        })

        self.action_space = spaces.MultiBinary(n=len(self.surfer.action_space))

        self.fps = fps

        self.render_ = render
        if self.render_:
            self.sb_viz = SurfBreakViz(self.surfer.surfbreak)
            self.surfer_viz = SurferViz(self.surfer)
            successes, failures = pygame.init()
            self.screen = pygame.display.set_mode((self.sb_viz.surfbreak.width,
                                                   self.sb_viz.surfbreak.height))
            self.my_font = pygame.font.SysFont("monospace", 16)
            score_text = self.my_font.render("Stoke: " + str(self.surfer_viz.surfer.total_stoke),
                                        1, (0, 0, 0))
            self.screen.blit(score_text, (5, 5))

            self.clock = pygame.time.Clock()

    def step(self, actions):
        assert len(actions) == len(self.surfer.action_space)
        actions = dict(zip(self.surfer.action_space, actions))
        if self.render_:
            self.sb_viz.step()
            self.surfer_viz.step(actions)
        else:
            self.surfer.surfbreak.step()
            self.surfer.step(actions)

        obs = {
            'active_water_level': self.surfer.surfbreak.active_water_level,
            'crashing': self.surfer.surfbreak.crashing,
            'position': [self.surfer.y, self.surfer.x],
            'speed': self.surfer.speed
        }
        reward = self.surfer.get_stoke()
        done = self.surfer.surfbreak.counter > self.max_timesteps

        return obs, reward, done, {}

    def reset(self):
        # Reset the state of the environment to an initial state
        self.surfer.surfbreak.counter = 0
        self.surfer.y = int(np.random.rand() * self.surfer.surfbreak.height)
        self.surfer.x = int(np.random.rand() * self.surfer.surfbreak.width)
        self.surfer.speed[0] = 0
        self.surfer.speed[1] = 0

        return {
            'active_water_level': self.surfer.surfbreak.active_water_level,
            'crashing': self.surfer.surfbreak.crashing,
            'position': [self.surfer.y, self.surfer.x],
            'speed': self.surfer.speed
        }

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        # TO-DO
        assert self.render_

        self.clock.tick(self.fps)

        self.screen.blit(self.sb_viz.surface, (0, 0))
        self.screen.blit(self.surfer_viz.surface,
                         ((self.surfer.x - self.surfer_viz.sprite_width / 2),
                          (self.surfer.y - self.surfer_viz.sprite_height / 2)))
        score_text = self.my_font.render("Stoke: " + str(self.surfer_viz.surfer.total_stoke),
                                    1, (0, 0, 0))
        self.screen.blit(score_text, (5, 5))
        pygame.display.flip()

    def close(self):
        if self.render_:
            pygame.quit()
