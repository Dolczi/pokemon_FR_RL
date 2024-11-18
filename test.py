from env_v2 import PokemonRedEnv
import numpy as np

rom_path = 'd:/Pokemon/pokemonRed.gb'
init_state_path = 'd:/Pokemon/has_pokedex_nballs.state'
freq = 24
env = PokemonRedEnv(freq, rom_path, init_state_path)
try:
    for i in range(3000):
        random_action = np.random.choice(list(range(len(env.actions))),size=1)[0]
        observation, reward, terminated, truncated, _ = env.step(random_action)
finally:
    env.close()