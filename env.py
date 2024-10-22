import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pyboy import PyBoy

actions = ['','a', 'b', 'left', 'right', 'up', 'down', 'start', 'select']

class PokemonRedEnv(gym.Env):

    def __init__(self, pyboy, debug=False):
        pass

    def step(self, action):
        pass

    def reset(self, **kwargs):
        pass

    def close(self):
        pass