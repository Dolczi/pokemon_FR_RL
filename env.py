import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pyboy import PyBoy

# Trzeba zaimportować jakoś game wrapper, może być ten domyślny, albo stworzony przez mnie
actions = ['','a', 'b', 'left', 'right', 'up', 'down', 'start', 'select']

matrix_shape = (16,20)
game_area_observation_space = spaces.Box(low=0, high=255, shape=matrix_shape, dtype=np.uint8)

class PokemonRedEnv(gym.Env):

    def __init__(self, pyboy, debug=False):
        super().__init__()
        self.pyboy = pyboy
        self.debug = debug
        
        if not self.debug:
            self.pyboy.set_emulation_speed(0)
        
        self.action_space = spaces.Discrete(len(actions))
        self.observation_space = game_area_observation_space
        self.pyboy.game_wrapper.start_game()

    def step(self, action):
        if action == 0:
            pass
        else:
            self.pyboy.button(actions[action])
        self.pyboy.tick(1)
        done = self.pyboy.game_wrapper.game_over

        self._calculate_fitness()
        reward=self._fitness-self._previous_fitness

        observation=self.pyboy.game_area()
        info = {}
        truncated = False

        return observation, reward, done, truncated, info
    
    def calculate_reward(self):
        # Tu obliczamy nagrodę
        pass

    def reset(self, **kwargs):
        self.pyboy.game_wrapper.reset_game()
        self._fitness=0
        self._previous_fitness=0

        observation=self.pyboy.game_area()
        info = {}
        return observation, info
    
    def render(self):
        pass

    def close(self):
        self.pyboy.stop()