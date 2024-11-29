from env_v2 import PokemonRedEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

rom_path = 'd:/Pokemon/pokemonRed.gb'
init_state_path = 'd:/Pokemon/has_pokedex_nballs.state'
freq = 24
ep_length = 2048 * 10

if __name__=='__main__':
    num_parallell = 6
    env = SubprocVecEnv([PokemonRedEnv(freq, rom_path, init_state_path) for _ in range(num_parallell)])

    model = PPO('CnnPolicy', env, verbose=1)
    model.learn(total_timesteps=(ep_length)*num_parallell*100)
    model.save("ppo_cartpole")