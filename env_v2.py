from gymnasium import Env, spaces
import numpy as np
from pyboy import PyBoy
from utils import calculate_reward, get_agent_stats, update_explored

class PokemonRedEnv(Env):

    def __init__(self, action_frequency, game_path, start_state):
        super().__init__()
        # Action space
        self.actions =  ['a', 'b', 'left', 'right', 'up', 'down', 'start']
        self.action_space = spaces.Discrete(len(self.actions))

        # Observation space
        self.output_shape_full = (144,160,4)
        self.output_shape_simplified = (18,20)
        self.observation_space = spaces.Box(low=0, high=255, shape=self.output_shape_simplified, dtype=np.uint8)

        # Action frequency
        self.action_frequency = action_frequency

        # Initialize Pyboy object
        self.pyboy = PyBoy(
                gamerom=game_path,
                window='SDL2',
            )

        # Start game from given state
        self.start_state = start_state
        with open(self.start_state, "rb") as f:
            self.pyboy.load_state(f)

        # Initialize the reward
        self.agent_current_stats = get_agent_stats(self.pyboy)
        self.agent_stats = []
        self.agent_explored = []
        self.total_reward = 0
        self.max_steps = 2048 * 10
        self.steps_count = 0

    def step(self, action):
        # take an action
        self.pyboy.button(self.actions[action], 8)
        self.pyboy.tick(24)

        observation = self.render()
        reward = calculate_reward(self.pyboy, self.agent_explored, self.agent_current_stats, self.agent_stats)
        self.total_reward += reward
        self.agent_current_stats = get_agent_stats(self.pyboy)
        self.agent_stats.append(self.agent_current_stats)
        self.agent_explored = update_explored(self.agent_explored, self.agent_current_stats)
        self.steps_count += 1

        terminated = self.agent_current_stats['badges'] > 0
        truncated = self.steps_count > self.max_steps

        return observation, reward, terminated, truncated, {}

    def reset(self):
        with open(self.start_state, "rb") as f:
            self.pyboy.load_state(f)

        self.total_reward = 0
        self.agent_stats = []
        self.agent_explored = []
        observation = self.render()
        self.agent_current_stats = get_agent_stats(self.pyboy)

        return observation, {}

    def render(self):
        # Generate observation
        # observation_full = self.pyboy.screen.ndarray
        observation_simplified = self.pyboy.game_area()
        return observation_simplified

    def close(self):
        self.pyboy.stop()