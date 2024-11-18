# Dodać implementację agenta uczącego się
# DQN lub PPO
# Poczytać więcej o PPO i znaleźć jakieś przykłady wykorzystania

from pyboy import PyBoy
from random import randint

pyboy = PyBoy('d:/Pokemon/pokemonRed.gb')
pyboy.game_wrapper.start_game()
pyboy.set_emulation_speed(0)

valid_keys = ['','a','b','up','down','left','right','start']
while True:
    pyboy.tick(10000)
    action = valid_keys[randint(0,len(valid_keys)-1)]
    if action == '':
        pass
    else:
        pyboy.button(action)
pyboy.stop()