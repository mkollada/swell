from gym.envs.registration import register

register(
    id='swell-v0',
    entry_point='swell.envs:SurfSesh',
)