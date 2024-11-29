from env_v2 import PokemonRedEnv
import numpy as np

rom_path = 'd:/Pokemon/pokemonRed.gb'
init_state_path = 'd:/Pokemon/has_pokedex_nballs.state'
freq = 24
env = PokemonRedEnv(freq, rom_path, init_state_path)
states = []
rewards = []
try:
    i = 0
    while True:
        #random_action = np.random.choice(list(range(len(env.actions))),size=1)[0]
        input_action = input()
        if input_action != '':
            input_action = int(input_action)
            if input_action in env.action_space:
                observation, reward, terminated, truncated, _ = env.step(input_action)

                states.append(observation)
                rewards.append(reward)
                print(env.agent_stats[i])
                i += 1

finally:
    env.close()