# Dodać implementację agenta uczącego się
# DQN lub PPO
# Poczytać więcej o PPO i znaleźć jakieś przykłady wykorzystania

from pyboy import PyBoy
from random import randint
import numpy as np

smth = {
    (1,2,3): 2,

}
rew = (1,2,3)
if rew in smth:
    print(smth[rew])
else:
    print(0)