import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pyboy import PyBoy

actions = ['','a', 'b', 'left', 'right', 'up', 'down', 'start', 'select']

class PokemonRedEnv(gym.Env):

    def __init__(self, pyboy, debug=False):
        super().__init__()
        self.pyboy = pyboy
        self.debug = debug
        