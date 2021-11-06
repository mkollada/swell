'''
NOTE:
    This file is to check that stable baselines can successfully train a model
    and then render that model using the custom environment.

    It is not a particularly successful RL agent
'''
import os
from swell.envs.custom_env import SurfSesh
from stable_baselines3 import PPO
from stable_baselines3.common.policies import MultiInputActorCriticPolicy
from stable_baselines.common.schedules import LinearSchedule, ConstantSchedule
# from stable_baselines3.common.torch_layers import CombinedExtractor

env = SurfSesh(render=True)
schedule = ConstantSchedule(value=1e-3)
model = PPO(
    # policy=MultiInputActorCriticPolicy(
    #     observation_space=env.observation_space,
    #     action_space=env.action_space,
    #     lr_schedule=ConstantSchedule
    # ),
    policy='MultiInputPolicy',
    env=env,
    verbose=10,
    # n_steps=10000
    )

if os.path.isfile('models/test_model.zip'):
    model.load('models/test_model', env=env)
else:
    model.learn(1000)
    model.save('models/test_model')

obs = env.reset()
for i in range(100):
    action, _state = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
        obs = env.reset()
