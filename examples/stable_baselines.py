'''
NOTE:
    This file is to check that stable baselines can successfully train a model
    and then render that model using the custom environment.

    It is not a particularly successful RL agent
'''
import os
from swell.envs.custom_env import SurfSesh
from stable_baselines3 import PPO

env = SurfSesh(render=True)

model = PPO('MultiInputPolicy', env, verbose=2)

if os.path.isfile('models/test_model.zip'):
    model.load('models/test_model', env=env)
else:
    model.learn(100)
    model.save('models/test_model')

obs = env.reset()
for i in range(100):
    action, _state = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
        obs = env.reset()