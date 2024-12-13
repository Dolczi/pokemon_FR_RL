from env_multi_input import PokemonRedEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.env_checker import check_env

rom_path = 'd:/Pokemon/pokemonRed.gb'
init_state_path = 'd:/Pokemon/has_pokedex_nballs.state'
render_mode = 'SDL2'
ep_length = 2048 * 8

#env = PokemonRedEnv(rom_path, init_state_path, render_mode)
#check_env(env)


def make_env(rank):
    def _init():
        env = PokemonRedEnv(rom_path, init_state_path, render_mode)
        env.reset(seed=rank)
        return env
    return _init

if __name__=='__main__':
    num_parallell = 4
    env = SubprocVecEnv([make_env(i) for i in range(num_parallell)])

    model = PPO('MultiInputPolicy', env, verbose=1, n_steps=ep_length, batch_size=512, n_epochs=8)
    model.learn(total_timesteps=ep_length*num_parallell*100)
    model.save('ppo_pokemon')
