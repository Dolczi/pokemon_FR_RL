from gymnasium import Env, spaces
import numpy as np
from pyboy import PyBoy
from utils import calculate_reward, get_agent_stats, update_explored, get_observation, update_max_level

class PokemonRedEnv(Env):

    def __init__(self, game_path, init_state, render_mode):
        super().__init__()
        # Config - zmienne konfiguracyjne
        self.frame_stack = 3
        self.action_frequency = 24
        self.render_mode = render_mode
        self.init_state = init_state

        # Action space - lista dostępnych dla agenta akcji
        self.actions = ['a', 'b', 'left', 'right', 'up', 'down']
        self.action_space = spaces.Discrete(len(self.actions))

        # Observation space - sposób reprezentacji obserwacji dla agenta
        self.output_shape = (36,40,self.frame_stack)
        self.observation_space = spaces.Dict(
            {
                'screen': spaces.Box(low=0, high=255, shape=self.output_shape, dtype=np.uint8),
                'location': spaces.Box(low=0, high=255, shape=(3,), dtype=np.int32),
                'hp': spaces.Box(low=0, high=1, shape=(1,), dtype=np.float64),
                'level': spaces.Box(low=5, high=255, shape=(1,), dtype=np.int32),
                'badges': spaces.Box(low=0, high=8, shape=(1,)), 
                'recent_actions': spaces.MultiDiscrete([len(self.actions)]*self.frame_stack),
                'is_in_battle': spaces.Box(low=0, high=1, shape=(1,))
            }
        )

        # Initialize Pyboy object
        self.pyboy = PyBoy(
                gamerom=game_path,
                window=self.render_mode,
            )

        if render_mode == 'headless':
            self.pyboy.set_emulation_speed(0)
        else:
            self.pyboy.set_emulation_speed(6)
        self.max_steps = 2048 * 8

    def reset(self, seed=0):
        with open(self.init_state, 'rb') as f:
            self.pyboy.load_state(f)

        self.total_reward = 0
        self.agent_stats = []
        self.agent_explored = {}
        self.recent_screens = np.zeros(self.output_shape, dtype=np.uint8)
        self.recent_actions = np.zeros((self.frame_stack,), dtype=np.uint8)
        self.step_count = 0
        
        self.agent_current_stats = get_agent_stats(self.pyboy)
        self.agent_stats.append(self.agent_current_stats)
        self.agent_max_level = 6
        self.agent_explored = update_explored(self.agent_explored, self.agent_current_stats)
        observation = self.render()

        return observation, {}
    
    def step(self, action):
        # take an action
        self.pyboy.button(self.actions[action], 8)
        self.pyboy.tick(24)

        self.agent_current_stats = get_agent_stats(self.pyboy)

        self.recent_actions = np.roll(self.recent_actions, 1)
        self.recent_actions[0] = action

        observation = self.render()

        reward = calculate_reward(self.agent_explored, self.agent_current_stats, self.agent_stats, self.step_count, self.agent_max_level)
        self.total_reward += reward
        
        self.agent_stats.append(self.agent_current_stats)
        self.agent_explored = update_explored(self.agent_explored, self.agent_current_stats)
        self.agent_max_level = update_max_level(self.agent_max_level, self.agent_current_stats)
        self.step_count += 1

        terminated = False #self.agent_current_stats['badges'] > 0
        truncated = self.step_count >= self.max_steps

        return observation, reward, terminated, truncated, {}

    def render(self):
        observation, self.recent_screens = get_observation(self.pyboy, self.recent_screens, self.recent_actions, self.output_shape)
        return observation

    def close(self):
        self.pyboy.stop()